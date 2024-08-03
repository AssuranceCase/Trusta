import os, sys

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append('../')
from prologpy import Solver
from prologpy import run_query


def test_simple_goal_query():

    rules_text = """

        brother_sister(joe, monica).
        brother_sister(eric, erica).
        brother_sister(jim, rebecca).

    """

    goal_text = """

        brother_sister(jim, rebecca).

    """

    solver = Solver(rules_text)
    solution = solver.find_solutions(goal_text)

    assert solution


def test_simple_goal_query2():
    rules_text = """

        brother_sister(joe, monica).
        brother_sister(eric, erica).
        brother_sister(jim, rebecca).

    """

    goal_text = """

        brother_sister(joe, rebecca).

    """

    solver = Solver(rules_text)
    solution = solver.find_solutions(goal_text)

    assert not solution


def test_simple_variable_query():

    rules_text = """

        father_child(mike, john).
        father_child(eric, sarah).
        father_child(bob, jim).

    """

    query_text = """

        father_child(X, sarah).

    """

    solver = Solver(rules_text)
    solutions = solver.find_solutions(query_text)

    assert len(solutions.get("X")) == 1

    assert str(solutions.get("X").pop()) == "eric"


def test_multi_variable_solutions():

    rules_text = """

        is_tall(jack, yes).
        is_tall(eric, no).
        is_tall(johnny, yes).
        is_tall(mark, no).

    """

    query_text = """

        is_tall(Y, yes)

    """

    solver = Solver(rules_text)
    solutions = solver.find_solutions(query_text)

    assert len(solutions.get("Y")) == 2

    assert ("jack" in str(solution) for solution in solutions.get("Y"))
    assert ("johnny" in str(solution) for solution in solutions.get("Y"))


def test_find_bad_dog():

    rules_text = """
        
        bad_dog(Dog) :-
           bites(Dog, Person),
           is_person(Person),
           is_dog(Dog).
        
        bites(fido, postman).
        is_person(postman).
        is_dog(fido).

    """

    query_text = """

        bad_dog( X )

    """

    solver = Solver(rules_text)
    solutions = solver.find_solutions(query_text)

    assert len(solutions.get("X")) == 1

    assert ("fido" in str(solution) for solution in solutions.get("X"))


def test_rule_sub():

    rules_text = """

        descendant(X, Y) :- offspring(X, Y).
        descendant(X, Z) :- offspring(X, Y), descendant(Y, Z).
        
        offspring(abraham, ishmael).
        offspring(abraham, isaac).
        offspring(isaac, esau).
        offspring(isaac, jacob).

    """

    query_text = """

        descendant(abraham, X).

    """

    solver = Solver(rules_text)
    solutions = solver.find_solutions(query_text)

    assert len(solutions.get("X")) == 4

    assert ("ishmael" in str(solution) for solution in solutions.get("X"))
    assert ("isaac" in str(solution) for solution in solutions.get("X"))
    assert ("esau" in str(solution) for solution in solutions.get("X"))
    assert ("jacob" in str(solution) for solution in solutions.get("X"))


def test_rule_sub2():

    rules_text = """

        father_child(massimo, ridge).
        father_child(eric, thorne).
        father_child(thorne, alexandria).

        mother_child(stephanie, chloe).
        mother_child(stephanie, kristen).
        mother_child(stephanie, felicia).

        parent_child(X, Y) :- father_child(X, Y).
        parent_child(X, Y) :- mother_child(X, Y).

        sibling(X, Y) :- parent_child(Z, X), parent_child(Z, Y).

    """

    query_text = """

 

    """

    solver = Solver(rules_text)
    solutions = solver.find_solutions(query_text)

    assert len(solutions.get("X")) == 3

    assert ("chloe" in str(solution) for solution in solutions.get("X"))
    assert ("kristen" in str(solution) for solution in solutions.get("X"))
    assert ("alexandria" in str(solution) for solution in solutions.get("X"))


def test_multiple_var_query():

    rules_text = """

        father(jack, susan).                            
        father(jack, ray).                             
        father(david, liza).                       
        father(david, john).                           
        father(john, peter).                
        father(john, mary).                     
        mother(karen, susan).                        
        mother(karen, ray).                              
        mother(amy, liza).                        
        mother(amy, john).                        
        mother(susan, peter).                            
        mother(susan, mary).                             
        
        parent(X, Y) :- father(X, Y).                    
        parent(X, Y) :- mother(X, Y).                    
        grandfather(X, Y) :- father(X, Z), parent(Z, Y).
        grandmother(X, Y) :- mother(X, Z), parent(Z, Y). 
        grandparent(X, Y) :- parent(X, Z), parent(Z, Y). 

    """

    query_text = """

        grandparent(X, Y)

    """

    solver = Solver(rules_text)
    solution_map = solver.find_solutions(query_text)
    solutions = list(zip(solution_map.get("X"), solution_map.get("Y")))

    assert len(solutions) == 8

    assert ("(jack, peter)" in str(solution) for solution in solutions)
    assert ("(jack, mary)" in str(solution) for solution in solutions)
    assert ("(david, peter)" in str(solution) for solution in solutions)
    assert ("(david, mary)" in str(solution) for solution in solutions)
    assert ("(karen, peter)" in str(solution) for solution in solutions)
    assert ("(karen, mary)" in str(solution) for solution in solutions)
    assert ("(amy, peter)" in str(solution) for solution in solutions)
    assert ("(amy, peter)" in str(solution) for solution in solutions)


def test_multiple_var_query_commiter():

    rules_text = """
        self_reviewed(M) :- developer(M, ID), committer(M, ID).
        developer(mr_a, zhangsan).
        developer(mr_b, lisi).
        committer(mr_a, zhangsan).
        committer(mr_b, wangwu). 
    """

    query_text = """
        self_reviewed(M)
    """

    solver = Solver(rules_text)
    solution_map = solver.find_solutions(query_text)
    solutions = solution_map.get("M")

    assert len(solutions) == 1
    assert 'mr_a' == str(solutions[0])

def test_multiple_var_query_api():
    
    rules_text = """
        self_reviewed(M) :- developer(M, ID), committer(M, ID).
        developer(mr_a, zhangsan).
        developer(mr_b, lisi).
        committer(mr_a, zhangsan).
        committer(mr_b, wangwu). 
    """

    query_text = """
        self_reviewed(M)
    """
    state_info = []
    if run_query(rules_text, query_text, state_info) >= 0:
        print('执行成功')
        print(state_info)
    else:
        print('执行失败')

if __name__ == '__main__':
    test_multiple_var_query_api()
