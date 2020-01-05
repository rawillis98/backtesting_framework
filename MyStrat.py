from Strategy import Strategy
from Backend_Alpaca import AlpacaBackend
from datetime import timedelta, time
import warnings
warnings.filterwarnings("ignore")


class MyStrat(Strategy):
    name = "My Strat"
    backend = AlpacaBackend('alpaca.key', 'alpaca.secret')
    universe = ["FB", "AAPL", "AMZN", "NFLX", "GOOG"]

    def __init__(self):
        super(MyStrat, MyStrat).__init__(self)
        self.schedule_function("buy", trading_days=1, tod=time(10, 30))
        self.schedule_function("sell", trading_days=1, tod=time(2, 30))

    def buy(self):
        for symbol in self.universe:
            self.context['qty'] = 2
            self.backend.order(symbol, self.context['qty'])

    def sell(self):
        for symbol in self.universe:
            self.backend.order(symbol, -self.context['qty'])

s = MyStrat()
s.run()
