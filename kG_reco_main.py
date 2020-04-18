from Data import Reco_data
from PhiMap import PhiMap
from random import choice
from Prover import Prover
from sklearn.svm import LinearSVC
from numpy import array

def dot(a,b):

    n = len(a)
    return (sum([a[i]*b[i] for i in range(n)]))

def run_linSVM(data,all_clauses):
    """runs scikit-learns linear SVM module
    """
    print ('='*40+" Weights learned by linear SVM"+'='*40)
    X,y = array(data[0]),array(data[1])
    clf = LinearSVC()
    #clf = SVC(kernel = 'linear')
    clf.fit(X,y)
    coeffs = list(clf.coef_[0])
    for clause in all_clauses:
        print (clause,coeffs[all_clauses.index(clause)])
    
    sv_count = 0
    print ('='*80)
    for item in X:
        W = coeffs + [clf.intercept_[0]]
        x_item = list(item)+[1.0]
        if round(abs(dot(W,x_item)),1) == 1.0:
            sv_count += 1
    print ("Number of support vectors",sv_count)
    

def get_one_person_data(collab_data,context_data,all_clauses):
    """gets random persons data
       for demo
    """

    spec_person = 'p0'

    collab_data_pos = [item[:-1] for item in collab_data[1]]
    collab_data_neg = [item[:-1] for item in collab_data[2]]
    collab_data_facts = [item[:-1] for item in collab_data[0]]
    context_data_facts = [item[:-1] for item in context_data[0]]
    context_data_pos = [item[:-1] for item in context_data[1]]
    context_data_neg = [item[:-1] for item in context_data[2]]

    facts = collab_data_facts + context_data_facts
    examples = collab_data_pos + collab_data_neg + context_data_pos + context_data_neg

    person_song = {}
    X,y = [],[]

    for example in examples:
        person = example.split('(')[1].split(',')[0]
        if person != spec_person:
            continue
        song = example.split('(')[1][:-1].split(',')[1]
        if (person,song) not in person_song:
            person_song[(person,song)] = []
        for clause in all_clauses:
            Prover.rule = clause
            Prover.facts = facts
            person_song[(person,song)] += [float(Prover.prove_rule(example))+1.0]

        if example in collab_data_pos or example in context_data_pos:
            person_song[(person,song)] += [int(1)]

        if example in collab_data_neg or example in context_data_neg:
            person_song[(person,song)] += [int(0)]

    for item in person_song:
        X.append(person_song[item][:-1])
        y.append(person_song[item][-1])

    return (X,y)

def main():
    """main method
    """

    d = Reco_data()
    d.get_data()
    collab_clauses = []
    context_clauses = []
    
    collab_data = d.collab_data
    bk = d.collab_bk

    train_facts = [item[:-1] for item in collab_data[0]]
    train_pos = [item[:-1] for item in collab_data[1]]
    train_neg = [item[:-1] for item in collab_data[2]]
    target = d.collab_target

    PhiMap.learn(train_facts,bk,target,train_pos,train_neg)
    collab_clauses = PhiMap.clause_list
    
    context_data = d.context_data
    bk = d.context_bk

    train_facts = [item[:-1] for item in context_data[0]]
    train_pos = [item[:-1] for item in context_data[1]]
    train_neg = [item[:-1] for item in context_data[2]]
    target = d.context_target

    PhiMap.learn(train_facts,bk,target,train_pos,train_neg)
    context_clauses = PhiMap.clause_list

    all_clauses = context_clauses + collab_clauses

    print ('='*40+' POSSIBLE THEORIES '+'='*40)
    
    for clause in all_clauses:
        print (clause)
        
    person_data = get_one_person_data(collab_data,context_data,all_clauses)

    run_linSVM(person_data,all_clauses)


if __name__ == '__main__':

    main()
    
