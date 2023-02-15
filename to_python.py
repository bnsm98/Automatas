"""
Cosas en las que hay que trabajar:
Lo que vaya entre comillas no se tiene que tocar
Cuando la linea acabe en : añadir {} para identificar el bloque
que no quede cadenas de texto de tamaño > 1
"""
from from_python import *

def save_print(string : str):
    r =  ['print','(',')']
    string = string.strip(" ")
    if string.startswith("print"):
        r.insert(2,string[string.find("(")+1:string.find(")")].strip("'").strip('"'))
    return r

def save(string : str):
    if "print" in line:
        new_line = line.strip("() ").split()
    elif line.endswith(":\n"):
        next = lines[lines.index(line)+1]
        if 4*" " in next:
            if is_output(next.lstrip(" ")) or is_assignment(next.lstrip(" ")):
                new_line=line.split()
                new_line.append('{')
                for c in save_print(next):
                    new_line.append(c)
                new_line.append('}')
                lines.remove(next)
            else:
                new_line = save(string)
    else:
        new_line = line.split()
    return new_line

with open("./Proyecto/test.py") as file:
    lines = file.readlines()
for line in lines:
    print(save(line))
