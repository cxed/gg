#!/usr/bin/python3
# gg - $Revision: 1.2 $ $Date: 2005/10/02 07:16:59 $
# Chris X Edwards - Copyright 2005 - GNU Public License
# This is the master control progam of the Geometry Gadget system.
# This program will determine where the input is coming from and what
# other runtime configuration is necessary.

# ---------- Option Parsing -----------------------------------------
def load_opt_parser():
    from optparse import OptionParser # For newer versions (2.3.5 works)
    p= OptionParser(
        usage='gg [option] ... [-c cmd | file | -] [arg] ... \n'
             +'Version: $Revision: 1.2 $')

    p.add_option( "-v", "--version", action= "store_true", 
           dest= "info", # variable name to store in.
           help= "output version information",)

    p.add_option( '-w', '--warn', action= 'store_true', 
           dest= 'warn',
           help= 'suppress warnings',) 

    p.add_option( '-c', '--command', action= 'store', 
           dest= 'command',
           help= 'text to execute',) 
    return p.parse_args()

# ---------- Main Program -------------------------------------------
(O, A)= load_opt_parser() # Load (Options, Args).

if O.info:
    O.command= 'version'
if O.command: # Then just execute this stuff.
    import interpreter
    interpreter.command_interpreter( O.command )
else: # Must want interactive shell.
    import interpreter
    if not A or '-' == A[0]: 
        interpreter.interactive_interpreter()
    else: # Must have specified a file.
        print("Loading and running:"+A[0])
        File= open(A[0], 'r')
        interpreter.file_interpreter( File )

# The End!
