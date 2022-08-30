import pandas as pd
from tabula import read_pdf

def test_groupby(df):
  '''
  perform groupby on truncated dataset by age
  '''
  age = df.groupby('AGE').aggregate({'ANXIETYFLG':'sum','ADHDFLG':'sum','DEPRESSFLG':'sum',
                                            'SCHIZOFLG':'sum','TRAUSTREFLG':['sum','count']})
  age.columns = ['ANXIETY','ADHD','DEPRESS','SCHIZO','TRAUMA','TOTAL']
  return age

def test_scrape(df):
  '''
  scrape a pdf file
  '''
  age_doc = read_pdf('Age Doc.pdf', pages = '1')[0]
  age_doc = age_doc[['Label', 'Value']]

  return age_doc.dropna()

def test_merge(age_doc, df):
  '''
  merge the scraped data with the groupby
  '''
  age_merged = df.merge(age_doc, left_on='AGE', right_on='Value', how='left')
  age_merged = age_merged.rename(columns={'Label':'Age Range'})
  return age_merged


