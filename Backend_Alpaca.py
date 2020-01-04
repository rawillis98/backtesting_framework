from read_key import read_key
import sys
import alpaca_trade_api as tradeapi
from Backend import Backend


class AlpacaBackend(Backend):
    def __init__(self, key_file, secret_file):
        self.key = read_key(key_file)
        self.secret = read_key(secret_file)
        self.api = tradeapi.REST(self.key, self.secret, r'https://paper-api.alpaca.markets')
        self.period = 1

    def get_account(self):
        return self.api.get_account()

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
            print(e)
            sys.exit(1)



    def get_buying_power(self):
        return float(self.api.get_account().buying_power)

    def get_portfolio(self):
        return self.api.list_positions()

    def step(self):
        time.sleep(self.period)



    

    

if __name__ == '__main__':
    ab = AlpacaBackend('/home/alex/Documents/keys/alpaca.key', '/home/alex/Documents/keys/alpaca.secret')
    print(ab.get_account())
