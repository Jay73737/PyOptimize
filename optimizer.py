import os
import inspect
import importlib
import traceback
import subprocess
import sys
import numpy

class TextParser:


    def __init__(self, main_file = None):
        self.file = main_file
        self.lines_list = None
        self.import_list = []  
        self.sys_path = sys.path.copy()
        self.files_found = []

    def find_end_parenthesis(self, line):
        for i,f in enumerate(self.file[line:]): 
            if ")" in f:
                return self.file[line+1:line+i+1], i


    def find_listed_classes(self, lines = [], base_class = None):
        classes = None
        library = base_class
        if type(lines) == str:
            classes = lines.split(',')
            library = base_class
            temp_classes = [(base_class,classes[0].split('import ')[1].strip())]
            if len(classes) > 1:
                for c in classes[1:]:
                    temp_classes.append((base_class,c.strip()))
            classes = temp_classes
            return classes
        elif type(lines) == list:
            if "from" in lines[0]:
                library = base_class
            classes = []
        else:
            library = base_class
            
        
        for i,l in enumerate(lines):
            temp_list = l.split(',')
            for t in temp_list:
                if "from" in t:
                    library = t.split('from')[1].strip()
                    classes.append((library,t.split('import ')[1].strip()))
                else:
                    classes.append((library,t.strip()))
                
        if type(classes) == str:
            return (library,classes)        
        for i,c in enumerate(classes):                     
            if c[1].strip() == "" or c[1].strip() == "(" or c[1].strip() == ")":
                classes.remove(c)
        return classes
            

    #left off here - need to get the function names and locations inside the class, then need to do the same for the import files
    def _find_imports(self, file, source, callback=False):       
        skip_lines = 0
        result_list = []
        self.results_dict = {}
        def _check_imports(l: str):
            try:
                temp = l
                if "import" in l:                
                        if "from" in l:
                            temp = l.split("from ")[1].split(" import ")[0]                     
                            if '(' in l.strip():
                                temp_lines, skip_lines = self.find_end_parenthesis(i)
                                classes = self.find_listed_classes(temp_lines, temp)
                                templist = []
                                for c in classes:
                                    templist.append((inspect.getfile(importlib.import_module(temp)), c[0], c[1]))
                                classes = templist
                                result_list.extend(classes)
                            elif ',' in l:
                                classes = self.find_listed_classes(l, temp)
                                templist = []
                                for c in classes:
                                    templist.append((inspect.getfile(importlib.import_module(temp)), c[0], c[1]))
                                classes = templist
                                result_list.extend(classes)
                            else:
                                result_list.append((temp, l.split("import ")[1].strip()))
                        elif "," in l:
                            classes = self.find_listed_classes(l)
                            for f in classes:
                                try:
                                    self._find_class_file(f[0], source)
                                    if type(f) == tuple:
                                        if f[0] is None:
                                            f = (f[1], None)
                                        module = importlib.import_module(f[0])
                                        file_path = inspect.getfile(module)
                                        result_list.append((file_path,f[0], f[1]))
                                except:
                                    print(os.path.dirname(source))
                                    if os.path.dirname(source) not in sys.path:
                                        _append_sys_path(os.path.dirname(source))
                                    if f[0] is None:
                                        f = (f[1], None)
                                    module = importlib.import_module(f[0])
                                    file_path = inspect.getfile(module)
                                    sys.path = self.sys_path
                                    result_list.append((file_path,f[0], f[1]))
                                    continue
                            print(classes)
                            result_list.extend(classes)
                        else:
                            result_list.append((temp.split("import ")[1].strip(), None))
            except:
                traceback.print_exc()

        

            
        def _append_sys_path(path):
            if path not in sys.path:
                sys.path.append(path)    
        
        

        def _find_classes(l: str, source: str):
            temp = l
            if "class" in l:
                temp = l.split("class ")[1].split("(")[0].strip()
                line = i
                self.results_dict[temp] = {'name': temp, 'functions': {}, 'begin': line,'end':None, 'source': source}
                return self.results_dict[temp], temp
            else:
                return None, None

        def _count_spaces(l: str):
            temp_text = l
            index = 0
            if l[0] == " ":
                while(temp_text[index] == " "):
                    index += 1
                return index
            else:
                return 0

        def find_functions(l: list,start: int, class_name: str):
            start_indent = -1
            start_index = 0
            for i,k in enumerate(l[start:]):
                if k.strip() == "":
                    continue
                if start_indent > -1:
                    if _count_spaces(k) <= start_indent:
                        start_indent = -1
                        self.results_dict[class_name]['functions'][temp] = {'begin': start_index, 'end':start + i - 1}
                        temp = None
                        continue
                if "def " in k and "(" in k:
                    temp = k.split("def ")[1].split("(")[0].strip()
                    start_index = i
                    start_indent = _count_spaces(k)
                    if class_name in self.results_dict.keys():
                        self.results_dict[class_name]['functions'][temp]={'name':temp, 'begin': start + i, 'end': None}
                    
            
        in_class = False
        
        for i,l in enumerate(file):
            
            print(repr(l))
            if skip_lines > 0:
                skip_lines -= 1
                continue
            else:
                temp_lines = None
            if l.strip() == "":
                continue
            temp = l                
            _check_imports(l)
            
            if not in_class:
                if "class" in l:
                
                        
                    in_class = True
                    _,temp = _find_classes(l, source)
                    class_name = temp
                    #class_name = temp
            else:                
                if '    ' in l:
                    print(l, _count_spaces(l))
                else:
                    if _count_spaces(l) < 4:
                        if l.strip()[0] == '#' or l.strip()[0] == '"""' or l.strip()[0] == "'''" or l.strip()[0] == '':
                            continue
                        in_class = False
                        self.results_dict[class_name]['end'] = i - 1
                        
                        temp = None
                        find_functions(file, 0, class_name)
                        class_name = ""
                        in_class = False
                
                
       
                
        return result_list
        

    def _find_class_file(self,class_name: str):
            try:
                print(os.getcwd())
                module = importlib.import_module(class_name)
                file_path = inspect.getfile(module)
                return file_path
            except ImportError:
                return None
            
    def install_package(self, package_name):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"'{package_name}' installed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install '{package_name}'.")          
    
    def _find_recursive_imports(self, file, parent=None):
        if parent is None:
            parent = file
        with open(file, "r") as f:
            lines = f.readlines()
            file_dict = {}
            imports = self._find_imports(lines, os.path.realpath(file))
            
            for i, l in enumerate(imports):
                if len(l) == 2:
                    if l[1] is None:                    
                        if l[0] not in file_dict.keys():
                            file_dict[l[0]] = (l[0], l[1])
                    elif l[1] not in file_dict.keys():
                        path = self._find_class_file(l[0])
                        file_dict[l[1]] = (l[0], path)
                 

                elif len(l) == 3:
                    if l[2] is not None:
                        if l[2] not in file_dict.keys(): 
                            file_dict[l[2]] = (l[1], l[0])
                    else:
                        if l[1] not in file_dict.keys():
                            file_dict[l[1]] = (l[1], l[0])
        self.results_dict[file] = file_dict
        if file_dict == {}:
            return None
        for k,v in file_dict.items():
            print(k,v)
            if v[1] is not None:
                if os.path.exists(v[1]):
                    
                    if v[1] not in sys.path:
                        sys.path.append(v[1])
                    self._find_recursive_imports(v[1], file)
                else:
                    print(f"File {v[1]} does not exist.")
            else:
                if v[0] not in self.files_found:

        return file_dict

                    
                




class DepthSearchFinder:
    def __init__(self, file_path):
        self.file_path = file_path
        self.visited = {}
        self.original_sys_path = sys.path.copy()
        
    def append_sys_path(self, path):
        if path not in sys.path:
            sys.path.append(path)

    def find_file_path(self, module_name):
        try:
            module = importlib.import_module(module_name)
            file_path = inspect.getfile(module)
            return file_path
        except ImportError:
            return None
    
    def find_imports(self, module_name):
        if module_name in self.visited:
            return []
        self.visited.add(module_name)
        try:
            module = importlib.import_module(module_name)
            file_path = inspect.getfile(module)
            if file_path not in self.visited:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    imports = []
                    for line in lines:
                        if line.startswith("import") or line.startswith("from"):
                            imports.append(line.strip())
                    return imports
        except Exception as e:
            print(f"Error importing {module_name}: {e}")
            return []

with open("ytdownloader\\main.py", "r") as file:
    tp = TextParser(file.readlines())
    tp._find_recursive_imports("ytdownloader\\main.py")
    dfs = DepthSearchFinder("ytdownloader\\main.py")
    print(tp.import_list)

        
