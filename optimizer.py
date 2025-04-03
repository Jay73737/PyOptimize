import os
import inspect
import importlib
import traceback
import subprocess
import sys
class TextParser:


    def __init__(self, main_file = None):
        self.file = main_file
        self.lines_list = None
        self.import_list = []  

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
            


    def find_imports(self, file, source):       
        skip_lines = 0
        temp_lines = None
        classes = []
        result_list = []
        self.results_dict = {}
        def check_imports(l: str):
            temp = l
            if "import" in l:                
                    if "from" in l:
                        temp = l.split("from ")[1].split(" import ")[0]                     
                        if '(' in l.strip():
                            temp_lines, skip_lines = self.find_end_parenthesis(i)
                            classes = self.find_listed_classes(temp_lines, temp)
                            result_list.extend(classes)
                        elif ',' in l:
                            classes = self.find_listed_classes(l, temp)
                            result_list.extend(classes)
                        else:
                            result_list.append((temp, l.split("import ")[1].strip()))
                    elif "," in l:
                        classes = self.find_listed_classes(l)
                        for f in classes:
                            if type(f) == tuple:
                                if f[0] is None:
                                    f = (f[1], None)
                        print(classes)
                        result_list.extend(classes)
                    else:
                        result_list.append((temp.split("import ")[1].strip(), None))
        
        def find_classes(l: str, source: str):
            temp = l
            if "class" in l:
                temp = l.split("class ")[1].split("(")[0].strip()
                line = i
                self.results_dict[temp] = {'name': temp, 'functions': {}, 'begin': line,'end':None, 'source': source}
                return self.results_dict[temp]
            else:
                return None, None

        def count_spaces(l: str):
            if l[0] == " ":
                return count_spaces(l[1:])
            else:
                return len(l) - len(l.lstrip(' '))

        in_class = False
        class_name = ""
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
            check_imports(l)
            if not in_class:
                if "class" in l:
                
                        
                    in_class = True
                    temp = find_classes(l, source)
                    class_name = temp['name']
                    #class_name = temp
            else:                
                if '    ' in l:
                    print(l, count_spaces(l))
                else:
                    if count_spaces(l) < 4:
                        if l.strip()[0] == '#' or l.strip()[0] == '"""' or l.strip()[0] == "'''" or l.strip()[0] == '':
                            continue
                        in_class = False
                        self.results_dict[class_name]['end'] = i - 1
                        
                        temp = None
                        class_name = ""
                        in_class = False
                
                
                    
        return result_list
        
    def install_package(self, package_name):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"'{package_name}' installed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install '{package_name}'.")          
    
    def find_recursive_imports(self, file, parent=None):
        if parent is None:
            parent = file
        with open(file, "r") as f:
            lines = f.readlines()
            file_dict = {}
            imports = self.find_imports(lines, os.path.realpath(file))
            
            for i, l in enumerate(imports):
                try:
                    if l[0] is None:
                        imports[i] = ('self', l[1])
                        continue
                    if l[0] not in file_dict.keys() and l[0] != 'self':# Leave off here, need to find user-made imports for l[0] = none 
                        module = importlib.import_module(l[0])      
                        file_dict[l[0]] = inspect.getfile(module)
                    imports[i] = (l[0], l[1], file_dict[l[0]])
                    
                
                
                
                
                
                
                
                except TypeError as e:                    
                    traceback.print_exc()
                except ModuleNotFoundError as e:
                    print(f"Module '{l[0]}' not found. Installing...")
                    self.install_package(l[0])
                    try:
                        module = importlib.import_module(l[0])
                        file_dict[l[0]] = inspect.getfile(module)
                        imports[i] = (l[0], l[1], file_dict[l[0]])
                    except Exception as e:
                        pass


print(os.getcwd())
with open("ytdownloader\\main.py", "r") as file:
    tp = TextParser(file.readlines())
    tp.find_recursive_imports("ytdownloader\\main.py")

    print(tp.import_list)

        
