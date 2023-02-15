from automata.fa.nfa import NFA

def translate_to_python(input_code):
    lines = input_code.strip().split("\n")
    python_code=[]

    afd = NFA(
        states={'q0','q1','q2','q3'},
        input_symbols={'let', '=',';'},
        transitions={
            'q0':{'let':{'q1'}},
            'q1':{'=':{'q2'}},
            'q2':{';':{'q3'}},
        },
        initial_state = 'q0',
        final_states={'q3'}
    )

    for line in lines:
        tokens = line.split()
        print(tokens)
        if afd.accepts_input(tokens):
            variable = tokens[1]
            value = tokens[2]
            python_code.append(f"{variable} = {value}")
    

    return "\n".join(python_code)

if __name__=="__main__":
    input_code = """
    let x = 5 ;
    let y = 10 ;
    """
    print(translate_to_python(input_code))