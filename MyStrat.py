from Strategy import Strategy
from Backend_Alpaca import AlpacaBackend
from Backend_Backtest import AlphaVantageBacktest 
import datetime
from datetime import timedelta, time
import warnings
import logging
warnings.filterwarnings("ignore")


class MyStrat(Strategy):
    name = "My Strat"
    # backend = AlpacaBackend('alpaca.key', 'alpaca.secret')
    backend = AlphaVantageBacktest(start=datetime.datetime(2017, 1, 3, 9, 30),
                                   end=datetime.datetime(2017, 6, 1))
    universe = ["FB", "AAPL", "AMZN", "NFLX", "GOOG"]

    def __init__(self):
        super(MyStrat, MyStrat).__init__(self)
        self.schedule_function("buy", trading_days=1, tod=time(11, 16))
        self.schedule_function("sell", trading_days=2, tod=time(11, 17))
        logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
        self.logger = logging.getLogger(self.name)
        self.logger.info("Initialized My Strat!")

    def buy(self):
        self.logger.info("Buying!")
        for symbol in self.universe:
            self.context['qty'] = 2
            self.backend.order(symbol, self.context['qty'])

    def sell(self):
        self.logger.info("Selling!")
        for symbol in self.universe:
            self.backend.order(symbol, -self.context['qty'])

if __name__ == '__main__':
    s = MyStrat()
    s.run()
    s.analyze()
