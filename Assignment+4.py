
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[ ]:

import pandas as pd
import numpy as np
import os
from scipy.stats import ttest_ind
os.chdir('D:\Study\OneDrive - The University of Texas at Dallas\Summer 1\py4e')

# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - 
# you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/)
# to find functions or methods you might not have used yet, or ask questions on
# [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course,
# the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June,
# Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two 
# consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the
# total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions.
# Run a t-test to compare the ratio of the mean price of houses in university towns the
# quarter before the recession starts compared to the recession bottom.
# (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is 
# housing data for the United States. In particular the datafile for [all homes at a city level]
# (http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), 
# ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States]
# (https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been
#  copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time]
# (http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars
# (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```.
# For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of `run_ttest()`, which is worth 50%.

# In[ ]:

# Read files
zh = pd.read_csv('City_Zhvi_AllHomes.csv', header=0)

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
    
data = []
state = None
state_towns = []
''' with open('test.txt') as f:
    for line in f:
        thisLine = line[:-1]
        print("start of line     " + thisLine)
        print("0")
        if thisLine[-6:] == '[edit]':
            print("state is " + thisLine[:-6])
            print("1")
            continue
        if '(' in line:
                print("city is " + thisLine[:thisLine.index('(')-1])
                print("2")
        else:
                print("else statement " + thisLine)
                print("4") '''

# In[ ]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    state_towns = []
    state = None
    data = []
    with open('university_towns.txt') as f:
        for line in f:
            thisLine = line[:-1]
            if thisLine[-6:] == '[edit]':
                state = thisLine[:-6]
                continue
            if '(' in line:
                region = thisLine[:thisLine.index('(')-1]
                state_towns.append([state,region])
            else:
                region = thisLine
                state_towns.append([state,region])
            data.append(thisLine)
    df = pd.DataFrame(state_towns,columns = ['State','RegionName'])
    return df

get_list_of_university_towns()


# In[ ]:



def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdp = pd.read_excel('gdplev.xls', header = 0, skiprows =219, skip_footer = 0, usecols = [4,5,6])
    gdp.columns = ['qtr', 'gdp', 'chain']
    gdp['gdp_diff'] = gdp.gdp-gdp.gdp.shift(1)
    temp = gdp[(gdp['gdp_diff'] < 0) & (gdp['gdp_diff'].shift(1) < 0)].iloc[0].name-2
    return gdp.iloc[temp].qtr
get_recession_start()

# In[ ]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    gdp = pd.read_excel('gdplev.xls', header = 0, skiprows =219, skip_footer = 0, usecols = [4,5,6])
    gdp.columns = ['qtr', 'gdp', 'chain']
    gdp['gdp_diff'] = gdp.gdp-gdp.gdp.shift(1)
    temp = gdp[(gdp['gdp_diff'] > 0) & (gdp['gdp_diff'].shift(1) > 0) & (gdp['gdp_diff'].shift(2) < 0) & (gdp['gdp_diff'].shift(3) < 0) ].iloc[0].name
    return gdp.iloc[temp].qtr
get_recession_end()

# In[ ]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdp = pd.read_excel('gdplev.xls', header = 0, skiprows =219, skip_footer = 0, usecols = [4,5,6])
    gdp.columns = ['qtr', 'gdp', 'chain']
    gdp['gdp_diff'] = gdp.gdp-gdp.gdp.shift(1)
    temp_st = gdp[(gdp['gdp_diff'] < 0) & (gdp['gdp_diff'].shift(1) < 0)].iloc[0].name-2
    temp_end = gdp[(gdp['gdp_diff'] > 0) & (gdp['gdp_diff'].shift(1) > 0) & (gdp['gdp_diff'].shift(2) < 0) & (gdp['gdp_diff'].shift(3) < 0) ].iloc[0].name
    rec = gdp.iloc[temp_st:temp_end,]
    return rec.loc[rec['gdp'].argmin()].qtr
get_recession_bottom()

# In[ ]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    # * From the [Zillow research data site](http://www.zillow.com/research/data/) there is 
    # housing data for the United States. In particular the datafile for [all homes at a city level]
    # (http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), 
    # ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    housing = pd.read_csv('City_Zhvi_AllHomes.csv', header=0)
    states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
    housing['State'] = housing['State'].map(states)
    housing = housing.set_index(["State","RegionName"])
    housing_qtr = (housing.iloc[:,5:].groupby(pd.PeriodIndex(housing.iloc[:,5:].columns, freq='Q'), axis=1).mean().round(2).rename(columns=lambda c: str(c).lower()))
    housing_qtr.columns.get_loc('2000q1')
    housing_qtr = housing_qtr.iloc[:,15:]
    
    housing.head(1)
    housing_qtr.head(1)
    return housing_qtr
convert_housing_data_to_quarters()
convert_housing_data_to_quarters().loc["Texas"].loc["Austin"].loc["2010q3"]

# In[ ]:

convert_housing_data_to_quarters().loc[[('Ohio','Akron'),('Ohio','Dayton')]].loc[:,['2010q3','2015q2','2016q4']]

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    housing = convert_housing_data_to_quarters().copy()
    rec_st = get_recession_start()
    rec_bt = get_recession_bottom()
    rec_en = get_recession_end()
    temp1 = housing.copy().loc[:,rec_st:rec_bt]
    # (`price_ratio=quarter_before_recession/recession_bottom`)
    temp1['price_ratio']=temp1[rec_st].div(temp1[rec_bt])

#    temp1['uni'] = 0
    uni = get_list_of_university_towns()
    uni['uni'] = 1
#   uni = set(uni)
    temp1.head(1)
    temp1 = temp1.reset_index()
    '''    temp1['uni'] = (temp1['RegionName'].isin(uni['RegionName']) & temp1['State'].isin(uni['State']))
    temp1['uni'] = np.where(temp1['uni'] == True, 1, 0)
    temp1['uni'].sum()
    
    temp1['uni'] = (temp1['RegionName'].isin(uni['RegionName']))
    temp1['uni'] = np.where(temp1['uni'] == True, 1, 0) '''
    
    temp2 = pd.merge(temp1, uni,  how='left', left_on=['RegionName','State'], right_on = ['RegionName','State'])
    temp2.head(1)
    temp2['uni'] = temp2['uni'].fillna(0)  
    
    uni_towns = temp2[temp2['uni']==1]#.dropna()
    uni_towns_not = temp2[temp2['uni']==0]
    
    
    if uni_towns_not['price_ratio'].mean() > uni_towns['price_ratio'].mean():
        better = 'university town'
    else:
        better = 'non-university town'
    better
    
    p_val = list(ttest_ind(uni_towns_not['price_ratio'], uni_towns['price_ratio'], nan_policy='omit'))[1]/2
    
    return ((p_val<0.01),p_val,better)
run_ttest()


