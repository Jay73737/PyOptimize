import os

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
            library = classes[0].split('import ')[0].split('from')[1].strip()
            classes[0] = classes[0].split('import ')[1].strip()
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
            


    def find_imports(self):       
        skip_lines = 0
        temp_lines = None
        classes = []

        for i,l in enumerate(self.file):
            if skip_lines > 0:
                skip_lines -= 1
                continue
            else:
                temp_lines = None
            if l.strip() == "":
                continue
            temp = l
            
            if "import" in l:                
                if "from" in l:
                    temp = l.split("from ")[1].split(" import ")[0]                     
                    if '(' in l.strip():
                        temp_lines, skip_lines = self.find_end_parenthesis(i)# leave off here - need to separate the classes out into individual components by ,'s 
                        classes = self.find_listed_classes(temp_lines, temp)
                        self.import_list.extend(classes)
                    elif ',' in l:
                        classes = self.find_listed_classes(l, temp)
                        for c in classes:
                            self.import_list.append((temp, c.strip()))
                    else:
                        self.import_list.append((temp, l.split("import ")[1].strip()))
                else:                    
                    self.import_list.append((temp.split("import ")[1].strip(), None))
                
    

print(os.getcwd())
with open("ytdownloader\\main.py", "r") as file:
    tp = TextParser(file.readlines())
 
    tp.find_imports()
    print(tp.import_list)

        
