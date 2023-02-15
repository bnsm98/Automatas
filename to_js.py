from from_python import *
with open("./Proyecto/test.py") as file:
    lines = file.readlines()

result=""

for line in lines:
    if is_assignment(line):
        result += "let " + line.strip("\n") + ";\n"
    if is_output(line.lstrip(" ")):
        result += "console.log("+line.strip(" print()\n")+");\n"


print(result)