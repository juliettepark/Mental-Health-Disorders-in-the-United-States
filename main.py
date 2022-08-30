import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from tabula import read_pdf
from data_prep import DataPrep
import scrape_weather
import scrape_income


def plot_geospatial(merged_geo):
    '''
    Create a geospatial plot for each disorder
    Plot cases as both a number, and a percent
    '''
    disorders = {'ANXIETY':'Anxiety', 
                 'DEPRESS': 'Depression', 
                 'SCHIZO': 'Schizophrenia',
                 'TRAUMA': 'Trauma', 
                 'ADHD':'ADHD'}
    # loop through to create a plot for each disorder
    for (disorder, name) in disorders.items():
        # lay plots side-by-side
        fig, [ax1, ax2] = plt.subplots(1,2, figsize=(15, 5))
        merged_geo.plot(column = disorder, legend=True, ax=ax1)
        ax1.set_title('Reported Cases of ' + name + ' by State')
        

        merged_geo[disorder + '_PERCENT'] = merged_geo[disorder] / merged_geo['TOTAL']
        merged_geo.plot(column = disorder + '_PERCENT', legend=True, ax=ax2)
        ax2.set_title('Percent ' + name)
        fig.savefig(name + 'geospatial.png')


def plot_education(edu_merged):
    '''
    Create a plot showing whether education level correlates with MH disorder prevalence 
    '''
    fig, ax = plt.subplots(1)
    edu_merged.plot(kind='bar', stacked=True, ax=ax, legend=True)   
    # manually ajust labels     
    labels = ['Sp Edu', '0 to 8', '9 to 11', 'HS Diploma', 'College']
    ax.set_xticklabels(labels, fontsize=11)
    plt.xticks(rotation = 0)
    plt.legend(loc='upper left')
    plt.xlabel('Education Level')
    plt.ylabel('# of Reported Cases')
    plt.title('Education Level vs Total Number of Reported Cases')  



def plot_employment(employ_data):
    '''
    Create a plot showing whether employment correlates with MH disorder prevalence 
    '''
    # Make stacked bar-plot for easy comparison
    fig, ax = plt.subplots(1)
    employ_data.plot(kind='bar', stacked=True, ax=ax, legend=False)
    labels = ['Unemployed', 'Employed']
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel('Total Reported Cases')
    ax.set_xlabel('Employment Level')
    ax.set_title('Employment Level vs Total Number of Reported Cases')  

    plt.xticks(rotation = 0)
    plt.savefig('employment.png')
    


def plot_weather(merged_geo):
    '''
    Create a plot showing if weather correlates with mental health disorders
    '''
    # get weather data
    weather = scrape_weather.scrape()

    fig, [ax1, ax2] = plt.subplots(1,2, figsize=(12, 6))
    # correlations between weather and depression/anxiety
    merged_geo_weather = merged_geo.merge(weather, left_on='NAME', right_on='State Name', how='left')
    del merged_geo_weather['State Name']
    sns.regplot(x='Avg Temp', y='DEPRESS', data=merged_geo_weather, ax=ax1)
    sns.regplot(x='Avg Temp', y='ANXIETY', data=merged_geo_weather, ax=ax2, color='green')
    ax1.set_ylabel('Cases of Depression', labelpad = 15, fontsize=12)
    ax1.set_xlabel('Average Temperature (Degrees Fahrenheit)', labelpad = 15, fontsize=12)
    ax1.set_title('Average Temperature vs Cases of Depression')
    ax2.set_ylabel('Cases of Anxiety', labelpad = 15, fontsize=12)
    ax2.set_xlabel('Average Temperature (Degrees Fahrenheit)', labelpad = 15, fontsize=12)
    ax2.set_title('Average Temperature vs Cases of Anxiety')

    # adjust spacing between subplots
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.4)
    fig.savefig('weather.png')
    plt.clf()


