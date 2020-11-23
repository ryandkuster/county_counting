#!/usr/bin/env python

from urllib.request import urlopen
import json
import math
import pandas as pd


def get_county():
    '''
    get county JSON
    '''
    print('getting county data')

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    return counties


def get_covid():
    '''
    get covid stats from NYT github
    '''
    print('getting covid stats')

    df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',
                       dtype={'fips': str})

    return df


def get_pop():
    '''
    get population data from census.gov
    '''
    print('getting population stats')

    pop_df = pd.read_csv('https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv',
                         encoding='gbk', dtype={'COUNTY': str, 'STATE': str})

    #pop_df.drop(pop_df.columns.difference(['POPESTIMATE2019','STATE', 'COUNTY', 'CTYNAME']), 1, inplace=True)

    a = pop_df['STATE'].str.len().max()
    b = pop_df['COUNTY'].str.len().max()
    pop_df['fips'] = pop_df['STATE'].str.rjust(a, fillchar='0') + pop_df['COUNTY'].str.rjust(b, fillchar='0')

    return pop_df


def get_election(election_file):
    '''
    get election data from local storage
    '''
    print('getting election stats')

    elec_df = pd.read_csv(election_file)

    return elec_df
