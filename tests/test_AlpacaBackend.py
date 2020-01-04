import pytest
from Backend_Alpaca import AlpacaBackend


def get_alpaca_backend():
    return AlpacaBackend('alpaca.key', 'alpaca.secret')

def test_get_account():
    ab = get_alpaca_backend()
    account = ab.get_account()
    print(account)
    assert hasattr(account, 'account_number'), "Couldn't get account_number"

def test_get_cash():
    ab = get_alpaca_backend()
    print(ab.get_cash())
    assert ab.get_cash() is not None
    assert isinstance(ab.get_cash(), float)

def test_get_equity():
    ab = get_alpaca_backend()
    print(ab.get_equity())
    assert ab.get_equity() is not None
    assert isinstance(ab.get_equity(), float)

def test_order():
    ab = get_alpaca_backend()
    order = ab.order('MSFT', 2, order_type='limit', limit=5.0, extended_hours=True)
    print(order)
    assert False

def test_get_buying_power():
    ab = get_alpaca_backend()
    bp = ab.get_buying_power()
    print(bp)
    assert isinstance(bp, float)
    
def test_get_portfolio():
    ab = get_alpaca_backend()
    portfolio = ab.get_portfolio()
    print(portfolio)
    assert False
