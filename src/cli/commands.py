"""CLI commands for the stock library."""

import click
from services.database_service import DatabaseService
from services.api_service import ApiService
from services.historical_data_service import HistoricalDataService
from services.sina_finance_service import SinaFinanceService
from lib.config import Config
from lib.logging import setup_logging, get_logger
import json
import concurrent.futures
from typing import Dict, Any


@click.group()
@click.option('--log-level', default='WARNING', help='Logging level')
@click.option('--log-file', default=None, help='Log file path')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
def cli(log_level, log_file, debug):
    """Stock data management CLI."""
    if debug:
        log_level = 'INFO'  # Show INFO and DEBUG messages when debug flag is used

    setup_logging(log_level, log_file)


def _setup_database_and_table(db_path: str, hist_service: HistoricalDataService) -> bool:
    """Helper function to set up database and ensure historical data table exists."""
    db_service = DatabaseService(db_path)
    if not db_service.database_exists():
        click.echo(f"Initializing database at {db_path}...")
        if not db_service.initialize_database():
            click.echo("Database initialization failed", err=True)
            return False

    if not hist_service.create_historical_data_table():
        click.echo("Failed to create historical data table", err=True)
        return False

    return True


def _process_single_stock(hist_service: HistoricalDataService, stock_code: str, force_full_sync: bool) -> Dict[str, Any]:
    """Process a single stock for historical data sync.

    Args:
        hist_service: Historical data service instance
        stock_code: Stock code to process
        force_full_sync: Whether to force full sync

    Returns:
        Dictionary with processing results
    """
    logger = get_logger(__name__)

    try:
        if force_full_sync:
            # Force full sync - fetch all historical data
            logger.info(f"Force full sync for {stock_code}")
            count = hist_service.fetch_and_store_historical_data(stock_code)
            action = "full sync"
        else:
            # Smart sync - check what data we need
            has_data = hist_service.get_latest_date_for_stock(stock_code) is not None

            if not has_data:
                # No data exists - fetch all historical data
                logger.info(f"No historical data found for {stock_code}, fetching all data")
                count = hist_service.fetch_and_store_historical_data(stock_code)
                action = "initial sync"
            else:
                # Check if data is fresh, fetch only missing data
                logger.info(f"Checking data freshness for {stock_code}")
                is_fresh, missing_start_date = hist_service.check_data_freshness(stock_code)

                if is_fresh:
                    logger.info(f"Historical data for {stock_code} is already up-to-date")
                    count = 0
                    action = "already up-to-date"
                else:
                    logger.info(f"Fetching missing data for {stock_code} from {missing_start_date}")
                    count = hist_service.fetch_and_store_historical_data(stock_code, missing_start_date)
                    action = "updated"

        return {'stock_code': stock_code, 'count': count, 'action': action, 'success': True}

    except Exception as e:
        logger.error(f"Failed to sync {stock_code}: {e}")
        return {'stock_code': stock_code, 'count': 0, 'action': 'failed', 'success': False, 'error': str(e)}


