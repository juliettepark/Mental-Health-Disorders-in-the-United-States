import pandas as pd
import os
import pickle
from tabula import read_pdf
import geopandas as gpd


class DataPrep:
    def __init__(self, df):
        self._df = df


    def clean_df(self):
        '''
        Loads mental health data, drops missing, renames cols
        '''
        # Drop missing values
        self._df = self._df.dropna()
        # Rename columns with weird names
        self._df = self._df.rename(columns={'SPHSERVICE': 'PSYCH HOSP', 'CMPSERVICE': 'COMM MENTAL HEALTH CENTER'})
        self._df = self._df.rename(columns={'OPISERVICE': 'PSYCH INPATIENT', 'RTCSERVICE': 'RES TREATMENT', 'IJSSERVICE': 'JUSTICE SYSTEM'})
        self._df = self._df.rename(columns={'MH1': 'DIAGNOSIS 1', 'MH2': 'DIAGNOSIS 2', 'MH3': 'DIAGNOSIS 3', 'SAP': 'SUBSTANCE PROBLEM'})
        self._df = self._df.rename(columns={'DETNLF': 'NOT LABOR FORCE', 'LIVARAG': 'RESIDENTIAL STATUS', 'NUMMHS': 'DIAGNOSES NUM'})
        
        return self._df


    def scrape(self, pdf):
        '''
        uses tabula library
        scrapes tables from pdfs
        getting info out of metadata to join to df
        '''
        data = read_pdf(pdf, pages = '1')
        return data[0]


    def join_data_geo(self, states):
        '''
        scrapes state names from metadata pdf
        joins state names with mental health data
        '''
        # scrape both pages of metadata doc to get state names
        states_pg_1 = self.scrape('StatesP1.pdf')
        states_pg_2 = self.scrape('States Doc Page 2.pdf')
        # join two tables together
        states_id = pd.concat([states_pg_1, states_pg_2], ignore_index=True, axis=0)
        states_id = states_id[['Value', 'Label']]
        gdf = self.geospatial()

        # merge the scraped data, the mental health data, and the geo data
        merged_step1 = states.merge(states_id, left_on='STATEFIP', right_on='Value', how='left')
        merged_geo = merged_step1.merge(gdf, left_on='Label', right_on='NAME', how='left')
        merged_geo = gpd.GeoDataFrame(merged_geo, geometry='geometry').dropna()
        merged_geo = merged_geo[(merged_geo['NAME'] != 'Alaska') & (merged_geo['NAME'] != 'Hawaii')]
        del merged_geo['Label']
        del merged_geo['Value']
        return merged_geo


    def marital_data(self, df):
        '''
        Scrapes marital status info from metadata
        groups by age, merges data together
        '''
        # scrape age data
        mar = self.scrape('marstat.pdf')
        mar = mar[['Value', 'Label']]
        # drop missing
        mar = mar.drop(labels=4, axis=0)

        # groupby marital status
        marital_groupby = df.groupby('MARSTAT').aggregate({'ANXIETYFLG':'sum','ADHDFLG':'sum','DEPRESSFLG':'sum',
                                                    'SCHIZOFLG':'sum','TRAUSTREFLG':['sum','count']})
        marital_groupby.columns = ['ANXIETY','ADHD','DEPRESS','SCHIZO','TRAUMA','TOTAL']
        # merge groupby with scraped
        mar_merged = mar.merge(marital_groupby, left_on='Value', right_on='MARSTAT', how='left')
    
        disorders = {'ANXIETY':'Anxiety', 
                 'DEPRESS': 'Depression', 
                 'SCHIZO': 'Schizophrenia',
                 'TRAUMA': 'Trauma', 
                 'ADHD':'ADHD'}

        # for each disorder, calculate the percent it makes up of the total caseload
        for (disorder, name) in disorders.items():
            mar_merged[disorder + '_PERCENT'] = mar_merged[disorder] / mar_merged['TOTAL']
            del mar_merged[disorder]
        del mar_merged['TOTAL']
        del mar_merged['Value']

        return mar_merged


    def age_data(self,df):
        '''
        scrape age metadata
        group dataset by age
        join data together
        '''
        # group main dataset by Age
        age =df.groupby('AGE').aggregate({'ANXIETYFLG':'sum','ADHDFLG':'sum','DEPRESSFLG':'sum',
                                                'SCHIZOFLG':'sum','TRAUSTREFLG':['sum','count']})
        # flatten multi-index
        age.columns = ['ANXIETY','ADHD','DEPRESS','SCHIZO','TRAUMA','TOTAL']

        # scrape age metadata
        age_doc = self.scrape('age.pdf')
        age_doc = age_doc[['Value', 'Label']]

        age_merged = age.merge(age_doc, left_on='AGE', right_on='Value', how='left')
        # Dropped the first row, for which age was "missing or unspecified"
        age_merged = age_merged.drop(labels=0, axis=0)
        age_merged = age_merged.rename(columns={'Label':'Age Range'})
        return age_merged


    def employment_data(self, df):
        '''
        scrape employment metadata
        groupby emoloyment status
        '''
        # scrape metadata
        employ = self.scrape('employment.pdf')

        # groupby employment
        employed_merge = df.groupby('EMPLOY').aggregate({'ANXIETYFLG':'sum','ADHDFLG':'sum','DEPRESSFLG':'sum',
                                              'SCHIZOFLG':'sum','TRAUSTREFLG':['sum','count']})
        employed_merge.columns = ['ANXIETY','ADHD','DEPRESS','SCHIZO','TRAUMA','TOTAL']
        employ = employ.merge(employed_merge, right_on='EMPLOY', left_on='Value', how='left')

        # filter dataframe to only include 'employed' status
        employed = employ[(employ['Label'] == 'Full-time') | (employ['Label'] == 'Part-time') | (employ['Label'] == 'Employed full-time/part-time not differentiated')]
        # add new column to indicate 'employed'
        employed['Employed'] = True
        # filter dataframe to include 'unemployed' status
        unemployed = employ[(employ['Label'] == 'Unemployed')]
        unemployed['Employed'] = False
        # concatenate both dfs
        emp_final = pd.concat([employed, unemployed], ignore_index=True, axis=0)
        # resulting data has two rows - one for employed and one for unemployed
        emp_final = emp_final.groupby('Employed').aggregate({'ANXIETY':'sum','ADHD':'sum','DEPRESS':'sum',
                                                    'SCHIZO':'sum','TRAUMA':'sum'})
        return emp_final


    def groupby_education(self, df):
        '''
        group data by education for plotting
        scrape metadata and join to main data
        '''
        educ = self.scrape('education.pdf')
        # groupby education 
        education_groupby = df.groupby('EDUC').aggregate({'ANXIETYFLG':'sum','ADHDFLG':'sum','DEPRESSFLG':'sum',
                                              'SCHIZOFLG':'sum','TRAUSTREFLG':['sum','count']})
        # flatten multiindex 
        education_groupby.columns = ['ANXIETY','ADHD','DEPRESS','SCHIZO','TRAUMA','TOTAL']

        edu_merged = educ.merge(education_groupby, left_on='Value', right_on='EDUC', how='left')
        # delete unecessary columns
        del edu_merged['Value']
        del edu_merged['Frequency']
        del edu_merged['%']
        del edu_merged['TOTAL']

        return edu_merged


    def load_urb_data(self, merged_geo):
        '''
        read a csv file with urbanization data
        filter to include relevant columns
        rename columns
        '''
        urb = pd.read_csv('US_violent_crime.csv')
        urb = urb.rename(columns={'Unnamed: 0': 'State'})[['State', 'UrbanPop']]
        merged_urb = merged_geo.merge(urb, left_on='NAME', right_on='State', how='left')
        return merged_urb


    def education_percentage(self, df):
        '''
        Groupby education
        Process data to allow plotting by percentage
        '''
        # scrape metadata to get categorical labels
        educ_levels = self.scrape('education.pdf')
        # groupby education levels
        education_groupby = df.groupby('EDUC').aggregate({'ANXIETYFLG':'sum','ADHDFLG':'sum','DEPRESSFLG':'sum',
                                              'SCHIZOFLG':'sum','TRAUSTREFLG':['sum','count']})
        # flatten multiindex by renaming columns
        education_groupby.columns = ['ANXIETY','ADHD','DEPRESS','SCHIZO','TRAUMA','TOTAL']
        # create dict with disorder names to make it easy to loop through 
        disorders = disorders = {'ANXIETY':'Anxiety', 
                 'DEPRESS': 'Depression', 
                 'SCHIZO': 'Schizophrenia',
                 'TRAUMA': 'Trauma', 
                 'ADHD':'ADHD'}

        # merge groupby with the scraped labels
        edu_merged_percent = educ_levels = self.scrape('education.pdf').merge(education_groupby, left_on='Value', right_on='EDUC', how='left')
        # for each disorder, add a column computing % of total caseload
        for (disorder, name) in disorders.items():
            edu_merged_percent[disorder + '_PERCENT'] = edu_merged_percent[disorder] / edu_merged_percent['TOTAL']
            del edu_merged_percent[disorder]
        # delete unnecessary columns
        del edu_merged_percent['Value']
        del edu_merged_percent['TOTAL']
        edu_merged_percent = edu_merged_percent.drop(labels=0, axis=0)
        
        return edu_merged_percent


    def groupby_state(self,df):
        '''
        group main dataframe by state
        results in a dataset with 50ish rows
        '''
        states =df.groupby('STATEFIP').aggregate({'ANXIETYFLG':'sum','ADHDFLG':'sum','DEPRESSFLG':'sum',
                                              'SCHIZOFLG':'sum','TRAUSTREFLG':['sum','count']})
        states.columns = ['ANXIETY','ADHD','DEPRESS','SCHIZO','TRAUMA','TOTAL']
        return states


    def geospatial(self):
        '''
        read and filter geodata
        remove alaska and hawaii for graph purposes
        '''
        gdf = gpd.read_file('united_states.json')
        country = gdf[(gdf['NAME'] != 'Alaska') & (gdf['NAME'] != 'Hawaii')]
        gdf = gdf[['NAME', 'geometry']]
        return gdf

    def crime_data(self, merged_urb):
        '''
        load dataset with info about crime
        filter data to include necessary columns
        join it to main dataset
        '''
        crime = pd.read_csv('state_crime.csv')
        crime['Crime Rate'] = crime['Data.Rates.Property.All'] + crime['Data.Rates.Violent.All']
        crime['Crimes Number'] = crime['Data.Totals.Property.All'] + crime['Data.Totals.Violent.All']
        crime = crime[['State', 'Year', 'Crime Rate', 'Crimes Number']]
        crime = crime[crime['Year'] == 2019]

        crime_merged = merged_urb.merge(crime, left_on='NAME', right_on='State', how='left')
        
        return crime_merged
    



    