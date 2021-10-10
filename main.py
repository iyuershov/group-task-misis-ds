import numpy as np
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta

# load data about oil prices from file
oil_df = pd.read_csv('data/brent_daily.csv')
# preprocess oil_df
oil_df['Date'] = pd.to_datetime(oil_df['Date'], format='%Y-%m-%d')

# load data about dollar rate from file
dollar_df = pd.read_xml('data/dollar_rate.xml')
# preprocess dollar_df
dollar_df['Value'] = dollar_df['Value'].str.replace(',', '.').astype(float)
dollar_df['Date'] = pd.to_datetime(dollar_df['Date'], format='%d.%m.%Y')
dollar_df = dollar_df.drop(columns=['Id', 'Nominal'])

# load data about inflation from file
inflation_df = pd.read_csv('data/inflation.csv')
# preprocess inflation_df
inflation_df = inflation_df.drop(columns=['LOCATION', 'INDICATOR', 'SUBJECT', 'MEASURE', 'FREQUENCY', 'Flag Codes'])
inflation_df.rename(columns={'TIME': 'year', 'Value': 'value'}, inplace=True)

# prepare DataFrame which contains info about oil_price and dollar_rate
oil_x_dollar_df = oil_df.merge(dollar_df, on='Date')
oil_x_dollar_df.rename(columns={'Value': 'dollar_rate', 'Price': 'oil_price'}, inplace=True)
oil_x_dollar_df['oil_price_rub'] = oil_x_dollar_df['oil_price'] * oil_x_dollar_df['dollar_rate']


# prepare empty dicts for results
correlation_by_years = {}
mean_by_years = {}
std_by_years = {}
statistical_outliers = []

# set date frames
current_date_start = datetime.strptime('2000-01-01', '%Y-%m-%d')
date_finish = datetime.strptime('2021-01-01', '%Y-%m-%d')

# loop by every year
while current_date_start < date_finish:
    current_date_finish = current_date_start + relativedelta(years=1)

    current_year_df = oil_x_dollar_df[
        (oil_x_dollar_df['Date'] >= current_date_start)
        & (oil_x_dollar_df['Date'] < current_date_finish)
    ]

    correlation_by_years[str(current_date_start.year)] = current_year_df['dollar_rate'].corr(current_year_df['oil_price'])

    mean_value = current_year_df['oil_price_rub'].mean()
    mean_by_years[str(current_date_start.year)] = mean_value

    std_value = current_year_df['oil_price_rub'].std()
    std_by_years[str(current_date_start.year)] = std_value

    statistical_outliers_df = current_year_df[
        (current_year_df['oil_price_rub'] > mean_value + (std_value * 3))
        | (current_year_df['oil_price_rub'] < mean_value - (std_value * 3))
    ]
    statistical_outliers += statistical_outliers_df['Date'].tolist()

    current_date_start = current_date_finish
