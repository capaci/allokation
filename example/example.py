from pprint import pp

from allokation import allocate_money

AVAILABLE_MONEY = 1000

tickers = [
    'B3SA3.SA',
    'BBDC4.SA',
    'MGLU3.SA',
    'PETR4.SA',
    'VVAR3.SA',
]

result = allocate_money(available_money=AVAILABLE_MONEY, tickers=tickers)
pp(result)