@cli.command()
@click.option('--db-path', default=None, help='Database file path')
@click.option('--default-db', is_flag=True, help='Use default database path')
@click.option('--stock-codes', help='Comma-separated list of specific stock codes to sync (optional)')
@click.option('--all-stocks', is_flag=True, help='Sync historical data for all stocks in database')
@click.option('--limit', default=None, type=int, help='Limit number of stocks to process')
@click.option('--force-full-sync', is_flag=True, help='Force full sync for all stocks (ignore existing data)')
@click.option('--max-threads', default=10, type=int, help='Maximum number of threads for parallel processing (default: 10)')
def sync_historical(db_path, default_db, stock_codes, all_stocks, limit, force_full_sync, max_threads):
    """Sync historical data for stocks - smart sync that fetches missing data only."""
    if default_db:
        db_path = Config.get_database_path()

    if not db_path:
        click.echo("Error: Database path must be specified or --default-db flag used", err=True)
        return 1

    logger = get_logger(__name__)

    # Initialize services
    hist_service = HistoricalDataService(db_path)
    db_service = DatabaseService(db_path)

    # Ensure database exists
    if not db_service.database_exists():
        click.echo(f"Database does not exist at {db_path}", err=True)
        return 1

    # Get list of stock codes to process
    if stock_codes:
        codes_to_process = [code.strip() for code in stock_codes.split(',')]
        click.echo(f"Processing {len(codes_to_process)} specified stocks: {', '.join(codes_to_process)}")
    elif all_stocks:
        stocks = db_service.get_all_stocks()
        all_codes = [stock.code for stock in stocks]

        # Get codes that already have historical data
        existing_codes = set(hist_service.get_stocks_with_historical_data())

        # Prioritize codes without historical data first
        missing_codes = [code for code in all_codes if code not in existing_codes]
        existing_codes_list = [code for code in all_codes if code in existing_codes]

        # Combine lists: missing codes first, then existing codes
        codes_to_process = missing_codes + existing_codes_list

        if limit:
            codes_to_process = codes_to_process[:limit]

        click.echo(f"Processing all {len(codes_to_process)} stocks from database")
        click.echo(f"  - {len(missing_codes)} stocks without historical data (prioritized first)")
        click.echo(f"  - {len(existing_codes_list)} stocks with existing historical data")
    else:
        click.echo("Error: Must specify --stock-codes or --all-stocks", err=True)
        return 1

    if not codes_to_process:
        click.echo("No stocks to process", err=True)
        return 1

    # Ensure database is initialized
    if not _setup_database_and_table(db_path, hist_service):
        return 1

    click.echo(f"Starting smart sync for {len(codes_to_process)} stocks using {max_threads} threads...")
    results = {}

    # Process stocks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit all tasks
        future_to_stock = {
            executor.submit(_process_single_stock, hist_service, stock_code, force_full_sync): stock_code
            for stock_code in codes_to_process
        }

        # Process results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(future_to_stock):
            stock_code = future_to_stock[future]
            completed += 1
            click.echo(f"[{completed}/{len(codes_to_process)}] Completed {stock_code}")

            try:
                result = future.result()
                results[stock_code] = result

                if result['success']:
                    if result['count'] > 0:
                        click.echo(f"  [OK] {result['action']}: {result['count']} records stored")
                    else:
                        click.echo(f"  [OK] {result['action']}")
                else:
                    click.echo(f"  [FAIL] Failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                logger.error(f"Unexpected error processing {stock_code}: {e}")
                results[stock_code] = {'count': 0, 'action': 'failed'}
                click.echo(f"  [ERROR] Unexpected error: {e}")

    # Generate summary
    total_processed = len(results)
    successful = sum(1 for r in results.values() if r['count'] > 0 or r['action'] == 'already up-to-date')
    total_records = sum(r['count'] for r in results.values())
    failed = sum(1 for r in results.values() if r['action'] == 'failed')

    click.echo("\n" + "="*60)
    click.echo("SYNC SUMMARY")
    click.echo("="*60)
    click.echo(f"Total stocks processed: {total_processed}")
    click.echo(f"Successful: {successful}")
    click.echo(f"Failed: {failed}")
    click.echo(f"Total records stored: {total_records}")

    if failed > 0:
        failed_stocks = [code for code, result in results.items() if result['action'] == 'failed']
        click.echo(f"Failed stocks: {', '.join(failed_stocks)}")

    return 0 if failed == 0 else 1


@cli.command()
@click.option('--db-path', default=None, help='Database file path')
@click.option('--default', is_flag=True, help='Use default database path')
def init_db(db_path, default):
    """Initialize the DuckDB database."""
    if default:
        db_path = Config.get_database_path()

    if not db_path:
        click.echo("Error: Database path must be specified or --default flag used", err=True)
        return 1

    logger = get_logger(__name__)
    logger.debug(f"Initializing database at path: {db_path}")

    service = DatabaseService(db_path)

    if service.database_exists():
        logger.debug("Database already exists, skipping initialization")
        click.echo(f"Database already exists at {db_path}")
        return 0

    logger.debug("Database does not exist, proceeding with initialization")
    click.echo(f"Initializing database at {db_path}...")
    if service.initialize_database():
        logger.debug("Database initialization completed successfully")
        click.echo(f"Database initialized successfully at {db_path}")
        return 0
    else:
        logger.error("Database initialization failed")
        click.echo("Database initialization failed", err=True)
        return 1


@cli.command()
@click.option('--db-path', default=None, help='Database file path')
@click.option('--default-db', is_flag=True, help='Use default database path')
@click.option('--validate-only', is_flag=True, help='Only validate data, do not store')
def fetch_stocks(db_path, default_db, validate_only):
    """Fetch stock information from API and optionally store in database."""
    if default_db:
        db_path = Config.get_database_path()

    if not db_path and not validate_only:
        click.echo("Error: Database path must be specified or --default-db flag used", err=True)
        return 1

    # Fetch stocks from API
    api_service = ApiService()
    logger = get_logger(__name__)
    logger.debug("Starting stock fetch operation")

    click.echo("Fetching stock information from API...")
    try:
        stocks = api_service.fetch_stock_info()
        click.echo(f"Successfully fetched {len(stocks)} stocks")
        logger.debug(f"API fetch completed with {len(stocks)} stocks")
    except Exception as e:
        logger.error(f"Stock fetch failed: {e}", exc_info=True)
        click.echo(f"Failed to fetch stocks: {e}", err=True)
        return 1

    # Validate data
    logger.debug("Starting data validation")
    if not api_service.validate_stock_data(stocks):
        logger.error("Data validation failed")
        click.echo("Stock data validation failed", err=True)
        return 1
    logger.debug("Data validation passed")

    # Output results
    if validate_only:
        logger.debug("Validate-only mode: outputting JSON to stdout")
        # Print JSON to stdout
        stock_dicts = [stock.to_dict() for stock in stocks]
        click.echo(json.dumps(stock_dicts, indent=2, ensure_ascii=False))
        return 0

    # Store in database
    logger.debug(f"Preparing to store stocks in database: {db_path}")
    db_service = DatabaseService(db_path)
    if not db_service.database_exists():
        logger.debug("Database does not exist, initializing...")
        click.echo(f"Initializing database at {db_path}...")
        if not db_service.initialize_database():
            logger.error("Database initialization failed")
            click.echo("Database initialization failed", err=True)
            return 1

    click.echo(f"Storing stocks in database at {db_path}...")
    inserted = db_service.insert_stocks(stocks)
    logger.debug(f"Database insertion completed: {inserted}/{len(stocks)} stocks stored")
    click.echo(f"Successfully stored {inserted} stocks in database")
    return 0


@cli.command()
@click.option('--db-path', default=None, help='Database file path')
@click.option('--default-db', is_flag=True, help='Use default database path')
@click.option('--limit', default=None, type=int, help='Limit number of stocks to return')
def list_stocks(db_path, default_db, limit):
    """List stocks from the database."""
    if default_db:
        db_path = Config.get_database_path()

    if not db_path:
        click.echo("Error: Database path must be specified or --default-db flag used", err=True)
        return 1

    db_service = DatabaseService(db_path)
    if not db_service.database_exists():
        click.echo(f"Database does not exist at {db_path}", err=True)
        return 1

    try:
        stocks = db_service.get_all_stocks()
        if limit:
            stocks = stocks[:limit]

        # Output as JSON
        stock_dicts = [stock.to_dict() for stock in stocks]
        click.echo(json.dumps(stock_dicts, indent=2, ensure_ascii=False))
        return 0

    except Exception as e:
        click.echo(f"Failed to list stocks: {e}", err=True)
        return 1


@cli.command()
@click.option('--db-path', default=None, help='Database file path')
@click.option('--default-db', is_flag=True, help='Use default database path')
def list_tables(db_path, default_db):
    """List all tables in the database."""
    if default_db:
        db_path = Config.get_database_path()

    if not db_path:
        click.echo("Error: Database path must be specified or --default-db flag used", err=True)
        return 1

    db_service = DatabaseService(db_path)
    if not db_service.database_exists():
        click.echo(f"Database does not exist at {db_path}", err=True)
        return 1

    try:
        tables = db_service.list_tables()

        # Output as JSON array
        click.echo(json.dumps(tables, indent=2, ensure_ascii=False))
        return 0

    except Exception as e:
        click.echo(f"Failed to list tables: {e}", err=True)
        return 1


@cli.command()
@click.option('--db-path', default=None, help='Database file path')
@click.option('--default-db', is_flag=True, help='Use default database path')
@click.option('--stock-code', required=True, help='Stock code to get historical data for')
@click.option('--start-date', default=None, help='Start date filter in YYYY-MM-DD format')
@click.option('--end-date', default=None, help='End date filter in YYYY-MM-DD format')
@click.option('--limit', default=None, type=int, help='Limit number of records to return')
@click.option('--format', default='json', type=click.Choice(['json', 'table']), help='Output format')
def get_historical(db_path, default_db, stock_code, start_date, end_date, limit, format):
    """Get historical data for a stock from the database."""
    if default_db:
        db_path = Config.get_database_path()

    if not db_path:
        click.echo("Error: Database path must be specified or --default-db flag used", err=True)
        return 1

    logger = get_logger(__name__)

    # Initialize historical data service
    hist_service = HistoricalDataService(db_path)

    # Ensure database exists
    db_service = DatabaseService(db_path)
    if not db_service.database_exists():
        click.echo(f"Database does not exist at {db_path}", err=True)
        return 1

    # Ensure historical data table exists
    if not hist_service.create_historical_data_table():
        click.echo("Failed to create historical data table", err=True)
        return 1

    try:
        df = hist_service.get_historical_data(stock_code, start_date, end_date, limit)

        if df is None or df.empty:
            click.echo(f"No historical data found for {stock_code}")
            return 0

        if format == 'json':
            # Convert DataFrame to JSON
            records = df.to_dict('records')
            click.echo(json.dumps(records, indent=2, ensure_ascii=False, default=str))
        else:  # table format
            # Simple table output
            click.echo(f"Historical data for {stock_code} ({len(df)} records):")
            click.echo("-" * 80)
            for _, row in df.head(10).iterrows():  # Show first 10 rows
                click.echo(f"{row['date']} | {row.get('close_price', 'N/A')} | {row.get('volume', 'N/A')}")
            if len(df) > 10:
                click.echo(f"... and {len(df) - 10} more records")

        return 0

    except Exception as e:
        logger.error(f"Failed to get historical data: {e}", exc_info=True)
        click.echo(f"Failed to get historical data: {e}", err=True)
        return 1


@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, type=int, help='Limit number of results to return')
def search(query, limit):
    """Search for stocks by code, name, or pinyin."""
    logger = get_logger(__name__)

    try:
        sina_service = SinaFinanceService()
        click.echo(f"Searching for stocks matching '{query}'...")

        results = sina_service.search_stocks(query)

        if not results:
            click.echo("No stocks found matching the query.")
            return 1

        # Limit results
        results = results[:limit]

        # Output in table format like rains
        for result in results:
            # Using 'full_code' and 'name' from the search results like rains
            code = result.get('full_code', '')
            name = result.get('name', '')
            click.echo(f"{code:<8}\t{name}")

        # Don't output count like rains does

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        click.echo(f"Search failed: {e}", err=True)
        return 1


