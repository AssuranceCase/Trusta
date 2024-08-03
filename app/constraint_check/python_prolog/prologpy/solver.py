from prologpy.interpreter import Database, Variable
from prologpy.parser import Parser
from collections import defaultdict


class Solver(object):
    def __init__(self, rules_text):
        rules = Parser(rules_text).parse_rules()
        self.database = Database(rules)

    def find_solutions(self, query_text):

        query = Parser(query_text).parse_query()

        query_variable_map = {}
        variables_in_query = False

        for argument in query.arguments:
            if isinstance(argument, Variable):
                variables_in_query = True
                query_variable_map[argument.name] = argument

        matching_query_terms = [item for item in self.database.query(query)]

        if matching_query_terms:
            if query_variable_map:

                solutions_map = defaultdict(list)
                for matching_query_term in matching_query_terms:
                    matching_variable_bindings = query.match_variable_bindings(
                        matching_query_term
                    )

                    for variable_name, variable in query_variable_map.items():
                        solutions_map[variable_name].append(
                            matching_variable_bindings.get(variable)
                        )

                return solutions_map

            else:
                return True if not variables_in_query else None
        else:
            return False if not variables_in_query else None

def run_query(rules_text, query_text, state_info):
    try:
        solver = Solver(rules_text)
    except Exception as e:
        state_info.append("Error processing prolog rules." + str(e))
        return -1

    try:
        solutions = solver.find_solutions(query_text)
    except Exception as e:
        state_info.append("Error processing prolog query." + str(e))
        return -2

    if isinstance(solutions, bool):
        state_info.append("Yes" if solutions else "No")
        return 1
    elif isinstance(solutions, dict):
        state_info.append("\n".join(
            "{} = {}"
            .format(variable, value[0] if len(value) == 1 else value)
            for variable, value in solutions.items()
        ))
        return 2
    else:
        state_info.append("No solutions found.")
        return 0
    