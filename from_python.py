import re
def is_assignment(string : str):
    pattern = r"^[a-zA-Z_]\w*\s*=\s*.+"
    return True if re.match(pattern, string) else False

def is_output(string : str):
    pattern = r"^print\s*\(.+\)"
    return True if re.match(pattern, string) else False

def is_input(string : str):
    pattern = r"^[a-zA-Z_]\w*\s*=\s*input\(.+\)"
    return True if re.fullmatch(pattern, string) else False

def is_cycle_for(string : str):
    pattern = r"^for\s+\w+\s+in\s+.+:\s*$"
    return True if re.match(pattern, string) else False

def is_cycle_while(string : str):
    pattern = r"^while\s+.+:\s*$"
    return True if re.match(pattern, string) else False

def is_if(string : str):
    pattern = r"^if\s+.+:\s*$"
    return True if re.match(pattern, string) else False


if __name__ == "__main__":
    text = "for i in range(9):"
    #print(is_cycle_for(text))
    with open("./Proyecto/test.py") as file:
        lines = file.readlines()
    
    for line in lines:
        if line.startswith(4*" "):
            line = line.lstrip(" ")
        print(line)
        print(is_output(line))