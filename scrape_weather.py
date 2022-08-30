import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape():

    url = 'http://www.usa.com/rank/us--average-temperature--state-rank.htm'
    page = requests.get(url)

    # create a beautiful soup object that can parse the HTML content
    soup = BeautifulSoup(page.content, 'html.parser')

    # get the table markup from soup object
    table = soup.select('#hcontent > table')
    cols = [ col.get_text() for col in table[0].select('tr > td') ]

    # create a list for each column, getting the text content as needed
    col1 = [ cols[e] for e in range(1, len(cols)) if e % 3 == 0]
    col2 = [ cols[(3 * e) + 1] for e in range(1, 52) ]
    col3 = [ cols[(3 * e) + 2] for e in range(1, 52) ]
    state_name = [ col.get_text() for col in table[0].select('tr > td > a') ]

    ser = pd.Series(col2)
    ser = ser.apply(lambda s: float(s[0:5]))

    d = {'Avg Temp': list(ser),'State Name': state_name}    
    weather = pd.DataFrame(d)
    return weather