import pandas as pd
import numpy as np


codes_df = pd.read_csv('all-geocodes-v2017.csv')
#pop_df = pd.read_csv('co-est2019-alldata.csv', sep=',', encoding='gbk')
tn_fips = 47
tn_codes = codes_df.loc[(codes_df['State Code (FIPS)'] == tn_fips)]
tn_codes = tn_codes[['County Code (FIPS)', 'Area Name (including legal/statistical area description)']].reset_index()
tn_codes.drop('index', axis=1,inplace=True)
tn_codes['County Code (FIPS)'] = tn_codes['County Code (FIPS)'].astype(str)
m = tn_codes['County Code (FIPS)'].str.len().max()
tn_codes['FIPS'] = tn_codes['County Code (FIPS)'].str.rjust(m, fillchar='0')

pop_df = pd.read_csv('co-est2019-cumchg-47.csv')
col_to_rename = pop_df.columns[2]
print(pop_df)

pop_df.rename(columns={'Unnamed: 0':'County and State', 'April 1, 2010 Estimates Base':'Apr 2010 Pop', col_to_rename:'Jul 2019 Pop', 'Number':'Change in Pop', 'Percent':'Percent Change in Pop', 'April 1, 2010 Estimates Base.1':'Apr 2010 Rank', 'July 1, 2019':'Jul 2019 Rank', 'Number.1':'Change in Rank'}, inplace=True)
pop_df.drop('Percent.1', axis=1, inplace=True)

pop_df['County'] = pop_df['County and State'].str.split(',').str[0]
pop_df['County'] = pop_df['County'].str.replace('.', '')

df = pop_df.merge(tn_codes, how='left', left_on='County', right_on='Area Name (including legal/statistical area description)')
#Give each FIPS code the tn prefix
df['County Code (FIPS)'] = df['County Code (FIPS)'].astype(str)
df['FIPS'] = '47' + df['FIPS']

print(df)


from urllib.request import urlopen
import json
import plotly.express as px
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

rank_fig = px.choropleth(df, geojson=counties, locations='FIPS', color='Jul 2019 Rank',
 color_continuous_scale="fall",
 range_color=(1, 133),
 scope="usa",
 labels={'Jul 2019 Rank':'Rank: 2019 Population'}
 )
rank_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
rank_fig.show()
