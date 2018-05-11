#!/usr/bin/python3
# interpreter.py $Revision: 1.13 $ $Date: 2014/04/11 06:20:14 $
# This program represents the simplest user interface to the GeoGad
# system. It will be the preliminary UI for the purpose of accomdating
# development and providing an interface specification.

import tokenizer
import objectifier
import evaluator

def get_user_input(n=''):
    """What to do when it's time to ask the user for more info."""
    if 0 == n: # Don't display depth in prompt...
        n= ''  # ...for first level situations.
    prompt= "gg-"+str(n)+"-> " # Compose user prompt.
    return input(prompt)   # Get line of user input and send it.

def general_interpreter(T, E, input):
    """Core functionality of running the interpreter."""
    try:
        T.tokenize_input(input)
        tokenQ= T.get_token_queue()
        for token in tokenQ:
           thisObject= objectifier.objectify(token,T.diagnostic)
           E.evaluate(thisObject)
    except IOError as errorstring:
        print("That line didn't work. Try again.")
        print(errorstring)
    else:
        E.The.StackDisplay()
        #E.dump_syms()

def interactive_interpreter():
    """Used for playing with the interpreter interactively."""
    import readline # Seems to enhance the input() function.
    # Hmm, how do I get my own completion set?
    #readline.parse_and_bind('tab: complete')
    T= tokenizer.Tokenizer()
    #T.diagnostic_on()
    E= evaluator.Evaluator()
    #E.diagnostic_on()
    E.evaluate( objectifier.StackOB_SYM('version') )
    try:
        user_input= get_user_input() # First time.
        while True:
            if not user_input:
                user_input= E.defaultcommand
            general_interpreter(T, E, user_input)
            promptmark= T.list_depth
            if T.text_mode:
                promptmark= 'T'
            user_input= get_user_input(promptmark) # Within loop.
    except EOFError as errorstring:
        E.evaluate(objectifier.StackOB_SYM('exit'))

def command_interpreter(input):
    """Used for specifying GeoGad commands on the command line."""
    T= tokenizer.Tokenizer()
    #T.diagnostic_on()
    E= evaluator.Evaluator()
    #E.diagnostic_on()
    general_interpreter(T, E, input)

def file_interpreter(file):
    """Used for executing GeoGad commands in a file."""
    T= tokenizer.Tokenizer()
    E= evaluator.Evaluator()
    try:
        file_input= file.readline() # First time.
        while file_input:
            general_interpreter(T, E, file_input.rstrip())
            file_input= file.readline() # Within loop.
    except EOFError as errorstring:
        E.evaluate(objectifier.StackOB_SYM('exit'))
