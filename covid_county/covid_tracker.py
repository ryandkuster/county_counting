#!/usr/bin/env python
# coding: utf-8

from urllib.request import urlopen
import argparse
import json
import math
import matplotlib
import pandas as pd
import plotly.express as px


def parse_user_input():
    parser = argparse.ArgumentParser(description='create county stats')
    parser.add_argument('-df', type=str, required=False, metavar='',
        help='the full or relative path to the fips county covid data')
    parser.add_argument('-start', type=str, required=False, metavar='',
        help='starting date for covid tracking, e.g., 2020-11-11')
    parser.add_argument('-end', type=str, required=False, metavar='',
        help='ending date for covid tracking, e.g., 2020-11-18')
    args = parser.parse_args()

    return args


def get_county_json():
    # ## get county JSON
    print('getting county data')

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    return counties


def get_covid_stats(start_date):
    # ## get covid stats from NYT github
    print('getting covid stats')

    all_df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',
                       dtype={'fips': str})
    colnames = list(all_df)
    start_df = pd.DataFrame(columns=colnames)
    start_df = all_df.loc[all_df['date'] == start_date]

    return all_df, start_df


def get_population_stats():
    # ## get population data from census.gov
    print('getting population stats')

    pop_df = pd.read_csv('https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv',
                         encoding='gbk', dtype={'COUNTY': str, 'STATE': str})

    pop_df.drop(pop_df.columns.difference(['POPESTIMATE2019','STATE', 'COUNTY', 'CTYNAME']), 1, inplace=True)

    a = pop_df['STATE'].str.len().max()
    b = pop_df['COUNTY'].str.len().max()
    pop_df['fips'] = pop_df['STATE'].str.rjust(a, fillchar='0') + pop_df['COUNTY'].str.rjust(b, fillchar='0')

    return pop_df


#def covid_difference_merge(start_date, end_date, start_df, all_df):
#    # subset the covid data from the end_date, then merge with the start_date subset
#    print('crunching data')
#
#    end_df = all_df.loc[all_df['date'] == end_date]
#    df = start_df.merge(end_df, how='left', left_on='fips', right_on='fips')
#    df['new_cases'] = (df['cases_y'] - df['cases_x'])
#    df['new_deaths'] = (df['deaths_y'] - df['deaths_x'])
#
#    return df


def covid_difference_merge(start_date, end_date, start_df, all_df):
    # subset the covid data from the end_date, then merge with the start_date subset
    print('crunching data')

    end_df = all_df.loc[all_df['date'] == end_date]
    df = start_df.merge(end_df, how='inner', left_on='fips', right_on='fips')
    df['new_cases'] = (df['cases_y'] - df['cases_x'])
    df['new_deaths'] = (df['deaths_y'] - df['deaths_x'])

    return df


def transform_variables(df, pop_df):
    # transform variables

    df['sqrt_cases_x'] = [math.sqrt(x) for x in df['cases_x']]
    df['log10_cases_x'] = [math.log10(x+1) for x in df['cases_x']]
    df['log10_new_cases'] = [math.log10(x+1) if x >= 0 else -1 * math.log10(abs(x)) for x in df['new_cases']]
    df['log10_new_deaths'] = [math.log10(x+1) if x >= 0 else -1 * math.log10(abs(x)) for x in df['new_deaths']]

    # merge the dataframe with the population dataset for normalization (per capita) estimates
    df = df.merge(pop_df, how='left', left_on='fips', right_on='fips')
    df['per_1k_cases_x'] = ((df['cases_x'] / df['POPESTIMATE2019']) * 1000)
    df['per_1k_new_cases'] = ((df['new_cases'] / df['POPESTIMATE2019']) * 1000)
    df['per_1k_new_deaths'] = ((df['new_deaths'] / df['POPESTIMATE2019']) * 1000)

    df['log10_per_1k_cases_x'] = [math.log10(x+1) for x in df['per_1k_cases_x']]
    df['log10_per_1k_new_cases'] = [math.log10(x+1) if x >= 0 else -1 * math.log10(abs(x)) for x in df['per_1k_new_cases']]
    df['log10_per_1k_new_deaths'] = [math.log10(x+1) if x >= 0 else -1 * math.log10(abs(x)) for x in df['per_1k_new_deaths']]
    return df


def create_chloropleth(df, figure_var, counties):
    # ## select 'figure_var' to plot that response

    minny = min(df[figure_var])
    maxxy = max(df[figure_var])

    import plotly.express as px

    fig = px.choropleth(df, geojson=counties, locations='fips', color=figure_var,
                               color_continuous_scale="Viridis",
                               range_color=(minny, maxxy),
                               scope="usa",
                               labels={figure_var:figure_var}
                              )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html('test.html')
    fig.show()


def check_variable_spread():
    # optional, better for EDA

    df['per_1k_cases_x'].hist()
    df['log10_per_1k_cases_x'].hist()
    df['cases_x'].hist()
    df['sqrt_cases_x'].hist()
    df['log10_cases_x'].hist()
    df['new_cases'].hist()
    df['log10_new_cases'].hist()
    df['new_deaths'].hist()
    df['log10_new_deaths'].hist()


if __name__ == '__main__':

    args = parse_user_input()

    start_date = args.start if args.start else '2020-11-11' # e.g., 2020-11-11 is the Nashville CMA...
    end_date = args.end if args.end else '2020-11-18'

    if not args.df:
        all_df, start_df = get_covid_stats(start_date)
        pop_df = get_population_stats()
        df = covid_difference_merge(start_date, end_date, start_df, all_df)
        df = transform_variables(df, pop_df)
        df.to_csv('test.csv')
    else:
        df = pd.read_csv(args.df)

    counties = get_county_json()
    print(df)

    figure_var = 'log10_per_1k_new_cases'
    create_chloropleth(df, figure_var, counties)

