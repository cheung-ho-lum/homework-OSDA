# Test of Implication Test by Threshold

import sys
from datetime import datetime
#max_index = sys.argv[1]

max_files = 11
ithr_min  = 10         # min Threshold * 10
ithr_max  = 11         # max Threshold * 10

max_index = max_files
accuracy  = {}          # Accuracy for different Threshold
accuracyf = {}          # Accuracy for different number of files
acc_max   = 0           # best Accuracy for different Threshold
acc_maxf  = 0           # best Accuracy for different number of files
ithr_best = ithr_min    # index of best Accuracy for different Threshold
imax_best = 1           # index of best Accuracy for different number of files
totalf    = {}           # total number of examples through all files

startTime = datetime.now()

#Check all files

    #threshold = 1.0   # just disregard this
execfile("test_impl.py")
    
accuracyf[max_index] = cv_res_p["positive_positive"] + cv_res_p["negative_negative"]    # Accuracy
if accuracyf[max_index] > acc_maxf :
    acc_maxf  = accuracyf[max_index]
    imax_best = max_index
totalf[max_index] = cv_res["total"]

print 'Number of Files =', max_index-1, '\tAccuracy =', accuracyf[max_index]
print 'True  Positive :\t', cv_res["positive_positive"], '\t', cv_res_p["positive_positive"]
print 'True  Negative :\t', cv_res["negative_negative"], '\t', cv_res_p["negative_negative"]
print 'False Positive :\t', cv_res["negative_positive"], '\t', cv_res_p["negative_positive"]
print 'False Negative :\t', cv_res["positive_negative"], '\t', cv_res_p["positive_negative"]
print 'Unclassified   :\t', cv_res["contradictory"], '\t', cv_res_p["contradictory"]
print 'Total          :\t', cv_res["total"], '\t', cv_res_p["total"]
print '========================================================'


#print '========================================================'
#print datetime.now() - startTime
#print "Files  \t\tExamples \tAccuracy"
#print "-------\t\t-------- \t--------------"
#print max_index-1, "\t\t", totalf[max_index], "\t\t", accuracyf[max_index], "\t"

print '========================================================'
print 'Runtime:' + str(datetime.now() - startTime)