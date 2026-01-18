"""CLI commands for the stock library."""

import click
from services.database_service import DatabaseService
from services.api_service import ApiService
from services.historical_data_service import HistoricalDataService
from lib.config import Config
from lib.logging import setup_logging, get_logger
import json
import concurrent.futures
from typing import Dict, Any


@click.group()
@click.option('--log-level', default='INFO', help='Logging level')
@click.option('--log-file', default=None, help='Log file path')
@click.option('--debug', is_flag=True, help='Enable full debug mode with performance metrics')
def cli(log_level, log_file, debug):
    """Stock data management CLI."""
    if debug:
        log_level = 'DEBUG'
        from lib.debug import enable_debug_logging
        enable_debug_logging()

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