@cli.command()
@click.argument('symbol')
@click.option('--no-check', '-n', is_flag=True, help='Do not validate symbol format')
@click.option('--realtime', '-r', is_flag=True, help='Enable real-time quote updates')
@click.option('--multiline', '-m', is_flag=True, help='Multi-line display for real-time quotes (single symbol only)')
def quote(symbol, no_check, realtime, multiline):
    """Get real-time quote for a stock."""
    logger = get_logger(__name__)

    try:
        sina_service = SinaFinanceService()

        # Handle multiple symbols (comma-separated) like rains does
        symbols = [s.strip() for s in symbol.split(',')]

        if realtime:
            # Real-time functionality not implemented yet - match rains behavior
            click.echo("Real-time quote functionality not yet implemented")
            return 1
        else:
            # Get quotes for all symbols like rains does - call quotes() plural method
            if no_check:
                # Use symbols as-is without validation
                symbols_list = symbols
            else:
                # Validate symbols like rains does
                symbols_list = []
                for sym in symbols:
                    # For now, just add them - SinaFinanceService handles validation internally
                    symbols_list.append(sym)

            if not symbols_list:
                click.echo("No valid symbols to query")
                return 1

            # Join symbols with comma like rains does
            symbols_str = ','.join(symbols_list)

            # Call quotes method (plural) like rains does
            quotes = sina_service.get_quotes(symbols_str)
            if quotes:
                for quote in quotes:
                    write_quote_formatted(quote)
            else:
                click.echo("No quote data found")
                return 1

        return 0

    except Exception as e:
        logger.error(f"Quote fetch failed: {e}", exc_info=True)
        click.echo(f"Quote fetch failed: {e}", err=True)
        return 1


