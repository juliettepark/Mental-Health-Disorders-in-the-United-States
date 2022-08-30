import our_code_tests
import tabula
import pandas as pd
from cse163_utils import assert_equals


def main():
    # load truncated dataset
    df = pd.read_csv('Testing File Mental Health.csv').loc[0:10, :]

    # test pdf scraping
    scraped = our_code_tests.test_scrape(df)[['Label']]
    # manually calculated values
    scrape_expected = ['0–11 years', '12–14 years', '15–17 years', '18–20 years', '21–24 years', '25–29 years','30–34 years', '35–39 years', '40–44 years', '45–49 years', '50–54 years', '55–59 years', '60–64 years', '65 years and older', 'Missing/unknown/not collected/invalid'] 

    # test merging
    merged = our_code_tests.test_merge(our_code_tests.test_scrape(df), df)[['Age Range']]
    # manually calculated values
    age_expected = ['Missing/unknown/not collected/invalid', '65 years and older', '55–59 years', '45–49 years', '12–14 years', '30–34 years', '12–14 years', '35–39 years', '30–34 years', '45–49 years', '45–49 years']
    
    # test groupby
    groupby = df.groupby('AGE')['GENDER'].count()
    # manually calculated values
    groupby_expected = [1, 2, 2, 1, 3, 1, 1]


    # run tests
    # if nothing prints, tests pass!
    assert_equals(age_expected, list(merged['Age Range']))
    assert_equals(scrape_expected, list(scraped['Label']))
    assert_equals(groupby_expected, list(groupby))


if __name__ == '__main__':
    main()