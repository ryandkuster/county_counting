#!/usr/bin/env python
# coding: utf-8

from urllib.request import urlopen
import argparse
import json
import math
import matplotlib
import pandas as pd
import plotly.express as px
import sys


def parse_user_input():
    parser = argparse.ArgumentParser(description='create county stats, run w/o args to refresh data')
    parser.add_argument('-all_df', type=str, required=False, metavar='',
        help='the full or relative path to the full covid data')
    parser.add_argument('-pop_df', type=str, required=False, metavar='',
        help='the full or relative path to the census population data')
    parser.add_argument('-frame', type=str, required=False, metavar='',
        help='include only dates ending in this number')
    parser.add_argument('-state', type=str, required=False, metavar='',
        help='include only this state')

    args = parser.parse_args()

    return args


def get_county_json():
    # ## get county JSON
    print('getting county data')

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    return counties


def get_covid_stats():
    # ## get covid stats from NYT github
    print('getting covid stats')

    if args.all_df:
        all_df = pd.read_csv(args.all_df, dtype={'fips': str})
    else:
        all_df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',
                       dtype={'fips': str})
        all_df.to_csv('all_df.csv', index=False)
    print(all_df)
    return all_df


def get_population_stats():
    # ## get population data from census.gov
    print('getting population stats')

    if args.pop_df:
        pop_df = pd.read_csv(args.pop_df, dtype={'COUNTY': str, 'STATE': str})
    else:
        pop_df = pd.read_csv('https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv',
                         encoding='gbk', dtype={'COUNTY': str, 'STATE': str})
        pop_df.to_csv('pop_df.csv', index=False)

    pop_df.drop(pop_df.columns.difference(['POPESTIMATE2019','STATE', 'COUNTY', 'CTYNAME']), 1, inplace=True)

    a = pop_df['STATE'].str.len().max()
    b = pop_df['COUNTY'].str.len().max()
    pop_df['fips'] = pop_df['STATE'].str.rjust(a, fillchar='0') + pop_df['COUNTY'].str.rjust(b, fillchar='0')

    return pop_df


def covid_merge(all_df, pop_df):
    # subset the covid data from the end_date, then merge with the start_date subset
    print('merging data')

    df = all_df.merge(pop_df, how='left', left_on='fips', right_on='fips')

    return df


def transform_variables(df):
    # transform variables

    df['log10_cases'] = [math.log10(x+1) for x in df['cases']]
    df['per_1k_cases'] = ((df['cases'] / df['POPESTIMATE2019']) * 1000)
    df['log10_per_1k_cases'] = [math.log10(x+1) for x in df['per_1k_cases']]
    return df


def create_chloropleth(df, figure_var, counties):
    # ## select 'figure_var' to plot that response

    minny = min(df[figure_var])
    maxxy = max(df[figure_var])

    import plotly.express as px

    fig = px.choropleth(df, geojson=counties, locations='fips', color=figure_var,
                               #color_continuous_scale="Viridis",
                               color_continuous_scale="fall",
                               #color_continuous_scale="spectral",
                               animation_frame='date',
                               range_color=(minny, maxxy),
                               scope="usa",
                               hover_data=[figure_var,'CTYNAME','date'],
                               labels={figure_var:figure_var}
                              )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html('animation_test.html')
    fig.show()


def define_frames(df, frame):
    frames_df = df.loc[df['date'].str.endswith(frame)]
    print(frames_df)
    return frames_df


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

    all_df = get_covid_stats()
    pop_df = get_population_stats()
    df = covid_merge(all_df, pop_df)
    df = transform_variables(df)

    counties = get_county_json()
    print(df)
    if args.frame:
        df = define_frames(df, args.frame)
    figure_var = 'per_1k_cases'
    create_chloropleth(df, figure_var, counties)