@cli.command()
@click.argument('symbol')
@click.option('--all', '-a', is_flag=True, help='Include all available information')
@click.option('--financials', '-f', is_flag=True, help='Include financial data')
@click.option('--structure', '-s', is_flag=True, help='Include shareholder structure')
@click.option('--dividends', is_flag=True, help='Include dividend history')
@click.option('--presses', '-p', is_flag=True, help='Include company announcements')
def info(symbol, all, financials, structure, dividends, presses):
    """Get detailed information about a stock."""
    logger = get_logger(__name__)

    try:
        sina_service = SinaFinanceService()
        click.echo(f"Fetching information for {symbol}...")

        # Get profile like rains does
        profile = sina_service.get_profile(symbol)
        if profile:
            # Format output exactly like rains - all fields shown unconditionally
            click.echo(click.style("基本信息", bold=True))
            click.echo(f"证券代码\t{symbol}")
            click.echo(f"简称历史\t{profile.used_name or ''}")
            click.echo(f"公司名称\t{profile.name}")
            click.echo(f"上市日期\t{profile.listing_date or ''}")
            click.echo(f"发行价格\t{profile.listing_price:.2f}")
            click.echo(f"行业分类\t{profile.industry or ''}")
            click.echo(f"主营业务\t{profile.business or ''}")
            click.echo(f"办公地址\t{profile.address or ''}")
            click.echo(click.style(f"公司网址\t{profile.website or ''}", underline=True))
            # Get price from quote like rains does
            quote_data = sina_service.get_quote(symbol)
            price = quote_data.price if quote_data else None
            click.echo(f"当前价格\t{price:.2f}" if price else "当前价格\t")
            click.echo(f"市净率PB\t{profile.pb_ratio:.2f}" if profile.pb_ratio else "市净率PB\t")
            click.echo(f"市盈率TTM\t{profile.pe_ratio:.2f}" if profile.pe_ratio else "市盈率TTM\t")
            # Format market cap like rains fmt_num function
            market_cap_str = fmt_num(profile.market_cap) if profile.market_cap else " - "
            traded_market_cap_str = fmt_num(profile.traded_market_cap) if profile.traded_market_cap else " - "

            click.echo(f"总市值  \t{market_cap_str}")
            click.echo(f"流通市值\t{traded_market_cap_str}")
        else:
            click.echo("Warning: Could not fetch company profile")

        # Optional data sections - simplified to match rains speed
        if all or financials:
            click.echo(f"\n{click.style('财务指标', bold=True)}")
            try:
                financial_data = sina_service.get_financials(symbol)
                if financial_data:
                    # Output like rains does - table format
                    cols = ["截止日期", "总营收", "净利润", "每股净资产", "每股资本公积金"]
                    for i, col in enumerate(cols):
                        output = f"{col:<16}"
                        for f in financial_data:
                            match i:
                                case 0:
                                    output += f"\t{f.date:<16}"
                                case 1:
                                    value = f"{f.total_revenue:,.0f}" if f.total_revenue else "-"
                                    output += f"\t{value:<16}"
                                case 2:
                                    value = f"{f.net_profit:,.0f}" if f.net_profit else "-"
                                    output += f"\t{value:<16}"
                                case 3:
                                    value = f"{f.ps_net_assets:.4f}" if f.ps_net_assets else "-"
                                    output += f"\t{value:<16}"
                                case 4:
                                    value = f"{f.ps_capital_reserve:.4f}" if f.ps_capital_reserve else "-"
                                    output += f"\t{value:<16}"
                        click.echo(output)
                else:
                    click.echo("No financial data available")
            except Exception as e:
                click.echo(f"Warning: Could not fetch financial data: {e}")

        if all or structure:
            click.echo(f"\n{click.style('股东结构', bold=True)}")
            try:
                structure_data = sina_service.get_shareholder_structure(symbol)
                if structure_data:
                    # Output like rains does
                    if structure_data.holders_num and structure_data.shares_avg:
                        holders = []
                        shares = []
                        for s in [structure_data]:  # Only one structure in rains
                            holders.append(f"{structure_data.holders_num:.0f}({structure_data.date})")
                            shares.append(f"{structure_data.shares_avg:.0f}({structure_data.date})")

                        click.echo(f"截止日期\t{structure_data.date}")
                        click.echo(f"股东户数\t{' '.join(holders)}")
                        click.echo(f"平均持股\t{' '.join(shares)}")
                        click.echo("十大股东")

                        for i, h in enumerate(structure_data.holders_ten or []):
                            shares_fmt = f"{h.shares:,.0f}" if h.shares >= 10000 else f"{h.shares:.0f}"
                            click.echo(f"{i+1}\t{h.name}\t({h.percent:.1f}%) {shares_fmt}")
                else:
                    click.echo("No shareholder structure data available")
            except Exception as e:
                click.echo(f"Warning: Could not fetch shareholder structure: {e}")

        if all or dividends:
            click.echo(f"\n{click.style('分红送配', bold=True)}")
            try:
                dividend_data = sina_service.get_dividends(symbol)
                if dividend_data:
                    # Output like rains does
                    click.echo("公告日期 \t 分红送配 \t\t\t 除权除息日 \t 股权登记日")
                    for d in dividend_data:
                        # Format the dividend info like rains does
                        info_parts = []
                        if d.shares_dividend > 0.0:
                            info_parts.append(f"送{d.shares_dividend}股")
                        if d.shares_into > 0.0:
                            info_parts.append(f"转{d.shares_into}股")
                        if d.money > 0.0:
                            info_parts.append(f"派{d.money}元")

                        info = "10" + "".join(info_parts) if info_parts else "不分配\t"

                        click.echo(
                            f"{d.date} \t {info if len(info) < 19 else info} \t\t {d.date_dividend if d.date_dividend else ' -\t'} \t {d.date_record if d.date_record else ' - '}"
                        )
                else:
                    click.echo("No dividend data available")
            except Exception as e:
                click.echo(f"Warning: Could not fetch dividend data: {e}")

        if all or presses:
            click.echo(f"\n{click.style('最新公告', bold=True)}")
            try:
                press_data = sina_service.get_press_releases(symbol)
                if press_data:
                    # Output like rains does
                    for p in press_data:
                        click.echo(f"{p.date}\t{p.title}\t{p.url}")
                else:
                    click.echo("No press release data available")
            except Exception as e:
                click.echo(f"Warning: Could not fetch press release data: {e}")

        return 0

    except Exception as e:
        logger.error(f"Info fetch failed: {e}", exc_info=True)
        click.echo(f"Info fetch failed: {e}", err=True)
        return 1


