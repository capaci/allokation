import os
from datetime import date, timedelta

import pandas as pd
import pytest
import requests_cache
from pandas_datareader import data as web

from allokation.utils import (calculate_amount, calculate_multiplier,
                              calculate_percentage_of_each_ticker,
                              calculate_total_for_each_ticker,
                              get_closing_price_from_yahoo, get_target_date,
                              map_columns_without_suffix, transpose_prices)

STOCKS_DATA_FILEPATH = os.path.join(os.path.dirname(__file__), './data/stocks.csv')


def test_get_target_date_when_today_is_a_weekday():
    base_date = date(year=2020, month=9, day=4)
    expected = base_date

    result = get_target_date(base_date=base_date)

    assert result == expected


def test_get_target_date_when_today_is_saturday():
    base_date = date(year=2020, month=9, day=5)
    expected = base_date - timedelta(days=1)

    result = get_target_date(base_date=base_date)

    assert result == expected


def test_get_target_date_when_today_is_sunday():
    base_date = date(year=2020, month=9, day=6)
    expected = base_date - timedelta(days=2)

    result = get_target_date(base_date=base_date)

    assert result == expected


def test_get_closing_price_from_yahoo(mocker):
    """
    The get_closing_price_from_yahoo() calls get_data_yahoo from pandas_datareader, which returns a pandas dataframe.
    For this reason, some data for test purposes were saved in a sqlite cache.
    In this test, the cache is used to return this data.
    """
    tickers = [
        'B3SA3.SA',
        'BBDC4.SA',
        'CSAN3.SA',
        'CYRE3.SA',
        'GGBR4.SA',
        'MGLU3.SA',
        'PETR4.SA',
        'VVAR3.SA',
        'WEGE3.SA',
    ]
    target_date = date(year=2020, month=9, day=4)
    cache_session = requests_cache.CachedSession(
        cache_name='tests/data/data_from_yahoo',
        backend='sqlite',
        expires_after=None
    )
    cached_df = web.DataReader(tickers, 'yahoo', session=cache_session, start=target_date, end=target_date)

    expected = cached_df['Adj Close']

    mocker.patch('allokation.utils.web.get_data_yahoo', lambda tickers, date: cached_df)
    result = get_closing_price_from_yahoo(tickers, target_date)

    assert result.equals(expected)


def test_transpose_prices():
    df = pd.DataFrame(
        data=[[93.22, 21.89, 20.50]],
        columns=['MGLU3', 'PETR4', 'VVAR3']
    )

    result = transpose_prices(prices=df)

    expected = pd.read_csv(STOCKS_DATA_FILEPATH)

    assert result.equals(expected)


def test_map_columns_without_suffix():
    tickers = [
        'MGLU3.SA',
        'PETR4.SA',
        'VVAR3.SA',
    ]

    result = map_columns_without_suffix(tickers)

    expected = {
        'MGLU3.SA': 'MGLU3',
        'PETR4.SA': 'PETR4',
        'VVAR3.SA': 'VVAR3',
    }
    assert result == expected


def test_calculate_multiplier():
    df = pd.read_csv(STOCKS_DATA_FILEPATH)
    number_of_tickers = len(df.values)
    available_money = 1000

    expected = pytest.approx(3.57, 0.01)

    result = calculate_multiplier(df, number_of_tickers, available_money)

    assert result == expected


def test_calculate_amount():
    df = pd.read_csv(STOCKS_DATA_FILEPATH)
    multiplier = 1

    expected = (df['price'].max()/df['price']).round(0)

    result = calculate_amount(df, multiplier=multiplier)

    assert result.equals(expected)


def test_calculate_total_for_each_ticker():
    df = pd.read_csv(STOCKS_DATA_FILEPATH)
    df['amount'] = 1

    expected = df['price'] * df['amount']

    result = calculate_total_for_each_ticker(df)

    assert result.equals(expected)


def test_calculate_percentage_of_each_ticker():
    df = pd.read_csv(STOCKS_DATA_FILEPATH)
    df['amount'] = 5
    df['total'] = calculate_total_for_each_ticker(df)

    expected = df['total']/df['total'].sum() * 100

    result = calculate_percentage_of_each_ticker(df)

    assert result.equals(expected)
