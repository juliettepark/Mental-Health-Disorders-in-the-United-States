import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape():
    url = 'https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_income'
    page = requests.get(url)

    # create a beautiful soup object that can parse the HTML content
    soup = BeautifulSoup(page.content, 'html.parser')

    # get the table markup from soup object
    table = soup.select('#mw-content-text > div.mw-parser-output > table:nth-child(12)')
    cols = [ col.get_text() for col in table[0].select('tbody > tr > td') ]

    # create a list for each column, getting the text content as needed
    state = pd.Series([ cols[e+1] for e in range(0, len(cols)) if e % 13 == 0]).apply(lambda s: s[:(len(s)-1)])
                                                                                                                                                                                                        
    income_2019 = pd.Series([ cols[e+2] for e in range(0, len(cols)) if e % 13 == 0]).apply(lambda s: int((s[1:(len(s)-1)]).replace(',','')))


    d = {'State': list(state),'Avg Income 2019': income_2019}    
    income = pd.DataFrame(d)
    return income