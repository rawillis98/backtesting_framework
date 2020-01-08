import numpy as np
from Backend import Backend
import pandas as pd
import logging
import logging.config
import os
from read_key import *
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime, time


class AlphaVantageBacktest(Backend):
    data_dir = r'/home/alex/Documents/Projects/data'
    av_key_file = r'/home/alex/Documents/keys/alpha_vantage.key'

    def __init__(self, start, end=datetime.now(), cash=100e3):
        super(AlphaVantageBacktest).__init__()
        self.__cash = cash
        self.end_time = end

        # set up alpha vantage
        av_key = read_key(self.av_key_file)
        self.ts = TimeSeries(av_key, output_format='pandas', indexing_type='date')        
        logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
        self.logger = logging.getLogger(__name__)

        self.__dt = start
        self.__portfolio = {}

    def get_next_open(self):
        symbol_for_calender = "SPY"
        self.quote(symbol_for_calender)
        data = pd.read_csv(os.path.join(self.data_dir, symbol_for_calender + '.csv'))
        data['date'] = pd.to_datetime(data['date'], infer_datetime_format=True)
        mask = self.__dt.date() == data['date'].apply(lambda x: x.date())
        current_date_index = data[mask].index
        next_open_dt = data['date'][current_date_index - 1].values[0]
        next_open_dt = self.to_datetime(next_open_dt).date()
        open_time = time(9, 30, 0)
        next_open = datetime.combine(next_open_dt, open_time)
        return next_open

    def to_datetime(self, date):
        timestamp = ((date - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's'))
        return datetime.utcfromtimestamp(timestamp)

    def is_open(self):
        return time(9, 30, 0) <= self.__dt.time() <= time(16, 0, 0)

    def verify_account_access(self):
        return True

    def get_cash(self):
        return self.__cash

    def get_buying_power(self):
        return self.__cash

    def order(self, symbol, qty, order_type='market', limit=None, stop_loss=None, good_for='gfd'):
        price = self.quote(symbol)
        self.logger.debug(f"Order: {symbol}x{qty}@{price}")
        self.__cash -= qty * price
        if symbol not in self.__portfolio:
            self.__portfolio[symbol] = 0
        self.__portfolio[symbol] += qty

    def get_equity(self):
        equity = self.get_cash()
        for symbol, qty in self.__portfolio.items():
            equity += self.quote(symbol) * qty
        return equity

    def get_portfolio(self):
        return self.__portfolio

    def step(self, until):
        self.logger.info(f"Sleeping until f{until}")
        self.__dt = until
        self.logger.info("Done sleeping")

    def get_time(self):
        return self.__dt

    def get_files_in_data_dir(self):
        listdir = os.listdir(self.data_dir)
        return [f for f in listdir if os.path.isfile(os.path.join(self.data_dir, f))]

    def quote(self, symbol, redownload=False):
        data_files = self.get_files_in_data_dir()
        file_path = os.path.join(self.data_dir, symbol + '.csv')
        if symbol + ".csv" not in data_files or redownload:
            self.logger.debug(f"{symbol + '.csv'} not in data_dir, downloading data")
            data, metadata = self.ts.get_daily(symbol, outputsize='full')
            data.to_csv(file_path)
        data = pd.read_csv(file_path)
        data['date'] = pd.to_datetime(data['date'], infer_datetime_format=True)

        mask = self.__dt.date() == data['date'].apply(lambda x: x.date())
        data = data[mask]

        close = data['4. close'].values[0]
        return close


if __name__ == '__main__':
    bt = Backtest_Alpha_Vantage(datetime(2017, 1, 3, 10, 0, 0))
    bt.quote("GOOG")
    print(bt)
