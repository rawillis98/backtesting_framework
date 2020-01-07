from Strategy import Strategy
from Backend_Alpaca import AlpacaBackend
from datetime import timedelta, time
import warnings
import logging
warnings.filterwarnings("ignore")


class MyStrat(Strategy):
    name = "My Strat"
    backend = AlpacaBackend('alpaca.key', 'alpaca.secret')
    universe = ["FB", "AAPL", "AMZN", "NFLX", "GOOG"]

    def __init__(self):
        super(MyStrat, MyStrat).__init__(self)
        self.schedule_function("buy", trading_days=1, tod=time(11, 16))
        self.schedule_function("sell", trading_days=1, tod=time(11, 17))
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

s = MyStrat()
s.run()
