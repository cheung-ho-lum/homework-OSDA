import pandas as pd
import numpy as np
#User Settings
training_set = 0.7
show_descriptive_statistics = True
num_cross_validations = 10

#Drops empty rows from IPEDS and creates test and train sets
attribute_names=['Name','Percent admitted - total','Total price for out-of-state students living on campus 2013-14',
                 'Geographic region','Estimated undergraduate enrollment total','Sector of institution',
                 'Percent of freshmen receiving any financial aid','Percent of freshmen receiving Pell grants']


#Initial data set has 1534 objects
data = pd.read_csv("IPEDS_Simple.csv")
data.replace('', np.nan, inplace=True)
data.dropna(inplace=True) #Completely drop anyone with any empty attributes (1326 results remain)

#Next, we go about renaming our columns and data for reading and processing purpose
data.rename(columns={'Percent admitted - total':'Percent Admitted',
                    'Total price for out-of-state students living on campus 2013-14':'Price (OOS)',
                    'Geographic region':'Region',
                    'Estimated undergraduate enrollment, total':'Undergrad Enrollment',
                    'Sector of institution':'Public',
                    'Percent of freshmen receiving any financial aid': 'Financial Aid',
                    'Percent of freshmen receiving Pell grants': 'Pell Grant'},inplace=True)



#Public institutions = 1, Private Institutions = 0
data['Public'].replace('Public, 4-year or above', 1, inplace=True)
data['Public'].replace('Private not-for-profit, 4-year or above', 0, inplace=True)

region_SE = 'Southeast AL AR FL GA KY LA MS NC SC TN VA WV'
region_W = 'Far West AK CA HI NV OR WA'
region_SW = 'Southwest AZ NM OK TX'
region_MNT = 'Rocky Mountains CO ID MT UT WY'
region_NE = 'New England CT ME MA NH RI VT'
region_ME = 'Mid East DE DC MD NJ NY PA'
region_MW = 'Great Lakes IL IN MI OH WI'
region_GP = 'Plains IA KS MN MO NE ND SD'

if show_descriptive_statistics:
    #Quick reference: 1QR,2QR,3QR
    print data['Percent Admitted'].describe() #54,66,77
    print data['Price (OOS)'].describe() #31842,37902,46323
    print data['Undergrad Enrollment'].describe() #1476,2687,6844
    print data['Financial Aid'].describe() #87,96,99
    print data['Pell Grant'].describe() #26,37,48
    print data.groupby(['Region']).size()
    print data.groupby(['Public']).size()


#Here we print our intermediate result
data.to_csv('IPEDS_Clean.csv',index=False)

#And then we proceed to drop identifying information
del data['ID number']
del data['Name']

#Next, we have to classify each of the variables
#Overall Settings
split_price = 38000
split_admitted_1 = 40 #Split on very selective schools
split_admitted_2 = 65  #Split on selective schools
split_enrollment_1 = 1000 #Split on low enrollment schools
split_financial_aid_1 = 90 #Split on low financial aid
split_pell_grant_1 = 30 #Split pell grant low
split_pell_grant_2 = 45 #Split pell grant high

if show_descriptive_statistics:
    less_than_split = data['Price (OOS)'] < split_price
    gte_split = data['Price (OOS)'] >= split_price
    less_than_pell_1 = data['Pell Grant'] < split_pell_grant_1
    gte_pell_1 = data['Pell Grant'] >= split_pell_grant_1

    print data[less_than_split].groupby(['Region']).size()
    print data[gte_split].groupby(['Region']).size()

    print len(data[less_than_split][less_than_pell_1])
    print len(data[gte_split][less_than_pell_1])
    print len(data[less_than_split][gte_pell_1])
    print len(data[gte_split][gte_pell_1])

#Public
data['Private'] = np.where(data['Public'] == 0, 1, 0)
#del data['Public'] #no need to delete this one

#Percent Admitted
data['Very Selective Admissions'] = np.where(data['Percent Admitted'] < split_admitted_1, 1, 0)
data['Selective Admissions'] = np.where(data['Percent Admitted'] < split_admitted_2, 1, 0)
data['Regular Admissions'] = np.where(data['Percent Admitted'] >= split_admitted_2, 1, 0)
del data['Percent Admitted']

#Region
data['New England'] = np.where(data['Region'] == region_NE, 1, 0)
data['West Coast'] = np.where(data['Region'] == region_W, 1, 0)
data['Inland'] = np.where(data['Region'].isin([region_MNT,region_GP, region_MW]), 1, 0)
data['South and Southwest'] = np.where(data['Region'].isin([region_SW, region_SE]), 1, 0)
del data['Region']
#Not split: SW, SE, ME

#Undergrad Enrollment
data['Small Enrollment'] = np.where(data['Undergrad Enrollment'] < split_enrollment_1, 1, 0)
data['Regular Enrollment'] = np.where(data['Undergrad Enrollment'] >= split_enrollment_1, 1, 0)
del data['Undergrad Enrollment']

#Financial Aid
data['Low Aid'] = np.where(data['Financial Aid'] < split_financial_aid_1, 1, 0)
data['Regular Aid'] = np.where(data['Financial Aid'] >= split_financial_aid_1, 1, 0)
del data['Financial Aid']

#Pell Grant
data['Low Pell'] = np.where(data['Pell Grant'] < split_pell_grant_1, 1, 0)
data['Medium Pell'] = np.where(data['Pell Grant'] < split_pell_grant_2, 1, 0)
data['High Pell'] = np.where(data['Pell Grant'] >= split_pell_grant_2, 1, 0)
del data['Pell Grant']

#Price (OOS) (target variable)
#TODO: out of laziness, target variable must always be last.
data['Low Price'] = np.where(data['Price (OOS)'] < split_price, 'positive', 'negative')
del data['Price (OOS)']

#data = data.sample(frac=0.5) #half the number of samples for timing analysis

#Here we print our intermediate result
data.to_csv('IPEDS_Clean_Normalized.csv',index=False)

#And split into train/test cases (10-fold cross-validation, 30% training set)
for i in range(1, num_cross_validations+1):
    train = data.sample(frac=training_set)
    test = data.drop(train.index)
    train.to_csv('IPEDS_Train_'+str(i)+'.csv',index=False)
    test.to_csv('IPEDS_Test_'+str(i)+'.csv',index=False)
