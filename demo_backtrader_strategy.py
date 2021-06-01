# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2019-2021 http://www.backtrader.cn  3952700@qq.com
#
###############################################################################

import datetime
import backtrader as bt
import os
from backtradercn.ctpstore import CtpStore


class Resample(bt.Strategy):
    params = (
        ('short_period', 13),
        ('long_period', 377),
        ('optim', False),  # 是不是开启优化方式
        ('optim_fs', (55, 377)),
        ('print_debug', True),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.print_debug or doprint:
            dt = dt or self.thedata.datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_data(self, data, status, *args, **kwargs):
        super().notify_data(data, status, *args, **kwargs)
        print('notify_data:', data._getstatusname(status), *args)
        print("data len:", len(self.datas[0]))
        print("self.position:", self.position)
        if data._getstatusname(status) == "LIVE":
            self.live_bars = True

        if len(self.datas[0]) > 1:
            # 必须有[-1][0]两个数据
            for i in range(len(self.datas[0]) - 1, -1, -1):
                print("display in notify_data:", i, self.datas[0].datetime.datetime(-i),
                      self.datas[0].open[-i], self.datas[0].high[-i], self.datas[0].low[-i], self.datas[0].close[-i],
                      "sma1", self.sma1[-i],
                      # self.datas[0].pre_close_price[-i],
                      self.datas[0].last_price[-i],
                      self.datas[0].average_price[-i],
                      self.datas[0].volume[-i],

                      self.datas[0].turnover[-i],
                      # self.datas[0].pre_open_interest[-i],
                      self.datas[0].open_interest[-i],
                      self.datas[0].open_price[-i],

                      self.datas[0].high_price[-i],
                      self.datas[0].low_price[-i],
                      self.datas[0].close_price[-i],
                      self.datas[0].upper_limit_price[-i],

                      self.datas[0].lower_limit_price[-i],
                      # self.datas[0].pre_settlement_price[-i],
                      # self.datas[0].settlement_price[-i],

                      self.datas[0].ask_price[-i],
                      self.datas[0].ask_volume[-i],
                      self.datas[0].bid_price[-i],
                      self.datas[0].bid_volume[-i],

                      )

    def notify_store(self, msg, *args, **kwargs):
        print('notify_store:', msg)

    def notify_order(self, order):
        print('notify_store:', order)

    def notify(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        if order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None
            self.log('Order Canceled/Margin/Rejected')
            if hasattr(order.info, 'error_id'):
                self.log('Order status %s, error_id, %s' % (order.status, order.info.error_id))

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed]:
            # Write down: no pending order
            self.order = None

    def __init__(self):
        self.live_bars = False
        self.order = None
        self.sma1 = bt.indicators.SMA(self.datas[0], period=self.params.short_period)
        self.thedata = self.datas[0]

    def next(self):
        print("self.live_bars:", self.live_bars, " name:", self.datas[0]._name, " len:", len(self.datas[0]))
        if not self.live_bars:
            return

        print(self.datas[0].datetime.datetime(0),
              self.datas[0].open[0], self.datas[0].high[0], self.datas[0].low[0], self.datas[0].close[0],
              "sma1", self.sma1[0],

              self.datas[0].pre_close_price[0],
              self.datas[0].last_price[0],
              self.datas[0].average_price[0],
              self.datas[0].volume[0],

              self.datas[0].turnover[0],
              self.datas[0].pre_open_interest[0],
              self.datas[0].open_interest[0],
              self.datas[0].open_price[0],

              self.datas[0].high_price[0],
              self.datas[0].low_price[0],
              self.datas[0].close_price[0],
              self.datas[0].upper_limit_price[0],

              self.datas[0].lower_limit_price[0],
              self.datas[0].pre_settlement_price[0],
              self.datas[0].settlement_price[0],

              self.datas[0].ask_price[0],
              self.datas[0].ask_volume[0],
              self.datas[0].bid_price[0],
              self.datas[0].bid_volume[0],

              )

        account_value = self.broker.getvalue()
        account_cash = self.broker.getcash()
        # 得到当天的时间
        current_date = self.datas[0].datetime.datetime(0)
        if self.params.print_debug:
            pass
            # print("current_date:", current_date, " account_value:", account_value, " account_cash:", account_cash)

        if self.order:
            # if an order is active, no new orders are allowed
            return

        # Check if we are in the market
        if not self.position:
            print("no position ", self.datas[0]._dataname, )
            pass
            # 测试开仓
            if self.datas[0].last_price[0] > self.sma1[0]:
                self.order = self.buy(price=self.datas[0].ask_price[0],  size=abs(1))
            elif self.datas[0].last_price[0] < self.sma1[0]:
                self.order = self.sell(price=self.datas[0].bid_price[0], size=abs(1))
        else:
            size = self.position.size
            print("position:", self.datas[0]._dataname, size, self.position)
            # 测试平仓
            if size > 0:
                if self.datas[0].last_price[0] < self.sma1[0]:
                    self.order = self.close(price=self.datas[0].bid_price[0],  size=abs(size))
            elif size < 0:
                if self.datas[0].last_price[0] > self.sma1[0]:
                    self.order = self.close(price=self.datas[0].ask_price[0],  size=abs(size))

if __name__ == '__main__':
    from sys import platform
    if platform != "win32":
        # linux
        csv_folder_path = r"/home/bt_docker_share_folder/ctp_test_cases/tick_folder_history_bar/"
    else:
        # window
        csv_folder_path = r"F:\lbc\product_env\ctp_test_cases_dwqh\tick_folder_history_bar"

    import logging
    logging.basicConfig(
        format='%(asctime)s[%(processName)s-%(process)d][%(threadName)s-%(thread)d] [%(filename)s:%(lineno)s] %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

    cerebro = bt.Cerebro()
    cerebro.addstrategy(Resample)

    store = CtpStore(
        qcheck=0.05,
        source_id='ctp',
        account_id='1111', # 参数含义参考课程讲解  https://edu.csdn.net/course/detail/24668
        app_id='ctp_store',  # 需要保证app_id在全系统的唯一性,并且长度不超过32bytes
        register_center_address='localhost:50051',
        location_ip='127.0.0.1',
        grpc_address='localhost:50056',
        paper_trading=0,
        offline=False,
        cachefile_valid_seconds=300,
        detect_position_change_timer=300,
        print_debug=True,
    )
    broker = store.getbroker()
    cerebro.setbroker(broker)

    instrumentId = "hc2110"
    from backtradercn.backfill import load_csv_candles, load_csv_ticks

    # 加载实时tick数据并预先填充历史数据
    # 填充历史来自backtradercn-ctp_collector产生的分钟线,使用load_csv_candles加载
    # 当然如果机器够快,硬盘够大,也可以使用load_csv_ticks加载历史tick
    data0 = store.getdata(dataname=instrumentId,
                          qcheck=0.5,
                          historical=False,
                          # backfill_from=load_csv_ticks(
                          #     datapath=r"/home/bt_docker_share_folder/ctp_test_cases/tick_folder/%s.csv" % instrumentId,
                          #     dataname=instrumentId,
                          #     fromdate=datetime.datetime.now() - datetime.timedelta(days=30),
                          #     todate=datetime.datetime.now(),
                          #     timeframe=bt.TimeFrame.Ticks,
                          #     compression=1
                          # ),
                          backfill_from=load_csv_candles(
                              datapath=os.path.join(csv_folder_path, "%s.csv" % instrumentId),
                              dataname=instrumentId,
                              fromdate=datetime.datetime.now() - datetime.timedelta(days=30),
                              todate=datetime.datetime.now(),
                              timeframe=bt.TimeFrame.Minutes,
                              compression=1
                          ),
                          timeframe=bt.TimeFrame.Minutes, compression=1,
                          fromdate=datetime.datetime.now() - datetime.timedelta(days=30),
                          todate=None,
                          )
    cerebro.adddata(data0)
    cerebro.resampledata(data0,
                         compression=5,
                         timeframe=bt.TimeFrame.Seconds)
    # cerebro.resampledata(data0,
    #                      compression=1,
    #                      timeframe=bt.TimeFrame.Days)
    cerebro.run()
    print("done")
