/**
 * 个股页面
 * 重构以匹配 StockPrices 布局，使用下拉菜单和表格显示
 */

import React, { useState, useCallback, useEffect } from 'react';
import { StockListItem, ApiError } from '../types';
import StockSelector from '../components/StockSelector/StockSelector';
import { stockInfoApi, StockInfoResponse } from '../services/stockInfoApi';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';

const IndividualStockPage: React.FC = () => {
  const [selectedStock, setSelectedStock] = useState<StockListItem | null>(null);
  const [stockData, setStockData] = useState<StockInfoResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null | undefined>(null);
  const [stocks, setStocks] = useState<StockListItem[]>([]);
  const [stocksLoading, setStocksLoading] = useState<boolean>(true);
  const [stocksError, setStocksError] = useState<ApiError | null>(null);

  // Field name translations from English to Chinese
  const fieldTranslations: Record<string, string> = {
    // Company basic info
    'org_id': '组织ID',
    'org_name_cn': '公司名称',
    'org_short_name_cn': '公司简称',
    'org_name_en': '公司英文名',
    'org_short_name_en': '公司英文简称',
    'pre_name_cn': '公司曾用名',
    'org_cn_introduction': '公司介绍',
    'org_website': '公司官网',

    // Industry and sector
    'industry': '行业',
    'industry_code': '行业代码',
    'sector': '板块',
    'sector_code': '板块代码',
    'affiliate_industry': '所属行业',
    'classi_name': '分类名称',

    // Market info
    'market': '市场',
    'exchange': '交易所',
    'symbol': '股票代码',
    'stock_code': '股票代码',
    '股票代码': '股票代码',
    '股票简称': '股票简称',
    'currency': '货币',
    'currency_encode': '货币编码',

    // Financial metrics
    'pe_ratio': '市盈率',
    'pb_ratio': '市净率',
    'price_to_book': '市净率',
    'price_to_earnings': '市盈率',
    'pe_after_issuing': '发行后市盈率',
    'roe': '净资产收益率',
    'roa': '总资产收益率',
    'net_profit': '净利润',
    'total_assets': '总资产',
    'total_liability': '总负债',
    'total_equity': '股东权益',
    'market_cap': '市值',
    'circulating_cap': '流通市值',
    '总市值': '总市值',
    '流通市值': '流通市值',
    'reg_asset': '注册资本',

    // Trading info
    'current_price': '当前价格',
    'open_price': '开盘价',
    'close_price': '收盘价',
    'high_price': '最高价',
    'low_price': '最低价',
    'volume': '成交量',
    'turnover': '成交额',
    'turnover_rate': '换手率',
    'price_change': '涨跌额',
    'price_change_rate': '涨跌幅',
    'amplitude': '振幅',
    '最新': '最新价格',

    // Company details
    'listing_date': '上市日期',
    'listed_date': '上市日期',
    '上市时间': '上市时间',
    'established_date': '成立日期',
    'total_shares': '总股本',
    'circulating_shares': '流通股本',
    '总股本': '总股本',
    '流通股': '流通股',
    'actual_issue_vol': '实际发行量',
    'issue_price': '发行价格',
    'online_success_rate_of_issue': '网上发行中签率',
    'actual_rc_net_amt': '实际募集资金净额',

    // Personnel
    'chairman': '董事长',
    'general_manager': '总经理',
    'legal_representative': '法定代表人',
    'secretary': '董事会秘书',
    'actual_controller': '实际控制人',

    // Contact info
    'telephone': '电话',
    'fax': '传真',
    'email': '邮箱',
    'postcode': '邮编',

    // Addresses
    'office_address_cn': '办公地址',
    'office_address_en': '办公地址(英文)',
    'reg_address_cn': '注册地址',
    'reg_address_en': '注册地址(英文)',

    // Business info
    'main_operation_business': '主营业务',
    'operating_scope': '经营范围',
    'staff_num': '员工人数',
    'executives_nums': '高管人数',

    // Geographic
    'provincial_name': '省份',
    'district_encode': '地区编码',

    // Other common fields
    'description': '描述',
    'website': '官网',
    'address': '地址',
    'phone': '电话',
    'business_scope': '经营范围',
    'employees': '员工人数',
    'establishment_date': '成立日期'
  };

  const getTranslatedFieldName = (key: string): string => {
    return fieldTranslations[key] || key; // Return translated name or original key if not found
  };

  // Load stock list on component mount
  useEffect(() => {
    const loadStocks = async () => {
      try {
        setStocksLoading(true);
        const response = await stockInfoApi.getStockList();
        setStocks(response.stocks);
        setStocksError(null);
      } catch (err) {
        setStocksError(err as ApiError);
      } finally {
        setStocksLoading(false);
      }
    };

    loadStocks();
  }, []);

  const handleStockSelect = useCallback(async (stock: StockListItem | null) => {
    setSelectedStock(stock);
    setError(null);

    if (!stock) {
      setStockData(null);
      return;
    }

    setLoading(true);
    try {
      const data = await stockInfoApi.getStockInfo(stock.code);
      setStockData(data);
      setError(null);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || '获取股票信息失败');
      setStockData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="flex flex-col h-full gap-2 w-full p-1 dark:bg-gray-900 transition-colors duration-200">
      {/* 控制头部 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 p-2 flex flex-col md:flex-row gap-2 items-center justify-between transition-colors duration-200">
        <div className="w-full md:w-96">
          <StockSelector
            stocks={stocks}
            selectedStock={selectedStock}
            onSelect={handleStockSelect}
            isLoading={stocksLoading}
            error={stocksError?.message || null}
          />
        </div>
      </div>

      {/* 主要内容 */}
      <div className="flex-1 flex flex-col gap-2 min-h-0">
        {selectedStock ? (
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden flex flex-col transition-colors duration-200">
            {/* 股票信息头部 */}
            <div className="p-3 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-gray-900 dark:text-white">
                    {selectedStock.code} - {selectedStock.name}
                  </h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    个股详细信息
                  </p>
                </div>
                {stockData && (
                  <div className="flex space-x-2 text-xs">
                    <span className={`px-2 py-1 rounded-full ${
                      stockData.data_sources.east_money
                        ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                        : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                    }`}>
                      东方财富: {stockData.data_sources.east_money ? '成功' : '失败'}
                    </span>
                    <span className={`px-2 py-1 rounded-full ${
                      stockData.data_sources.xueqiu
                        ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                        : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                    }`}>
                      雪球: {stockData.data_sources.xueqiu ? '成功' : '失败'}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* 内容 */}
            <div className="flex-1 overflow-auto p-3">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <LoadingSpinner message="加载股票信息中..." />
                </div>
              ) : error ? (
                <ErrorMessage error={error} onRetry={() => handleStockSelect(selectedStock)} />
              ) : stockData ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          项目
                        </th>
                        <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          数值
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {Object.entries(stockData).filter(([key]) =>
                        !['code', 'data_sources', 'errors', 'last_updated'].includes(key)
                      ).map(([key, value], index) => (
                        <tr key={key} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors bg-white dark:bg-gray-800">
                          <td className="px-3 py-2 whitespace-nowrap text-xs font-medium text-gray-900 dark:text-gray-100">
                            {getTranslatedFieldName(key)}
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500 dark:text-gray-400">
                            {value !== null && value !== undefined && value !== 'None' ? String(value) : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500 dark:text-gray-400">
                    选择股票代码开始查看信息
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 flex items-center justify-center transition-colors duration-200">
            <EmptyState
              title="选择股票"
              description="从上方下拉菜单中选择股票查看详细信息"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default IndividualStockPage;