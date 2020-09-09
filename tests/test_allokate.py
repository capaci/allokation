from datetime import date

import pytest
import requests_cache
from pandas_datareader import data as web

from allokation.allokate import allocate_money


def test_allocate_money(mocker):
    """
    The get_closing_price_from_yahoo() calls get_data_yahoo from pandas_datareader, which returns a pandas dataframe.
    For this reason, some data for test purposes were saved in a sqlite cache.
    In this test, the cache is used to return this data.
    """
    tickers = [
        'B3SA3.SA',
        'BBDC4.SA',
        'MGLU3.SA',
        'PETR4.SA',
        'VVAR3.SA',
    ]
    target_date = date(year=2020, month=9, day=4)
    cache_session = requests_cache.CachedSession(
        cache_name='tests/data/data_from_yahoo',
        backend='sqlite',
        expires_after=None
    )
    cached_df = web.DataReader(tickers, 'yahoo', session=cache_session, start=target_date, end=target_date)

    mock_result = cached_df['Adj Close']

    mocker.patch('allokation.allokate.get_closing_price_from_yahoo', lambda tickers, date: mock_result.copy())
    result = allocate_money(1000, tickers)

    assert result.get('allocations', None)
    assert result.get('total_value', None)
    assert result['allocations'].get('B3SA3.SA', None)
    assert result['allocations'].get('BBDC4.SA', None)
    assert result['allocations'].get('MGLU3.SA', None)
    assert result['allocations'].get('PETR4.SA', None)
    assert result['allocations'].get('VVAR3.SA', None)


def test_allocate_money_with_percentage_with_different_length_than_stocks():
    with pytest.raises(Exception):
        tickers = [
            'B3SA3.SA',
            'BBDC4.SA',
            'MGLU3.SA',
            'PETR4.SA',
            'VVAR3.SA',
        ]

        percentages = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

        allocate_money(1000, tickers, percentages=percentages)
