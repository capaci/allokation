import os
from datetime import date, timedelta

import pandas as pd
import requests_cache
from pandas_datareader import data as web

from allokation.utils import (calculate_amount,
                              calculate_percentage_of_each_ticker,
                              calculate_total_for_each_ticker,
                              get_closing_price_from_yahoo,
                              get_percentage_of_stocks, get_target_date,
                              transpose_prices)

STOCKS_DATA_FILEPATH = os.path.join(os.path.dirname(__file__), './data/stocks.csv')


def test_get_percentage_of_stocks_without_percentage_should_return_equal_distribution():
    tickers = [
        'B3SA3.SA',
        'BBDC4.SA',
        'CSAN3.SA',
        'CYRE3.SA',
    ]

    expected = 0.25

    result = get_percentage_of_stocks(tickers=tickers)

    assert result == expected


def test_get_percentage_of_stocks_with_percentage_should_return_pandas_series():
    tickers = [
        'B3SA3.SA',
        'BBDC4.SA',
        'CSAN3.SA',
        'CYRE3.SA',
    ]
    percentages = [40, 20, 20, 20]
    expected = pd.Series([0.4, 0.2, 0.2, 0.2])

    result = get_percentage_of_stocks(tickers=tickers, percentages=percentages)

    assert result.equals(expected)


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


def test_calculate_amount_with_equal_distribution():
    df = pd.read_csv(STOCKS_DATA_FILEPATH)
    available_money = 1000
    percentage_multiplier = 1/len(df)

    expected = (available_money*percentage_multiplier/df['price']).round(0)

    result = calculate_amount(df, available_money=available_money, percentage_multiplier=percentage_multiplier)

    assert result.equals(expected)


def test_calculate_amount():
    df = pd.read_csv(STOCKS_DATA_FILEPATH)
    available_money = 1000
    percentage_multiplier = pd.Series([0.33, 0.33, 0.34])

    expected = (available_money*percentage_multiplier/df['price']).round(0)

    result = calculate_amount(df, available_money=available_money, percentage_multiplier=percentage_multiplier)

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