def plot_income(merged_geo):
    '''
    Create plots to show correlation between mental health & income in a state
    '''
    # obtain data via webscraping
    income = scrape_income.scrape()
    # remove extra space at the beginning of each word
    income['State'] = income['State'].apply(lambda s: s[1:])
    merged_all = merged_geo.merge(income, left_on='NAME', right_on='State', how='left')
    del merged_all['State']
    disorders = {'ANXIETY':'Anxiety', 
                 'DEPRESS': 'Depression', 
                 'SCHIZO': 'Schizophrenia',
                 'TRAUMA': 'Trauma', 
                 'ADHD':'ADHD'}

    # loop through disorders to create a plot for each one
    for (disorder, name) in disorders.items():
        merged_all[disorder + '_PERCENT'] = merged_all[disorder] / merged_all['TOTAL']

        sns.regplot(x='Avg Income 2019', y=disorder, data=merged_all) 
        plt.xlabel('Average Income')
        plt.ylabel('Number of ' + name + ' Cases')
        plt.title('Number of ' + name + ' vs Average Income per State')  
        plt.savefig('income_' + name +  '_number.png')  
        plt.clf()

        sns.regplot(x='Avg Income 2019', y=disorder+'_PERCENT', data=merged_all) 
        plt.xlabel('Average Income')   
        plt.ylabel('Percentage of ' + name + ' Cases')
        plt.title('Percentage of ' + name + ' vs Average Income per State') 

        plt.savefig('income_' + name +  '_percent.png') 
        plt.clf()


def plot_age(df, age_merged):
    '''
    For each disorder, plot frequency of disorder v age
    '''
    disorders = {'ANXIETY':'Anxiety', 
                 'DEPRESS': 'Depression', 
                 'SCHIZO': 'Schizophrenia',
                 'TRAUMA': 'Trauma', 
                 'ADHD':'ADHD'}

    # loop through each disorder to create a graph for each
    for (disorder, name) in disorders.items():
        age_merged[disorder + '_PERCENT'] = age_merged[disorder] / age_merged['TOTAL']
        plt.figure(figsize=(8, 5))

        sns.barplot(x='Age Range', y=(disorder + '_PERCENT'), data=age_merged)
        plt.xticks(rotation = 90)
        plt.ylabel('Percentage of ' + name + ' Cases')
        plt.title('Percentage of ' + name + ' Cases for Each Age Group')
        plt.savefig(name + '_age.png')


def plot_education(edu_merged):
    '''
    Create plot to see if education has an influence on mental health
    Use # of each disorder
    '''
    edu_merged = edu_merged.drop(labels=5, axis=0)
    edu_merged = edu_merged.drop(labels=6, axis=0)

    fig, ax = plt.subplots(1)
    # stacked plot
    edu_merged.plot(kind='bar', stacked=True, ax=ax, legend=True)
    # manually adjust labels
    labels = ['Sp Edu', '0 to 8', '9 to 11', 'HS Diploma', 'College']
    ax.set_xticklabels(labels, fontsize=11)
    plt.xticks(rotation = 0)
    plt.legend(loc='upper left')
    plt.ylabel('# of Total Reported Cases')
    plt.title('Education Level vs Total Reported Cases')

    plt.savefig('education.png')
    plt.clf()


def plot_education_percentage(edu_merged_percent):
    '''
    Create plot to see if education has an influence on mental health
    Use % of each disorder
    '''
    edu_merged_percent = edu_merged_percent.drop(labels=5, axis=0)
    edu_merged_percent = edu_merged_percent.drop(labels=6, axis=0)

    fig, ax = plt.subplots(1)
    # make stacked plot
    edu_merged_percent.plot(kind='bar', stacked=True, ax=ax, legend=False)
    labels = ['0 to 8', '9 to 11', 'HS Diploma', 'College']
    ax.set_xticklabels(labels, fontsize=11)
    plt.xticks(rotation = 0)

    del edu_merged_percent['Frequency']
    del edu_merged_percent['%']

    plt.ylabel('Percent of Total Reported Cases')
    plt.title('Education Level vs Percent of Total Reported Cases')

    plt.savefig('education_percentages.png')
    plt.clf()


