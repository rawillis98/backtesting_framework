from Strategy import Strategy
from Backend_Alpaca import AlpacaBackend
from Backend_Backtest import AlphaVantageBacktest 
import datetime
from datetime import timedelta, time
import warnings
import logging
warnings.filterwarnings("ignore")


class BH(Strategy):
    name = "Buy and Hold"
    backend = AlphaVantageBacktest(start=datetime.datetime(2001, 1, 3, 9, 30),
                                   end=datetime.datetime(2019, 6, 1))
    def __init__(self):
        super(BH, BH).__init__(self)
        logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
        self.logger = logging.getLogger(self.name)
        self.logger.info(f"Initialized {self.name}!")

        qty = self.backend.get_cash() // self.backend.quote("SPY")
        self.backend.order("SPY", qty)


if __name__ == '__main__':
    s = BH()
    s.run()
    s.analyze()
