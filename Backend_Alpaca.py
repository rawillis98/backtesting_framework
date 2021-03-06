import logging
import logging.config
from read_key import read_key
import datetime
import sys
import pause
import alpaca_trade_api as tradeapi
from Backend import Backend


class AlpacaBackend(Backend):
    def __init__(self, key_file, secret_file):
        self.key = read_key(key_file)
        self.secret = read_key(secret_file)
        self.api = tradeapi.REST(self.key, self.secret, r'https://paper-api.alpaca.markets')
        logging.config.fileConfig("logging.conf", disable_existing_loggers=True)
        self.logger = logging.getLogger(__name__)
        self.period = 1

    def get_account(self):
        return self.api.get_account()

    def verify_account_access(self):
        self.get_accout()
        return

    def get_cash(self):
        return float(self.get_account().cash)

    def get_equity(self):
        return float(self.get_account().equity)

    def order(self, symbol, qty, order_type='market', limit=None, stop_loss=None, time_in_force='day', extended_hours=False):
        if order_type not in ['market', 'limit', 'stop', 'stop_limit']:
            raise ValueError(f"Invalid order_type: {order_type}")

        if time_in_force not in ['day', 'gtc', 'fok', 'cls', 'opg', 'ioc']:
            raise ValueError(f"Invalid time_in_force: {time_in_force}")

        if not isinstance(qty, int):
            raise ValueError(f"qty must be integer: {qty}")

        if order_type in ['limit', 'stop_limit']:
            assert limit is not None, f"limit is required if order_type is {order_type}"

        if order_type in ['stop', 'stop_loss']:
            assert stop_loss is not None, f"stop_loss is required if order_type is {order_type}"

        if extended_hours:
            assert order_type == 'limit' and time_in_force == 'day', f"extended_hours only works with order_type=limit and time_in_force=day"
        

        side = 'buy' if qty > 0  else 'sell'
        qty = abs(qty)

        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                type=order_type,
                side=side,
                limit_price=limit,
                stop_price=stop_loss,
                time_in_force=time_in_force,
                extended_hours=extended_hours
            )

            return order
        except tradeapi.rest.APIError as e:
            self.logging.critical(e)
            sys.exit(1)

    def get_buying_power(self):
        return float(self.api.get_account().buying_power)

    def get_portfolio(self):
        return self.api.list_positions()

    def step(self, dt):
        dt = dt.replace(hour=dt.hour - 1)
        self.logger.debug(f"Sleeping until {dt} System Time")
        pause.until(dt)
        self.logger.debug(f"Done sleeping. System time is: {datetime.datetime.now()}")

    def get_time(self):
        time = self.api.get_clock().timestamp.to_pydatetime()
        time = time.replace(tzinfo=None)
        return time 

    def is_open(self):
        return self.api.get_clock().is_open

    def get_next_open(self):
        time = self.api.get_clock().next_open.to_pydatetime()
        time = time.replace(tzinfo=None)
        return time 

if __name__ == '__main__':
    ab = AlpacaBackend('/home/alex/Documents/keys/alpaca.key', '/home/alex/Documents/keys/alpaca.secret')
    print(ab.get_next_open())
