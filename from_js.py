import re
def is_assignment(string : str):
    pattern = r"^(let|var|const)\s+\w+\s*=.*;$"
    return True if re.fullmatch(pattern, string) else False

def is_output(string : str):
    pattern = r"^console\.log\(.+\);$"
    return True if re.fullmatch(pattern, string) else False

def is_input(string : str):
    pattern = r"^(let|var|const)\s+\w+\s*=\s*prompt\(.+\);$"
    return True if re.fullmatch(pattern, string) else False

def is_cycle_for(string : str):
    pattern = r"^for\s*\(\s*.*\s*;\s*.*\s*;\s*.*\s*\)\s*\{.+\}$"
    return True if re.match(pattern, string) else False

def is_cycle_while(string : str):
    pattern = r"^while\s*\(.+\)\s*\{.+\}$"
    return True if re.match(pattern, string) else False

def is_if(string : str):
    pattern = r"^if\s*\(.+\)\s*\{.+\}$"
    return True if re.match(pattern, string) else False

text = "var num1=prompt('Ingresa el primer numero: ');"
print(is_input(text))
