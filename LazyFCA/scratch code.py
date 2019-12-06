def example_score(example, intersect, context_of_example, context_of_counterexamples):
    positive_cases = 0.00
    negative_cases = 0.00
    for j in context_of_example:
        if is_list_subset(intersect,compare(example,j)):
            positive_cases+=1
    for k in context_of_counterexamples:
        if is_list_subset(intersect, compare(example, k)):
            negative_cases+=1
    score= positive_cases / len(context_of_example) - negative_cases / len(context_of_counterexamples)
    if score<=0: return 0
    else: return 1

def is_list_subset(list1,list2):
    for i in range(len(list1)):
        if list1[i]==1 and list2[i]==0: return False
    return True