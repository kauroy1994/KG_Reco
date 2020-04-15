from Data import Reco_data
from PhiMap import PhiMap

def main():
    """main method
    """

    d = Reco_data()
    d.get_data()
    collab_data = d.collab_data
    bk = d.collab_bk

    train_facts = [item[:-1] for item in collab_data[0]]
    train_pos = [item[:-1] for item in collab_data[1]]
    train_neg = [item[:-1] for item in collab_data[2]]
    target = d.collab_target

    PhiMap.learn(train_facts,bk,target,train_pos,train_neg)
    PhiMap.remove_redundant(train_facts,train_pos,train_neg)

    print (PhiMap.clause_list)

if __name__ == '__main__':

    main()
    
