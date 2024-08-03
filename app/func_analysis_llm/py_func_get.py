import inspect
import importlib.util
import os, sys, json
from pathlib import Path

class PyFunctionGetter:
    def select_dir_functions_bodies(self, dir_path):
        all_functions_bodies = {}
        path = Path(dir_path)
        for file_path in path.glob("**/*.py"):
            print('Parse file:', file_path)
            all_functions_bodies = {**all_functions_bodies, **self.select_all_functions_bodies(file_path)}
        
        return all_functions_bodies

    def select_all_functions_bodies(self, file_path):
        #  Get function 
        functions_bodies = self.get_functions_and_bodies(file_path)

        #  Get class member functions 
        classes_functions_bodies = self.get_classes_functions_and_bodies(file_path)
        classes_functions_bodies = self.class_func_name_combine(classes_functions_bodies)

        #  Merge output 
        all_functions_bodies = {**functions_bodies, **classes_functions_bodies}

        #  Add file name 
        file_name = os.path.basename(file_path).rsplit('.', 1)[0]
        final_functions_bodies = {}
        for func_name, func_body in all_functions_bodies.items():
            final_functions_bodies[f'{file_name}.{func_name}'] = func_body
        
        return final_functions_bodies

    def get_functions_and_bodies(self, file_path):
        sys.path.append(os.path.dirname(file_path))
        sys.path.append(os.path.join(os.path.dirname(file_path), '../../http_server/infer_call'))
        
        #  Dynamic import module 
        module_name = 'example_module'
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        functions_bodies = {}
        #  Traverse all members in the module and check if they are functions 
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                try:
                    function_body = inspect.getsource(obj)
                    functions_bodies[name] = function_body
                except TypeError:
                    #  Some built-in / The imported function may not be able to obtain the source code 
                    functions_bodies[name] = "Function body not available."

        return functions_bodies

    def get_classes_functions_and_bodies(self, file_path):
        sys.path.append(os.path.dirname(file_path))
        sys.path.append(os.path.join(os.path.dirname(file_path), '../../http_server/infer_call'))

        #  Dynamic import module 
        module_name = 'example_module'
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        #  Dictionary for storing results 
        classes_functions_bodies = {}

        #  Traverse all classes in the module 
        for name, obj in inspect.getmembers(module, inspect.isclass):
            #  Get all member functions and their bodies in the class 
            member_functions = {}
            for f_name, f_obj in inspect.getmembers(obj, inspect.isfunction):
                try:
                    function_body = inspect.getsource(f_obj)
                    member_functions[f_name] = function_body
                except TypeError:
                    #  Some built-in / The imported function may not be able to obtain the source code 
                    member_functions[f_name] = "Function body not available."

            classes_functions_bodies[name] = member_functions

        return classes_functions_bodies
    
    def class_func_name_combine(self, classes_functions_bodies):
        functions_bodies = {}
        for c_name, c_info in classes_functions_bodies.items():
            for f_name, f_body in c_info.items():
                combine_name = f'{c_name}.{f_name}'
                functions_bodies[combine_name] = f_body
        
        return functions_bodies
    
    def filter_functions(self, all_functions_bodies):
        result_f_b = {}
        for f_name, f_body in all_functions_bodies.items():
            if f_name.rsplit('.', 1)[1].startswith('test'):
                result_f_b[f_name] = f_body
        return result_f_b

if __name__ == '__main__':
    file_path=r'C:\Users\zezhong\Documents\github\ds_deployer\test\UnitTest\main.py'
    dir_path=r'C:\Users\zezhong\Documents\github\ds_deployer\http_server\infer_call'

    pfg = PyFunctionGetter()
    all_functions_bodies = pfg.select_all_functions_bodies(file_path)
    # all_functions_bodies = pfg.select_dir_functions_bodies(dir_path)

    all_functions_bodies = pfg.filter_functions(all_functions_bodies)

    with open('app/func_analysis_llm/callgraph_data/src_test_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_functions_bodies, f, indent=4)
