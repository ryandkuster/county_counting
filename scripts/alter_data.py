#!/usr/bin/env python

import pandas as pd


def merge_dfs(left_df, right_df, left_var, right_var):
    '''
    subset the covid data from the end_date, then merge with the start_date subset
    '''
    print('merging data')

    df = left_df.merge(right_df, how='outer', left_on=left_var, right_on=right_var)

    return df
