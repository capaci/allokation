from datetime import date, timedelta

from allokation import (
    get_closing_price_from_yahoo,
    map_columns_without_suffix,
    transpose_prices,
    calculate_multiplier,
    calculate_amount,
    calculate_total_for_each_ticker,
    calculate_percentage_of_each_ticker
)

AVAILABLE_MONEY = 1000

tickers = [
    'B3SA3.SA',
    'BBDC4.SA',
    'MGLU3.SA',
    'PETR4.SA',
    'VVAR3.SA',
]

weekdays = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
]

target_date = date.today()
weekday = weekdays[target_date.weekday()]
if weekday == 'saturday':
    target_date = target_date - timedelta(days=1)
elif weekday == 'sunday':
    target_date = target_date - timedelta(days=2)

prices = get_closing_price_from_yahoo(tickers=tickers, date=date.today()-timedelta(days=2))

renamed_columns = map_columns_without_suffix(tickers)

prices.rename(columns=renamed_columns, inplace=True)

df = transpose_prices(prices)

multiplier = calculate_multiplier(df, number_of_tickers=len(tickers), available_money=AVAILABLE_MONEY)

df['amount'] = calculate_amount(df, multiplier)
df['total'] = calculate_total_for_each_ticker(df)
df['percentage'] = calculate_percentage_of_each_ticker(df)

print(df)
print(f'multiplier = {multiplier}')

total_sum = df["total"].sum()
print(f'MONEY = {AVAILABLE_MONEY}')
print(f'TOTAL = {total_sum}')
print(f'DIFF  = {AVAILABLE_MONEY - total_sum}')