def fmt_num(num: float) -> str:
    """Format number like rains fmt_num function."""
    if num > 100_000_000.0:
        return f"{num / 100_000_000.0:.2f}亿"
    elif num == 0.0:
        return " - "
    else:
        return f"{num / 10_000.0:.2f}万"


def write_quote_formatted(quote):
    """Format and output quote data like rains does.

    Args:
        quote: Quote object with market data
    """
    from datetime import datetime

    # Calculate change rate and format price like rains does
    rate = (quote.price / quote.close_price - 1.0) * 100.0 if quote.close_price and quote.close_price != 0 else 0.0
    now = f"{quote.price:.2f} {rate:.2f}%"

    # Format volume (HK stocks multiply by 1000 like rains does)
    volume = quote.volume
    if volume and 'HK' in quote.symbol:
        volume = volume * 1000.0 if volume else None

    # Format volume display like rains (using fmt_num logic)
    if volume and volume >= 100000000:
        volume_display = f"{volume/100000000:.2f}亿"
    elif volume and volume == 0.0:
        volume_display = " - "
    else:
        volume_display = f"{volume/10000:.2f}万" if volume else " - "

    # Format turnover display like rains (using fmt_num logic)
    turnover = quote.turnover
    if turnover and turnover >= 100000000:
        turnover_display = f"{turnover/100000000:.2f}亿"
    elif turnover and turnover == 0.0:
        turnover_display = " - "
    else:
        turnover_display = f"{turnover/10000:.2f}万" if turnover else " - "

    # Use quote timestamp if available, otherwise current time like rains does
    date_str = quote.timestamp.strftime('%Y-%m-%d') if quote.timestamp else datetime.now().strftime('%Y-%m-%d')
    time_str = quote.timestamp.strftime('%H:%M:%S') if quote.timestamp else datetime.now().strftime('%H:%M:%S')

    # Format output exactly like rains - with colors and spacing
    colored_now = now
    if rate > 0.0:
        colored_now = click.style(now, fg='red', bold=True, underline=True)
    elif rate < 0.0:
        colored_now = click.style(now, fg='green', bold=True, underline=True)
    else:
        colored_now = click.style(now, fg='bright_black', bold=True, underline=True)

    # Exact formatting like rains: date time symbol(8 chars) price(16 chars) close open high low volume(8) turnover(8) name
    click.echo(f"{date_str} {time_str}  {quote.symbol:<8}  {colored_now:<16} \t昨收：{quote.close_price:.2f}\t今开：{quote.open_price:.2f}\t最高：{quote.high_price:.2f}\t最低：{quote.low_price:.2f}\t成交量：{volume_display:<8}\t成交额：{turnover_display:<8}\t{quote.name}")