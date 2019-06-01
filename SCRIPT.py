
import pandas as pd
import numpy as np
import matplotlib as plt
pd.options.display.float_format = '{:,}'.format
pd.options.mode.chained_assignment = None
# The following script reads 3 datasets;
# (Energy Indicators.xls, world_bank.csv, and scimagojr-3.xlsx),
# and merges them in order of rank based on their journal contributions
# to Energy Engineering and Power Technology publications.
# Energy data is in 'Gigajoules'


energy = (pd.read_excel('Energy Indicators.xls', skiprows = 17, skipfooter = 38)).drop(['Unnamed: 0', 'Unnamed: 1'], axis = 1)
energy.columns = ['Country', 'Energy Supply', 'Energy Supply per Capita', '% Renewable']
energy = energy.replace('...', np.nan)
energy['Country'] = energy['Country'].str.replace('\d+', '')
energy['Country'] = energy['Country'].str.replace(r" \(.*\)","")
energy = energy.replace('Republic of Korea', 'South Korea')
energy = energy.replace('United States of America', 'United States')
energy = energy.replace('United Kingdom of Great Britain and Northern Ireland', 'United Kingdom')
energy = energy.replace('China, Hong Kong Special Administrative Region', 'Hong Kong')
energy['Energy Supply'] = energy['Energy Supply'] * 1000000

GDP = pd.read_csv('world_bank.csv', skiprows = 4)
GDP = GDP.replace('Korea, Rep.', 'South Korea')
GDP = GDP.replace('Iran, Islamic Rep.', 'Iran')
GDP = GDP.replace('Hong Kong SAR, China', 'Hong Kong')

ScimEn = pd.read_excel('scimagojr-3.xlsx')

dataset1 = pd.merge(ScimEn, energy, how='inner', left_on=['Country'], right_on=['Country'])
dataset2 = pd.merge(dataset1, GDP, how='inner', left_on=['Country'], right_on=['Country Name']).set_index('Country')

