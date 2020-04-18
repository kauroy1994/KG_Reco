from string import ascii_uppercase
from itertools import product
from copy import deepcopy
from Prover import Prover
from math import log2
from statistics import pvariance, mean

class Node(object):
    """implements clause node
    """
    
    def __init__(self,facts,examples,bk,clause,var_types={}):
        """information needed during current
           and k+1th degree clause modelling
        """

        self.facts = facts
        self.examples = examples
        self.bk = bk
        self.clause = clause
        self.var_types = var_types

    def __repr__(self):

        return_str = "clause: "+self.clause.replace(';',',')
        return_str += "\n\nfacts:\n"
        return_str += str(self.facts)
        return_str += "\n\nexamples:\n"
        return_str += str(self.examples)
        return_str += "\n\nvariables and types:\n"
        return_str += str(self.var_types)+"\n"
        return (return_str)


class PhiMap(object):
    """implements PhiMap learning
    """

    target = None
    score_threshold = 0.99
    max_degree = 2
    all_vars = list(ascii_uppercase)
    target_pred = ''
    clauses = {}
    clause_list = []
    var_types = {}
    
    @staticmethod
    def init():
        """initializes clauses
        """
        PhiMap.target = None
        PhiMap.score_threshold = 0.99
        PhiMap.max_degree = 2
        PhiMap.all_vars = list(ascii_uppercase)
        PhiMap.target_pred = ''
        PhiMap.clauses = {}
        PhiMap.clause_list = []
        PhiMap.var_types = {}
        for d in range(PhiMap.max_degree):
            PhiMap.clauses[d] = []

    @staticmethod
    def get_conditions(facts,bk,var_types):
        """gets all conditions corresponding
           to degree k based on aleph modes
        """

        conditions = []    
        node_var_types = deepcopy(var_types)

        for functor in bk:

            #target alpeh mode info skip
            if functor.split('(')[0] == PhiMap.target:
                continue

            #for other modes, generate literals
            pred = functor.split('(')[0]
            mode = functor.split('(')[1][:-1].split(',')
            n = len(mode)
            args = [[] for i in range(n)]
            for i in range(n):
                spec = mode[i]

                #if '+' then set with seen var of same type
                if spec[0] == '+':
                    typ = spec[1:]

                    #assume var of same type not in clause
                    exists = False

                    for var in var_types:
                        if var_types[var] == typ:
                            exists = True
                            args[i].append(var)
                            node_var_types[var] = typ

                    #if no var of type in clause
                    if not exists:

                        #assume var not in prev mode
                        seen = False
                        for var in PhiMap.all_vars:
                            if (var in node_var_types) and (node_var_types[var] == typ):
                                seen = True
                                args[i].append(var)
                                break
                        if not seen:
                            for new_var in PhiMap.all_vars:
                                if new_var not in node_var_types:
                                    args[i].append(new_var)
                                    node_var_types[new_var] = typ
                                    break
                #if '-' then set with new var not in clause
                elif spec[0] == '-':
                    typ = spec[1:]

                    seen = False
                    for var in PhiMap.all_vars:
                        if (var in node_var_types) and (node_var_types[var] == typ) and (var not in var_types):
                            seen = True
                            args[i].append(var)
                            break
                    if not seen:
                        for new_var in PhiMap.all_vars:
                            if new_var not in node_var_types:
                                args[i].append(new_var)
                                node_var_types[new_var] = typ
                                break

                #if '#' collect all constants from facts at this pos
                elif spec[0] == '#':
                    for fact in facts:
                        if fact.split('(')[0] == pred:
                            fact_args = fact.split('(')[1][:-1].split(',')
                            if fact_args[i] not in args[i]:
                                args[i].append(fact_args[i])

            combinations = list(product(*args))
            for combination in combinations:
                literal = pred+'('+','.join(list(combination))+')'
                if (literal not in conditions):
                    conditions.append((literal,functor))

        return (conditions,node_var_types)
                
    @staticmethod
    def learn(facts,bk,target,pos=[],neg=[],examples={}):
        """learns a PhiMap of max_degree
           from data,examples and aleph modes
           to constrain the search
        """

        PhiMap.init()

        for ex in pos:
            examples[ex] = 1

        for ex in neg:
            examples[ex] = 0

        #assign clause targets
        PhiMap.target = target

        for d in range(PhiMap.max_degree):

            if d == 0:

                #set target pred and vars as per aleph modes
                PhiMap.target_pred = PhiMap.target+'('
                for functor in bk:
                    if functor.split('(')[0] == PhiMap.target:
                        mode = functor.split('(')[1][:-1].split(',')
                        n = len(mode)
                        for i in range(n):
                            variable = PhiMap.all_vars[i]
                            typ = mode[i][1:]
                            PhiMap.target_pred += variable+','
                            PhiMap.var_types[variable] = typ
                        break
                PhiMap.target_pred = PhiMap.target_pred[:-1]+')'
                conditions = PhiMap.get_conditions(facts,bk,PhiMap.var_types)
                for condition in conditions[0]:
                    positive_covered = False
                    negative_covered = False
                    node_examples = {}
                    clause = PhiMap.target_pred+':-'
                    clause += condition[0]
                    if PhiMap.senseless(clause):
                        continue
                    example_list = list(examples.keys())
                    n = len(example_list)
                    print ("Checking theory:",clause)
                    Prover.rule = clause
                    Prover.facts = facts
                    for example in example_list:
                        if Prover.prove_rule(example) and example in pos:
                            positive_covered = True
                            node_examples[example] = 1
                        if Prover.prove_rule(example) and example in neg:
                            negative_covered = True
                            node_examples[example] = 0
                    if positive_covered and negative_covered:
                        node = Node(facts,node_examples,bk,clause,conditions[1])
                        PhiMap.clauses[d].append(node)
                        PhiMap.clause_list.append(node.clause)

            if d > 0:
                #print ('='*80)
                prev_degree_nodes = PhiMap.clauses[d-1]
                for node in prev_degree_nodes:
                    conditions = PhiMap.get_conditions(facts,bk,node.var_types)
                    node_conditions = node.clause.split(':-')[1].split(';')
                    for condition in conditions[0]:
                        positive_covered = False
                        negative_covered = False
                        node_examples = {}
                        if condition[0] in node_conditions:
                            continue
                        clause = node.clause+';'+condition[0]
                        if PhiMap.senseless(clause):
                            continue
                        example_list = list(node.examples.keys())
                        n = len(example_list)
                        print ("Checking theory:",clause)
                        Prover.rule = clause
                        Prover.facts = facts
                        for example in example_list:
                            if Prover.prove_rule(example) and example in pos:
                                positive_covered = True
                                node_examples[example] = 1
                            if Prover.prove_rule(example) and example in neg:
                                negative_covered = True
                                node_examples[example] = 0
                        if positive_covered and negative_covered:
                            new_node = Node(facts,node_examples,bk,clause,conditions[1])
                            PhiMap.clauses[d].append(new_node)
                            PhiMap.clause_list.append(new_node.clause)
                            
        PhiMap.remove_copies()        

    @staticmethod
    def equals(clause1,clause2,facts,pos,neg):
        """checks if two clauses correlated
        """

        examples = pos+neg

        clause1_signature = ""
        clause2_signature = ""

        Prover.rule = clause1
        Prover.facts = facts
        for example in examples:
            if not Prover.prove_rule(example,exists=False):
                clause1_signature += str(int(Prover.prove_rule(example,exists=False)))
            else:
                clause1_signature += str(len(Prover.prove_rule(example,exists=False)[0]))

        Prover.rule = clause2
        for example in examples:
            if not Prover.prove_rule(example,exists=False):
                clause2_signature += str(int(Prover.prove_rule(example,exists=False)))
            else:
                clause2_signature += str(len(Prover.prove_rule(example,exists=False)[0]))

        if clause1_signature == clause2_signature:
            return True

        return False

    @staticmethod
    def senseless(clause):
        """removes senseless clauses
        """
        clause_head = clause.split(':-')[0]
        clause_body = clause.split(':-')[1].split(';')
        head_vars = clause_head.split('(')[1][:-1].split(',')
        body_vars = []
        for literal in clause_body:
            literal_vars = literal.split('(')[1][:-1].split(',')
            body_vars += literal_vars
        for var in body_vars:
            if var in head_vars:
                return False
        return True

    @staticmethod
    def remove_copies():
        """removes clause copies
        """

        nc = []
        
        n = len(PhiMap.clause_list)
        for i in range(n):
            copied = False
            curr = PhiMap.clause_list[i]
            for clause in PhiMap.clause_list[:i]:
                curr_literals = curr.split(':-')[1].split(';')
                clause_literals = clause.split(':-')[1].split(';')
                if set(clause_literals) == set(curr_literals):
                    copied = True
            if not copied:
                nc.append(curr)

        PhiMap.clause_list = nc
            

    @staticmethod
    def remove_redundant(facts,pos,neg):
        """removes correlated clauses
        """

        unique = []

        n_clauses = len(PhiMap.clause_list)
        for i in range(n_clauses):
            redundant = False
            for clause in PhiMap.clause_list[:i]:
                if PhiMap.equals(clause,PhiMap.clause_list[i],facts,pos,neg):
                    redundant = True
            if not redundant:
                unique.append(PhiMap.clause_list[i])

        PhiMap.clause_list = unique
                    
# --> TODO: ============ WRITE TEST CASE HERE ASAP =================

"""                
def main():
    #main method
    

    train_data = ['o(m1,d1)','r(m1,w1,st)','o(m2,d2)','r(m2,w2,st)','o(m3,d3)','r(m3,w3,st)','o(m4,d4)','r(m4,w4,lt)','r(m5,w5,st)','r(m6,w6,lt)','r(m7,w7,lt)']
    train_pos = ['h(m1)','h(m2)','h(m4)','h(m6)']
    train_neg = ['h(m3)','h(m5)','h(m7)']
    target = 'h'
    bk = ['h(+man)','o(+man,-dog)','r(+man,-woman,#term)']

    PhiMap.learn(train_data,bk,target,train_pos,train_neg)
    PhiMap.remove_redundant(train_data,train_pos,train_neg)

    print (PhiMap.clause_list)
    
if __name__ == '__main__':

    main()
"""
