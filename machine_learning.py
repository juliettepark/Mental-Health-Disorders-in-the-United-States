import pandas as pd
from tabula import read_pdf
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def scrape_tables():
    """
    Scrape each table in each of the 6 documentation pdfs.
    This will match the code to its string equivlent.
    Put this in a list of tables to merge with the mental health dataset.
    """
    scraped_tables = list()

    # make a list of the pdf names.
    # utilize a list. the only difference is the pdf name so pass in each one.
    file_names = ['region.pdf', 'marstat.pdf', 'race.pdf', 'education.pdf', 'employment.pdf', 'age.pdf']
    for file in file_names:
        table = read_pdf(file, pages = '1')[0][['Value', 'Label']]
        scraped_tables.append(table)
    return scraped_tables


def scrape_labels(labels):
    """
    Same scraping and merging as the features, but for the label column only.
    """
    disorders = read_pdf('mh1.pdf', pages = '1')[0][['Value', 'Label']]

    labels = labels.merge(disorders, left_on='MH1', right_on='Value', how='left')
    labels = labels.rename(columns={'MH1':'dummy', 'Label': 'MH1'})
    labels = labels['MH1']

    return labels


def merge_features(scraped_tables, features):
    """
    The tables with the feature strings must be merged and filtered into the main
    dataset. Only the column name and scraped table changes, so leverage a loop
    to merge and filer all.
    """
    old_columns = ['REGION', 'MARSTAT', 'RACE', 'EDUC', 'EMPLOY', 'AGE']

    for featurenum in range(6):
        scraped_table = scraped_tables[featurenum]
        old_column = old_columns[featurenum]
        features = features.merge(scraped_table, left_on=old_column, right_on='Value', how='left')
        features = features.rename(columns={old_column:'dummy', 'Label': old_column})
        features = features.loc[:,features.columns != 'Value']
        features = features.loc[:,features.columns != 'dummy']
    return features


def train_the_model(features_train, labels_train):
    """
    Decision Tree Classifier since we are predicting categorical
    data (which mental health disorder).
    """
    model = DecisionTreeClassifier()
    model.fit(features_train, labels_train)

    # Test
    trained_predictions = model.predict(features_train)
    train_score = accuracy_score(labels_train, trained_predictions)
    return (model, train_score)


def test_the_model(model, features_test, labels_test):
    """
    Find how accurately the model predicted the mental health disorder.
    """
    tested_predictions = model.predict(features_test)
    test_score = accuracy_score(labels_test, tested_predictions)
    return test_score

def main():
    df = pd.read_csv('mhcld-puf-2019-csv.csv')
    # Drop missing values
    df = df.dropna()

    # Grab initial "features" and "labels"
    features = df[['AGE', 'EMPLOY', 'EDUC', 'RACE', 'MARSTAT', 'REGION']]
    # Make labels a DataFrame instead of Series to merge later
    labels = pd.DataFrame(df['MH1'])

    # Scrape and replace the features and labels
    labels = scrape_labels(labels)
    scraped_tables = scrape_tables()
    features_new = merge_features(scraped_tables, features) 

    # Finally, one-hot encode to prepare final features for ML
    features_new = pd.get_dummies(features_new)
    features_train, features_test, labels_train, labels_test = train_test_split(features_new, labels, test_size=0.3)

    # ML Model
    model, train_accuracy = train_the_model(features_train, labels_train)
    print('Train accuracy:', train_accuracy)

    test_accuracy = test_the_model(model, features_test, labels_test)
    print('Test Accuracy:', test_accuracy)
    

if __name__ == '__main__':
    main()