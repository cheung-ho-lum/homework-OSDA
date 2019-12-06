#Imports#
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


#Program Options
print_debug = False
print_results = True
display_graphs = True
analyze_full = False
analyze_clc = False
analyze_small = True
balance_data = True


#Researcher Options
num_estimators = 100    # Number of trees in our forest
num_features_disp = 10  # Number of features to display in feature importance graph
max_depth = 50          # A higher depth is less explainable

target = 'Low Price'
confusion_matrix = [[0,0],[0,0]]
for index in xrange(1, 11):
    train = pd.read_csv('IPEDS_Train_' + str(index) + '.csv')
    test = pd.read_csv('IPEDS_Test_' + str(index) + '.csv')
    clf = RandomForestClassifier(n_estimators=num_estimators)
    target_train = train['Low Price']
    features_train = train.drop(columns=['Low Price'])
    target_test = test['Low Price']
    features_test = test.drop(columns=['Low Price'])

    clf.fit(features_train, target_train)
    target_pred = clf.predict(features_test)
    confusion_matrix += metrics.confusion_matrix(target_test, target_pred) #row i = truth, col j = predictions
print confusion_matrix


