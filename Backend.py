from abc import ABC, abstractmethod


class Backend(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def order(self, symbol, qty, order_type='market', limit=None, stop_loss=None, good_for='gfd'):
        pass

    @abstractmethod
    def get_cash(self):
        pass

    @abstractmethod
    def get_buying_power(self):
        pass

    @abstractmethod
    def get_equity(self):
        pass

    @abstractmethod
    def get_portfolio(self):
        pass

    @abstractmethod
    def step(self):
        pass

    @abstractmethod
    def get_time(self):
        pass