def plot_urban(merged_urb):
    '''
    Create a plot for each disorder
    Plot % urbanization vs mental health cases #s and %s
    '''

    disorders = {'ANXIETY':'Anxiety', 
                 'DEPRESS': 'Depression', 
                 'SCHIZO': 'Schizophrenia',
                 'TRAUMA': 'Trauma', 
                 'ADHD':'ADHD'}

    sns.regplot(x='UrbanPop', y='TOTAL', data=merged_urb) 
    plt.xlabel('Percent Urban Population')
    plt.ylabel('Total # of Reported Cases')
    plt.title('Urban Population vs # of Total Cases')
    plt.savefig('urban_vs_total.png')
    plt.clf()


    # loop through disorders to create a plot for each one
    for (disorder, name) in disorders.items():
        merged_urb[disorder + '_PERCENT'] = merged_urb[disorder] / merged_urb['TOTAL']
        sns.regplot(x='UrbanPop', y=disorder, data=merged_urb) 
        plt.ylabel('Cases of ' + name)
        plt.xlabel('Percent Urban Population')
        plt.title('Cases of ' + name + ' vs Percent Urban Population')
        plt.savefig('urb_' + name +  '_number.png')    
        plt.clf()

        sns.regplot(x='UrbanPop', y=disorder+'_PERCENT', data=merged_urb) 
        plt.ylabel('Percent of ' + name)
        plt.xlabel('Percent Urban Population')
        plt.title('Percent of ' + name + ' vs Percent Urban Population')
        plt.savefig('urb_' + name +  '_percent.png')    
        plt.clf()

    

def plot_crime(crime_merged):
    '''
    Create a plot for each disorder
    Plot average crime rates vs each disorder
    '''
    disorders = {'ANXIETY':'Anxiety', 
                 'DEPRESS': 'Depression', 
                 'SCHIZO': 'Schizophrenia',
                 'TRAUMA': 'Trauma', 
                 'ADHD':'ADHD'}
                 
    # loop through each disorder and make a plot
    for (disorder, name) in disorders.items():
        crime_merged[disorder + '_PERCENT'] = crime_merged[disorder] / crime_merged['TOTAL']

        sns.regplot(x='Crime Rate', y=disorder, data=crime_merged) 
        plt.ylabel('Cases of ' + name)
        plt.xlabel('Crime Rate')
        plt.title('Total Cases of ' + name + ' vs Crime Rate')
        plt.savefig('crime_' + name +  '_number.png')  
        plt.clf()

        sns.regplot(x='Crime Rate', y=disorder+'_PERCENT', data=crime_merged) 
        plt.savefig('crime_' + name +  '_percent.png')    
        plt.ylabel('Percent of ' + name)
        plt.xlabel('Crime Rate')
        plt.title('Percent of ' + name + ' vs Crime Rate')
        plt.clf()


def main():
    data = DataPrep(pd.read_csv('mhcld-puf-2019-csv.csv'))

    # main mental health dataset
    df = data.clean_df()
    
    # merge main data with shp file
    geodata_merged = data.join_data_geo(data.groupby_state(df))

    # get data for and plot demographic factors 
    age_merged = data.age_data(df)
    plot_age(df, age_merged)
    employment_data = data.employment_data(df)
    plot_employment(employment_data)

    education_data = data.groupby_education(df)
    plot_education(education_data)

    education_data_percent = data.education_percentage(df)
    plot_education_percentage(education_data_percent)

    # get data for and plot geographic data
    plot_geospatial(geodata_merged)
    plot_weather(geodata_merged)

    # get data for and plot economic factors
    plot_income(geodata_merged)

    urb_data = data.load_urb_data(geodata_merged)
    plot_urban(urb_data)

    crime = data.crime_data(urb_data)
    plot_crime(crime)


if __name__ == '__main__':
    main()