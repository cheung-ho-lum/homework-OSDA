import sys
import random
import copy

attrib_names = [
    'top-left-square',
    'top-middle-square',
    'top-right-square',
    'middle-left-square',
    'middle-middle-square',
    'middle-right-square',
    'bottom-left-square',
    'bottom-middle-square',
    'bottom-right-square',
    'class'
]

def make_intent(example):
    global attrib_names
    return set([i+':'+str(k) for i, k in zip(attrib_names, example)])

cv_res = {
    "positive_positive": 0,
    "positive_negative": 0,
    "negative_positive": 0,
    "negative_negative": 0,
    "contradictory": 0,
    "total": 0,
}

def check_intersect(context_plus, context_minus, example, num_sub=1):
    global cv_res
    pos = 0
    neg = 0
    intent = make_intent(example)
    for i in xrange(num_sub):
        t = set(random.sample(example, random.randrange(len(intent)))) #t is some set of 0,1,and (KEY) positive/negative
        #Illustration: suppose we omit the target feature from example (uncomment below code)
        t.discard('positive')
        t.discard('negative')

        for j in context_plus:
            if t.issubset(j): #Suppose t does contain identifying information, ex. [0,1,positive]
                pos += len(t) #It will be very likely to be in j and...
        for k in context_minus:
            if t.issubset(k):
                neg += len(t) #not very likely to be in k

    def score(pos, neg):
        return pos * 1. / (neg + 1)

    #threshold = 1.1
    
    if score(pos, neg) > threshold:
        if example[-1] == 'positive':
            cv_res['positive_positive'] += 1
        else:
            cv_res['negative_positive'] += 1
    elif score(neg, pos) > threshold:
        if example[-1] == 'positive':
            cv_res['positive_negative'] += 1
        else:
            cv_res['negative_negative'] += 1
    else:
        cv_res['contradictory'] += 1

def check_hypothesis(context_plus, context_minus, example):
    global cv_res
    eintent = make_intent(example)
    big_context = context_plus + context_minus
    labels = {}
    for e in big_context:
        ei = make_intent(e)
        candidate_intent = ei & eintent
        if not candidate_intent:
            continue

        closure = [make_intent(i) for i in big_context
                   if make_intent(i).issuperset(candidate_intent)]

        res = reduce(lambda x, y: x & y if x & y else x | y, closure)

        for cs in ['positive', 'negative']:
            if 'class:' + cs in res:
                labels[cs] = True
                labels[cs + '_res'] = candidate_intent

    if labels.get("positive", False) and labels.get("negative", False):
        cv_res["contradictory"] += 1
        return
    if example[-1] == "positive" and labels.get("positive", False):
        cv_res["positive_positive"] += 1
    if example[-1] == "negative" and labels.get("positive", False):
        cv_res["negative_positive"] += 1
    if example[-1] == "positive" and labels.get("negative", False):
        cv_res["positive_negative"] += 1
    if example[-1] == "negative" and labels.get("negative", False):
        cv_res["negative_negative"] += 1

# Get data from train and test files
#max_index = sys.argv[1]
use_IPEDS_files = False
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

    for elem in unknown:
        cv_res['total'] += 1
        check_intersect(plus, minus, elem, len(elem) / 2)

cv_res_p = copy.copy(cv_res)
total = cv_res_p["total"]
for k, v in cv_res_p.iteritems():
    cv_res_p[k] = v * 1. / total    # part of 1.0
    
print "Number of datasets done = %s" % index
#print cv_res
