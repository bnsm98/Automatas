import numpy as np
import math
import nltk
from nltk import CFG
from nltk.parse.generate import generate
import re
import string
class PyLeX:
    def __init__(self, code):
        """ constraints: used for removing unnecessary code
            raw: dict to store decomposed expressions"""

        self.solved_expr = set()

        self.constraints = [r'\right)', r'\left(']
        self.operators = ['+', '-']
        self.code = code
        self.raw = {}
        self.strings = []
        self.init_utils()
        self.validate(code)
        self.process()

    def push_var(self):
        """ generate capital ascii characters used for put labels """
        for i in range(65, 91):
            yield chr(i)

    def init_utils(self):
        """ clean code purposes"""
        self.matchers = {
            'functions': re.compile(r"""
                            (
                                \\( [^{}]* )\{  (.*)  \}                #most functions like \something{something}
                            )* 
                        """, re.VERBOSE),
            'frac': re.compile(r"""
                            (
                                \\( [^{}]* )\{ (.*) \}\{ (.*) \}        #\frac{}{} like 
                            )*
                        """, re.X),
            'over': re.compile(r"""
                            (
                                \{ (.*) \\over (.*) \}                   
                            )*
                        """, re.VERBOSE),
            'exp': [re.compile(r"""(\{ ([^}]+) \}\^\{ ([^{}]+) \})""", re.VERBOSE),
                    re.compile(r"""(\{ (\\.+\}) \}\^\{ ([^{}]+)\})""", re.VERBOSE)]
        }
        self.labels = self.push_var()  # generator

    def get_matchers(self, name):
        try:
            return self.matchers[name]
        except IndexError:
            print(f"[ERROR] {name} Matcher not implemented yet.")

    def validate(self, latex_code):
        """ validate a given code using a Context-Free Grammar"""
        print(f"[INFO] Input: {latex_code}")
        code = self.format_code(latex_code)
        print(f"[INFO] Processed as: {self.split_code}")
        grammar = CFG.fromstring("""
            S -> '{' S '}' S | '\\' T S | S O S | C S | D S |
            T -> F | O | V 
            F -> 'sin' | 'cos' | 'sqrt' | 'ln'
            O -> '+' | '-' | '^' | '.' | 'cdot' | 'over' | 'frac'
            C -> '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | C C
            V -> 'pi'
            D -> 'e'
            """)
        # try to generate the code
        parser = nltk.ChartParser(grammar)
        for tree in parser.parse(code):
            print(tree.pretty_print())

    def format_code(self, code):
        """ remove extra-code matched by constraints and split the code"""
        for constraint in self.constraints:
            code = code.replace(constraint, '')
        self.code = code
        self.formatter(code)
        return self.split_code

    def formatter(self, code):
        """ format a given str for CFG read, the format is store
        by split_code attr """
        self.split_code = []
        stop_conditions = ['\\', '{', '}', ' ']
        operators = ['^', '+', '-']
        num = ''  # for numbers like 123, 25, etc.

        for index, char in enumerate(code):
            if not char in stop_conditions[:-1]:
                if char.isnumeric():
                    num += char
                elif char == 'e':
                    # this condition is intended to deal with missmatching \over and e
                    it = index - 1
                    if it <= 0:
                        self.split_code.append(char)
                    while it >= 0:  # iterate left till find stop condition or letter
                        if code[it] in stop_conditions:
                            self.split_code.append(char)
                            break
                        elif code[it].isalpha():
                            break
                        it -= 1
                elif char in operators:
                    # first add the remaining number before a operator
                    if num != '':
                        self.split_code.append(num)
                        num = ''
                    self.split_code.append(char)
            else:
                if num != '':
                    self.split_code.append(num)
                    num = ''
                self.split_code.append(char)
                if char == '\\':
                    func = ''
                    for shift_char in code[index + 1:]:
                        if shift_char in stop_conditions or shift_char == code[-1]:
                            if shift_char == code[-1] and shift_char.isalpha():
                                func += shift_char
                            self.split_code.append(func)
                            break
                        func += shift_char

    def process(self):
        """ called respectively functions to decompose and parse the latex input"""
        label = next(self.labels)
        self.raw.setdefault(label, self.code)

        self.expressioner(label)
        self.operacioner()
        print(f"[INFO] Python form: {self.strings[0]}")

    def split_sums(self, secuence):
        """ split into a list all sums or substractions. the list elements are (expr, sign) like"""
        sub_exprs = []
        lbrackets = 0
        rbrackets = 0
        prev_index = 0  # index of previous sub-expression
        sign = '+'
        for index, char in enumerate(secuence):
            if char == '{':
                lbrackets += 1
            if char == '}':
                rbrackets += 1

            if char in self.operators and lbrackets == rbrackets:
                if index > 0:
                    if len(sub_exprs) >= 1:
                        sign = secuence[prev_index - 1]
                    sub_exprs.append(
                        (secuence[prev_index:index], sign))
                    prev_index = index + 1
                else:
                    sign = char
                    prev_index = 1

        if not sub_exprs:  # no operations, hence it's a whole block
            sub_exprs.append((secuence[prev_index:], sign))
        else:
            sub_exprs.append((secuence[prev_index:], secuence[prev_index - 1]))
        sub_exprs = [(expr.replace(' ', ''), sign)
                    for expr, sign in sub_exprs]  # deleting spaces
        return sub_exprs

    def split_cdot(self, secuence):
        """ split concurrencies of \cdot 
            RETURN: list """
        raw_splits = secuence.split('\cdot')
        splits = []
        regroup = ''
        rbrackets = 0
        lbrackets = 0
        for index, expr in enumerate(raw_splits):
            for char in expr:
                if char == '}':
                    rbrackets += 1
                elif char == '{':
                    lbrackets += 1
            if rbrackets == lbrackets:
                if rbrackets == 0:
                    regroup = expr
                else:
                    # regroup = re.sub(r"\\cdot$", '', regroup)
                    regroup += expr
                splits.append(regroup)
                regroup = ''
                rbrackets = 0
                lbrackets = 0
            else:
                regroup += expr + r'\cdot'
        return splits

    def split_exp(self, secuence):
        assert isinstance(secuence, str)
        lbrackets = 0
        rbrackets = 0
        right_index = 0
        previous_index = 0
        splits = []
        for index, char in enumerate(secuence):
            if char == '^':
                lbrackets = 0
                rbrackets = 0
                sub_str = secuence[previous_index:index]
                sub_str = sub_str[::-1]
                for indx, sub_char in enumerate(sub_str):
                    if sub_char == '{':
                        lbrackets += 1
                    elif sub_char == '}':
                        rbrackets += 1

                    if lbrackets == rbrackets:
                        if indx == 0:
                            base = secuence[index - 1]
                        else:
                            rel_index = index - indx
                            last_char = index - 1
                            base = secuence[rel_index:last_char]
                        # start to get exponent
                        lbrackets = 0
                        rbrackets = 0
                        for ind, char_p in enumerate(secuence[index + 1:]):
                            if char_p == '{':
                                lbrackets += 1
                            elif char_p == '}':
                                rbrackets += 1

                            if lbrackets == rbrackets:
                                exp = secuence[index + 2:ind + index + 1]
                                previous_index = ind + index + 2
                                break
                        break
                if base == '':
                    continue
                format_match = r"%s^{%s}" % (base, exp)
                splits.extend([base, exp])
                base = ''
                exp = ''

        if splits:
            return splits
        else:
            return None

    def extract_external_func(self, secuence):
        """ subdivide in one layer a given secuence
        layer: most external function """
        assert isinstance(secuence, str)
        operators = ['+', '-', '^']
        expr_set = set(secuence)
        # make sure not sums, otherwise return None
        if expr_set.intersection(operators) or 'cdot' in secuence:
            operators.extend(['cdot'])
            for op in operators:
                if not op in secuence:
                    continue
                split = secuence.split(op)
                for index, expr in enumerate(split):
                    lbrackets = 0
                    rbrackets = 0
                    for char in expr:
                        if char == '}':
                            rbrackets += 1
                        elif char == '{':
                            lbrackets += 1
                    if lbrackets == rbrackets:
                        if lbrackets == 0:
                            substring = ''.join(split[:index])
                            charity_check = substring.count(
                                '}') + substring.count('{')
                            if charity_check % 2 == 0:
                                return (None, [None])
                            else:
                                continue
                        return (None, [None])  # compatibility

        inner_exprs = []
        groups = None
        if secuence.startswith('\\frac'):
            groups = self.get_matchers('frac').search(secuence).groups()
            func_name = groups[1]
            # append both numerator and denominator
            [inner_exprs.append(expr) for expr in groups[2:4]]

        elif secuence.startswith('\\'):
            groups = self.get_matchers('functions').search(secuence).groups()
            inner_exprs.append(groups[2])  # inner expr of the external layer
            func_name = groups[1]

        elif secuence.startswith(r'{') and '\over' in secuence:
            groups = self.get_matchers('over').search(secuence).groups()
            func_name = 'over'
            # append both numerator and denominator
            [inner_exprs.append(expr) for expr in groups[1:3]]

        if not groups:
            return (None, [None])
        else:
            return (func_name, inner_exprs)

    def expressioner(self, expr_label):
        """ """
        continue_conditions = {'\\', '{', '}'}

        expr = self.raw[expr_label]
        expr = expr.replace(' ', '')
        expr_set = set(expr)

        self.solved_expr.add(expr_label)

        if not continue_conditions.intersection(expr_set) or expr == r'\pi':
            return None

        func_name, inner = self.extract_external_func(expr)

        rel_expr = expr
        rel_expr = rel_expr.replace('over', '$')

        label = next(self.labels)
        prev_lbl = chr(ord(label) - 1)  # get previous lbl

        sum_operations = {'+', '-'}
        multiply_operations = 'cdot'
        exp_operations = '^'

        new_expr = True

        if not func_name:

            if exp_operations in expr:
                sub_exprs = self.split_exp(expr)
                for sub_expr in sub_exprs:

                    if sub_expr in string.ascii_uppercase:
                        new_expr = False
                        continue

                    rel_expr = rel_expr.replace(sub_expr, label)
                    self.raw.setdefault(label, sub_expr)
                    label = next(self.labels)

            elif multiply_operations in expr:
                sub_exprs = self.split_cdot(expr)
                for sub_expr in sub_exprs:
                    rel_expr = rel_expr.replace(sub_expr, label)
                    self.raw.setdefault(label, sub_expr)
                    label = next(self.labels)

            elif sum_operations.intersection(expr_set):
                sub_exprs = self.split_sums(expr)
                for sub_expr, sign in sub_exprs:
                    if sign == '-':
                        sub_expr = '-' + sub_expr
                    rel_expr = rel_expr.replace(sub_expr, label)
                    self.raw.setdefault(label, sub_expr)
                    label = next(self.labels)

        else:
            # turns \frac{}{} patterns into \over
            if 'frac' == func_name:
                matcher = self.get_matchers('frac').search(expr).groups()[0]
                new_form = r"{(%s)\over(%s)}" % (inner[0], inner[1])
                mod_expr = expr.replace(matcher, new_form)
                for lbl, expression in self.raw.items():
                    if matcher in expression:
                        replacement = self.raw[lbl].replace(matcher, new_form)
                        self.raw[lbl] = replacement
                # self.raw[expr_label] = mod_expr
                expr = mod_expr
                rel_expr = mod_expr

            for sub_expr in inner:
                if sub_expr in string.ascii_uppercase:
                    new_expr = False
                    continue

                self.raw.setdefault(label, sub_expr)
                rel_expr = rel_expr.replace(sub_expr, label)
                label = next(self.labels)
            

        if new_expr:
            rel_expr = rel_expr.replace('$', 'over')
            self.raw[expr_label] = rel_expr

        for key in dict(self.raw):

            if key not in self.solved_expr:
                self.expressioner(key)

    def operacioner(self):

        numbered_variables = set()
        ascii_uppercase = set(string.ascii_uppercase)

        for key, value in self.raw.items():

            if isnumber(value):
                numbered_variables.add(key)
            
            elif value in (r'\pi', r'e'):
                self.raw[key] = self.string_to_py(self.raw[key])
                numbered_variables.add(key)

        while not isnumber(self.raw['A']):

            for key, expr in self.raw.items():

                if key in numbered_variables:
                    continue

                for num in set(numbered_variables):

                    if num in expr:
                        self.raw[key] = expr.replace(num, self.raw[num])

                    if not ascii_uppercase.intersection(set(expr)):

                        self.raw[key] = str(
                            eval(self.string_to_py(self.raw[key])))
                        numbered_variables.add(key)

    def string_to_py(self, string):

        # '\\sin{1}' -> math.sin(1)
        # \frac{1}{3} -> 1/3

        original_string = string

        string = string.replace('{', '(')
        string = string.replace('}', ')')

        replacement_keys = [
            '\\sin',
            '\\cos',
            '\\tan',
            '\\cot',
            '\\ln',
            '\\sqrt',
            '^',
            '\\over',
            '\\cdot',
            '\\pi',
            'e',
        ]

        replacement_ops = {
            '\\sin': 'math.sin',
            '\\cos': 'math.cos',
            '\\tan': 'math.tan',
            '\\cot': 'math.cot',
            '\\ln': 'math.log',
            '\\sqrt': 'math.sqrt',
            '\\over': '/',
            '^': '**',
            '\\cdot': '*',
            '\\pi': '3.1415926535',
            'e': '2.71828'
        }

        for op in replacement_keys:

            if op in string:

                string = string.replace(op, replacement_ops[op])
        self.strings.append(string)
        return string

    def get_value(self):
        return float(self.raw['A'])


def isnumber(value):

    try:
        value = float(value) - 1
        return True
    except Exception as e:
        return False

if __name__=="__main__":
    SAMPLE = r'\sqrt{\frac{\pi}{2\cdot \sin{2}}\cdot e}'
    # SAMPLE = r'\sin{\pi}'

    pylex = PyLeX(SAMPLE)

    print(f'[SUCCESS] El resultado de la expresion es: {pylex.get_value()}')