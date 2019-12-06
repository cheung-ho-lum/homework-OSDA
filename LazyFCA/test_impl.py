import copy
from datetime import datetime

#user settings
print_debug = False
advanced_scoring = True
use_IPEDS_files = True
min_hypothesis_length = 4

cv_res = {
    "positive_positive": 0,
    "positive_negative": 0,
    "negative_positive": 0,
    "negative_negative": 0,
    "contradictory": 0,
    "total": 0,
}

#Compares two objects and generates their intersect
#Intersect is a tuple of matching features
#Each matching feature is a tuple of an ordered pair (matching_index,matching value)
def compare(obj1, obj2):
    tup = zip(obj1,obj2)
    tup.pop() #Last feature = target feature. Written this way to save time.
    intersect = []
    for i in range(len(tup)):
        if tup[i][0]==tup[i][1]:
            intersect.append((i,tup[i][0]))
    return tuple(intersect)

def score(pos, neg):
    return pos-neg

def calculate_hypothesis_and_add(intersect, hypotheses, context_plus, context_minus ):
    total_positive_cases = 0.00;
    total_negative_cases = 0.00;
    pos_support = len(context_plus)
    neg_support = len(context_minus)

    for j in context_plus:
        if is_intersect_subset(intersect,j):
            total_positive_cases+=1
    for k in context_minus:
        if is_intersect_subset(intersect,k):
            total_negative_cases+=1

    hypotheses[intersect] = (total_positive_cases/pos_support,total_negative_cases/neg_support)
    return hypotheses

#Loop over all items in intersect and see if they are in list.
def is_intersect_subset(intersect,list):
    for i in range(len(intersect)):
        index = intersect[i][0]
        value = intersect[i][1]
        if list[index] != value:
            return False
    return True


#Obviously this is not the most efficient way of going about things, but there was no demand on efficiency.
'''Prompt: for each object from C+  you have to calculate intersection with the description of the object to classify 
(g'); and check, whether this description is presented in any example from C- do the same thing vice versa for C- - 
for each object description from C- calculate intersection and check whether this intersection is common with any 
object description from C+ You will have to explore possible step functions for classification. 
 '''
def check_intersect(context_plus, context_minus, example, hypotheses):
    global cv_res
    pos = 0.00
    neg = 0.00
    for j in context_plus:
        intersect = compare(example,j)
        if intersect not in hypotheses.keys():
            hypotheses = calculate_hypothesis_and_add(intersect, hypotheses, context_plus, context_minus)
        if (hypotheses[intersect][0]  > hypotheses[intersect][1]):
            if advanced_scoring:
                if(len(intersect) >= min_hypothesis_length):
                    pos += len(intersect)*len(intersect) #* (hypotheses[intersect][0]-hypotheses[intersect][1])
            else:
                pos += 1
    for k in context_minus:
        intersect = compare(example,k)
        if intersect not in hypotheses.keys():
            hypotheses = calculate_hypothesis_and_add(intersect, hypotheses, context_plus, context_minus)
        if(hypotheses[intersect][1] > hypotheses[intersect][0]):
            if advanced_scoring:
                if(len(intersect) >= min_hypothesis_length):
                    neg += len(intersect)*len(intersect) #* (hypotheses[intersect][1]-hypotheses[intersect][0])
            else:
                neg += 1
    pos /= len(context_plus)
    neg /= len(context_minus)
    if score(pos, neg) > 0:
        if example[-1] == 'positive':
            cv_res['positive_positive'] += 1
        else:
            cv_res['negative_positive'] += 1
    elif score(neg, pos) > 0:
        if example[-1] == 'positive':
            cv_res['positive_negative'] += 1
        else:
            cv_res['negative_negative'] += 1
    else:
        cv_res['contradictory'] += 1
# Get data from train and test files
#max_index = sys.argv[1]


for index in xrange(1, int(max_index)):
    index = str(index)

    if use_IPEDS_files:
        q = open("IPEDS_Train_" + index + ".csv", "r")
        next(q) #skip header row, probably needed for original too
    else:
        q = open("train" + index + ".csv", "r")

    train = [a.strip().split(",") for a in q]
    plus  = [a for a in train if a[-1] == "positive"]
    minus = [a for a in train if a[-1] == "negative"]
    q.close()
    if use_IPEDS_files:
        w = open("IPEDS_Test_" + index + ".csv", "r")
        next(w) #skip header row. probably needed for original too
    else:
        w = open("test" + index + ".csv", "r")
        next(w) #skip header row. probably needed for original too

    unknown = [a.strip().split(",") for a in w]
    w.close()

    starttime = datetime.now()
    #Dictionary of Hypotheses:
    #Key = list of tuples indicating the hypothesis
    #Values = tuple containing positive and negative support (not normalized)
    #It turns out that the dictionary doesn't save much runtime overall (~1:22 -> 1:06) even with so many hypotheses.
    hypotheses = dict()
    for elem in unknown:
        cv_res['total'] += 1
        check_intersect(plus, minus, elem, hypotheses)
        if cv_res['total'] % 100 == 0:
            if print_debug:
                print 'Hypotheses: ' + str(len(hypotheses))
                print (str(datetime.now()-starttime))
    print 'Duration of Test ' + str(index) + ': ' + str(datetime.now()-starttime)
    print 'Total Hypotheses: ' + str(len(hypotheses))
cv_res_p = copy.copy(cv_res)
total = cv_res_p["total"]
for k, v in cv_res_p.iteritems():
    cv_res_p[k] = v * 1. / total    # part of 1.0
    
print "Number of datasets done = %s" % index
#print cv_res
