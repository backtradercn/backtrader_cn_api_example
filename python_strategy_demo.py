# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2019-2021 http://www.backtrader.cn  3952700@qq.com
#
###############################################################################

config_str = {
    'register_center_address': 'localhost:50051',
    'location_ip': '127.0.0.1',
    'grpc_address': 'localhost:50056',
    'source_id': 'ctp',
    'account_id': '526013021'
}

config_int = {
    'log_level': 0,
	'cachefile_valid_seconds': 300,
	'paper_trading': 0,
    'heartbeat_every_seconds': 300
}

config_double = {}

import numpy as np

from pystrategy import *
# help(strategy)

# st = strategy("python_strategy_demo", config_str, config_int, config_double)


'''
    BsFlagBuy = '1'
    BsFlagSell = '2'
    BsFlagUnknown = '0'
    DirectionLong = '0'
    DirectionShort = '1'
    OffsetClose = '1'
    OffsetCloseToday = '2'
    OffsetCloseYesterday = '3'
    OffsetOpen = '0'
    OrderStatusCancelled = '3'
    OrderStatusError = '4'
    OrderStatusFilled = '5'
    OrderStatusPartialFilledActive = '7'
    OrderStatusPartialFilledNotActive = '6'
    OrderStatusPending = '2'
    OrderStatusSubmitted = '1'
    OrderStatusUnknown = '0'
    PriceTypeAny = '0'
    PriceTypeBest5 = '2'
    PriceTypeForwardBest = '4'
    PriceTypeLimit = '3'
    PriceTypeReverseBest = '5'
    SideBuy = '0'
    SideSell = '1'
    TimeConditionGFD = '1'
    TimeConditionGTC = '2'
    TimeConditionIOC = '0'
    VolumeConditionAll = '2'
    VolumeConditionAny = '0'
    VolumeConditionMin = '1'

'''

class MyPairTradeStrategy(strategy):
    def __init__(self, name, config_str, config_int, config_double):
        strategy.__init__(self, name, config_str, config_int, config_double)
        self.name = name

        self.source_id = config_str["source_id"]
        self.account_id = config_str["account_id"]

        self.instrument_id_a = "rb2110"
        self.instrument_id_b = "hc2110"
        self.exchange_id_a = "SHFE"
        self.exchange_id_b = "SHFE"

        self.md_a_ask = 0
        self.md_b_bid = 0
        self.price_diff_aask_bbid = np.array([])

    def init(self):
        print('init')
        self.add_md(self.source_id, self.account_id)
        self.add_account(self.source_id, self.account_id, 10000.0)
       
    def md_subscribe(self, instrument_id):
        self.subscribe(self.source_id, self.account_id, [instrument_id], "", False)

    def on_quote(self, quote):
        print(quote.instrument_id, quote.trading_day, quote.data_time, \
              quote.ask_price[0], quote.ask_volume[0], \
              quote.bid_price[0], quote.bid_volume[0], \
              quote.open_interest, quote.turnover, \
              quote.volume, quote.pre_close_price, \
              quote.open_price, flush=True
              )
        # get_last_md 测试,总是返回对象,需要检查里面的 len(quote.instrument_id) > 0
        md_a = self.get_last_md(self.instrument_id_a, self.exchange_id_a)
        if len(md_a.instrument_id) == 0:
            return
        self.md_a_ask = md_a.ask_price[0]

        md_b = self.get_last_md(self.instrument_id_b, self.exchange_id_b)
        if len(md_b.instrument_id) == 0:
            return
        self.md_b_bid = md_b.ask_price[0]

        if self.md_a_ask == 0 and self.md_b_bid == 0:
            return

        self.price_diff_aask_bbid = np.append(self.price_diff_aask_bbid, [self.md_a_ask - self.md_b_bid])

        if len(self.price_diff_aask_bbid) > 10:
            print(self.price_diff_aask_bbid)

        # if (self.c%10 == 0):
        #     ret = self.req_position(self.source_id, self.account_id)
        #     print("self.req_position(self.source_id, self.account_id)", ret)
        #     ret = self.req_account(self.source_id, self.account_id)
        #     print("self.req_account(self.source_id, self.account_id)", ret)
        #     #OffsetOpen/OffsetClose/OffsetCloseToday/OffsetCloseYesterday
        #     self.order_id = self.insert_limit_order("rb2101", self.exchange_id, self.account_id, quote.ask_price[0], 1,
        #                                 SideBuy, OffsetOpen)
        #     print("insert_limit_order", self.order_id)

    def on_trade(self, trade):
        print('on trade:', trade)

    def on_order(self, order):
        print('on_order', order)

    def list_positions(self, ):
        return []

    def get_instrument(self, instrumentID):
        pass
        # return get_instrument(instrumentID)

    def on_position(self, pos):
        print(pos)

    def on_position_detail(self, pos):
        print(pos)

    def on_account(self, account):
        print(account)

    def on_future_instrument(self, instrumentInfo):
        print(instrumentInfo)

    def on_order_action_error(self, orderactionerror):
        print('on_order_action_error')
        print(orderactionerror)

    def on_order_input_error(self, orderinputerror):
        print('on_order_input_error')
        print(orderinputerror)


def run_strategy():
    st = MyPairTradeStrategy("pair_strategy_demo", config_str, config_int, config_double)
    st.init()
    st.md_subscribe(st.instrument_id_a)
    st.md_subscribe(st.instrument_id_b)
    st.run()
    print("done")

def test_np_code():
    arr = np.array([])
    for x in [1, 2, 3, 4, 5, 6]:
        arr = np.append(arr, [x])
    print(arr)
    # 求均值
    arr_mean = np.mean(arr)
    # 求方差
    arr_var = np.var(arr)
    # 求标准差
    arr_std = np.std(arr, ddof=1)
    print("arr_mean:", arr_mean)
    print("arr_var:", arr_var)
    print("arr_std:", arr_std)

if __name__ == '__main__':
    test_np_code()
    run_strategy()




