#!/usr/bin/python
# fn_vi.py $Revision: 1.2 $ $Date: 2005/10/09 02:19:09 $
# This library contains functions whose commands are composed of key
# sequences that will be pleasing to people who really love vi.

import objectifier
build_GG_command= objectifier.build_GG_command

# =============== Built In Functions ===========================
internal_syms= dict() # Establish the list of built-in functions.

internal_syms['dd']= build_GG_command('drop')
internal_syms['yy']= build_GG_command('yank')
internal_syms['ggdG']= build_GG_command('clear')
internal_syms['dgg']= build_GG_command('clear')
internal_syms['ZZ']= build_GG_command('exit')

#def intf_MUL(E):
#    """Simple multiplication."""
#    term1= E.The.StackPop().val
#    term2= E.The.StackPop().val
#    E.The.StackPush(objectifier.StackOB_VAL(term1 * term2))
#internal_syms['mul']= intf_MUL # Register function.
    