data_main = dataset2[['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index',
                      'Energy Supply', 'Energy Supply per Capita', '% Renewable',
                      '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]


def main_dataset():

    return data_main.iloc[:15]


main_dataset()

# The following function returns the number of lost entries due to the merge;


def lost_entries():
    merge1 = pd.merge(ScimEn, energy, how='inner', left_on=['Country'], right_on=['Country'])
    merge2 = pd.merge(ScimEn, GDP, how='inner', left_on=['Country'], right_on=['Country Name'])
    merge3 = pd.merge(energy, GDP, how='inner', left_on=['Country'], right_on=['Country Name'])

    tot_entries = len(energy) + len(GDP) + len(ScimEn)
    lost_entries = tot_entries - len(merge1) - len(merge2) - len(merge3)

    return lost_entries


lost_entries()

# The following function returns the average GDP of the Top 15 countries
# ordered from highest to lowest


def avg_GDP():
    Top15 = main_dataset()
    data = Top15[['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]
    avgGDP = pd.Series(data.mean(axis = 1), name = 'avgGDP')

    return avgGDP.sort_values(ascending = False)


avg_GDP()

# The following function returns the change in GDP between 2006-2015 for
# the country with the 6th highest average GDP


def GDP_change():
    Top15 = main_dataset()
    avgGDP = avg_GDP()
    GDP_6th = avgGDP[5]
    country = avgGDP[avgGDP == GDP_6th].index[0]
    GDP_change = Top15.loc[country]['2015'] - Top15.loc[country]['2006']

    return GDP_change


GDP_change()

# The following function returns the average energy supply per Capita


def avg_energy():
    Top15 = main_dataset()
    data = Top15['Energy Supply per Capita']
    avg_energy = np.mean(data)

    return avg_energy


avg_energy()

# The following function returns the country with the highest energy generation
# from renewables, expressed as a % of total energy supply


def highest_ren():
    Top15 = main_dataset()
    data = Top15['% Renewable']
    max_renewable = np.max(data)
    country = Top15[Top15['% Renewable'] == max_renewable].iloc[0].name
    perc_ren = Top15[Top15['% Renewable'] == max_renewable].loc['Brazil', '% Renewable']
    return country, perc_ren


highest_ren()

# The following function returns the country with the highest ratio
# of Self-Citations to Total Citations


def citation_ratio():
    Top15 = main_dataset()
    data = Top15[['Citations', 'Self-citations']]
    data['ratio'] = data['Self-citations'] / data['Citations']
    max_citation_ratio = np.max(data['ratio'])
    country = data[data['ratio'] == max_citation_ratio].iloc[0].name
    ratio = data[data['ratio'] == max_citation_ratio].loc['China', 'ratio']
    return country, ratio


citation_ratio()

# The following function estimates the population using the Energy supply
# and Energy per Capita data. It then returns the 3rd most populous country
# according to this.


def PopEst3():
    Top15 = main_dataset()
    data = Top15[['Energy Supply', 'Energy Supply per Capita']]
    data['Population Estimate'] = data['Energy Supply'] / data['Energy Supply per Capita']
    data = data.sort_values(['Population Estimate'], ascending = False)
    pop3 = data.iloc[2].name

    return pop3


PopEst3()

# The following function returns the correlation between Energy supply
# per capita and citable documents per capita


def EnC_corr():
    Top15 = main_dataset()
    data = Top15[['Energy Supply', 'Energy Supply per Capita', 'Citable documents']]
    data['PopEst'] = data['Energy Supply'] / data['Energy Supply per Capita']
    data = data.sort_values(['PopEst'], ascending = False)
    data['Citable docs per Capita'] = data['Citable documents'] / data['PopEst']
    data = data[['Energy Supply per Capita', 'Citable docs per Capita']]
    en_cit_corr = data['Energy Supply per Capita'].corr(data['Citable docs per Capita'], method = 'pearson')
    return en_cit_corr


EnC_corr()

# The following function plots the correlation calculated above


def plot_corr():
    get_ipython().magic('matplotlib inline')

    Top15 = main_dataset()
    Top15['PopEst'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    Top15['Citable docs per Capita'] = Top15['Citable documents'] / Top15['PopEst']
    return Top15.plot(x='Citable docs per Capita', y='Energy Supply per Capita', kind='scatter', xlim=[0, 0.0006])


plot_corr()

# The following function evaluates the median % Renewables for each country,
# creates a new column 'HighRenew' and assigns a 1 for countries with
# % Renewables at or above the median and 0 for those below the median


def ren_median():
    Top15 = main_dataset()
    ren_median = np.median(Top15['% Renewable'])
    Top15['HighRenew'] = None
    for country in range(len(Top15)):
        if Top15.iloc[country, 9] >= ren_median:
            Top15.iloc[country, 20 ] = 1
        else: Top15.iloc[country, 20] = 0

    return pd.Series(Top15['HighRenew'], dtype='int64')


ren_median()

# The following function groups the countries by continent, then returns
# a table illustrating the number of countries in each continent,
# the sum, mean, and std deviation for the estimated population of each country


def group_summary():
    Top15 = main_dataset()
    ContinentDict  = {'China': 'Asia',
                  'United States': 'North America',
                  'Japan': 'Asia',
                  'United Kingdom': 'Europe',
                  'Russian Federation': 'Europe',
                  'Canada': 'North America',
                  'Germany': 'Europe',
                  'India': 'Asia',
                  'France': 'Europe',
                  'South Korea': 'Asia',
                  'Italy': 'Europe',
                  'Spain': 'Europe',
                  'Iran': 'Asia',
                  'Australia': 'Australia',
                  'Brazil': 'South America'}
    Top15['Continent'] = None
    Top15['size'] = None
    Top15['PopEst'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']

    for i in range(len(Top15)):
        Top15.iloc[i,20] = ContinentDict[Top15.index[i]]
    summary = Top15.set_index('Continent').groupby(level=0)['PopEst'].agg(['size', 'sum', 'mean', 'std'])
    return summary


group_summary()

# The following function groups the countries according to continents,
# and 5 % Renewables categories, showing the number of countries in each


def ren_categories():
    Top15 = main_dataset()
    ContinentDict  = {'China':'Asia',
                  'United States':'North America',
                  'Japan':'Asia',
                  'United Kingdom':'Europe',
                  'Russian Federation':'Europe',
                  'Canada':'North America',
                  'Germany':'Europe',
                  'India':'Asia',
                  'France':'Europe',
                  'South Korea':'Asia',
                  'Italy':'Europe',
                  'Spain':'Europe',
                  'Iran':'Asia',
                  'Australia':'Australia',
                  'Brazil':'South America'}
    Top15['Continent'] = None
    Top15['size'] = None

    for i in range(len(Top15)):
        Top15.iloc[i, 20] = ContinentDict[Top15.index[i]]

    Top15['% Renewable'] = pd.cut(Top15['% Renewable'], 5)
    return Top15.groupby(['Continent', '% Renewable']).size()


ren_categories()

# The following function formats floating point numbers to contain comma
# separators for thousands
# NOTE:- lamda function only required if 'pd.options.display.float_format = '{:,}'.format'
# is not explicitly stated at the start of script


def comma_1000separator():
    Top15 = main_dataset()
    Top15['PopEst'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    PopEst = Top15.apply(lambda x: "{:,}".format(x['PopEst']), axis=1)
    return pd.Series(PopEst, name = 'PopEst')


comma_1000separator()

# The following function plots a bubble chart showing % Renewable vs. Rank.


def plot_chart():
    get_ipython().magic('matplotlib inline')
    Top15 = main_dataset()
    ax = Top15.plot(x='Rank', y='% Renewable', kind='scatter',
                    c=['#e41a1c','#377eb8','#e41a1c','#4daf4a','#4daf4a','#377eb8','#4daf4a','#e41a1c',
                       '#4daf4a','#e41a1c','#4daf4a','#4daf4a','#e41a1c','#dede00','#ff7f00'],
                    xticks=range(1,16), s=6*Top15['2014']/10**10, alpha=.75, figsize=[16,6]);

    for i, txt in enumerate(Top15.index):
        ax.annotate(txt, [Top15['Rank'][i], Top15['% Renewable'][i]], ha='center')

    print("This is a bubble chart showing % Renewable vs. Rank.")
    print("The size of the bubble corresponds to the countries' 2014 GDP, and the color corresponds to the continent.")


plot_chart()
