#!/usr/bin/python
# fn_stack.py $Revision: 1.6 $ $Date: 2006/02/05 00:45:36 $
# This library contains essential stack related commands.

import objectifier
build_GG_command= objectifier.build_GG_command

# =============== Built In Functions ===========================
internal_syms= dict() # Establish the list of built-in functions.

#STACK COMMANDS
#--------------
def intf_DROPN(E):
    """Drops n objects from the stack."""
    tempUndoList= list()
    n= E.The.StackPop()
    for i in range(int(n.val)):
        if E.The.StackSize(): # Is there something to drop?
            X= E.The.StackPop() # Then drop it.
            tempUndoList.insert(0, X) # Build the undo (backwards).
        else: # Nothing left on the stack. Then just ignore.
            break # No point in attempting more when it's empty.
    tempUndoList.append(n) # Don't forget to return the user's N.
    E.Undo.StackPush( tempUndoList ) # Save it in case of Undo.
intf_DROPN.sd= '... OBn ... OB1 n dropn ==> ...'
internal_syms['dropn']= intf_DROPN # Register function.

# It's obviously highly advantageous to write python functions.
# Time to drop 1e6 objects:    0m51.370s
def intf_DROP(E):
    """Drops one item from the stack."""
    if E.The.StackSize(): # Is there something to drop?
        X= E.The.StackPop()  # Then drop it.
        E.Undo.StackPush( [ X ] ) # Save it in case of Undo.
intf_DROP.sd= '... OB  drop ==> ...'
internal_syms['drop']= intf_DROP # Register 'drop'.
internal_syms['#']= intf_DROP # "Comments look like this."" #

# Time to drop 1e6 objects:   1m40.400s
#internal_syms['drop_gg']= build_GG_command('1 dropn') # Benchmark this.

def intf_CLEAR(E):
    """Clear entire stack."""
    E.Undo.StackPush( E.The.Stacklist ) # Push whole stack list as undo.
    E.The.Stacklist= list()
intf_CLEAR.sd= '... clear ==> <empty stack> '
internal_syms['clear']= intf_CLEAR # Register 'clear'.

def intf_DEPTH(E):
    """Returns the number of items that were on the stack before
    execution."""
    E.The.StackPush( objectifier.StackOB_VAL( E.The.StackSize() ) )
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop') ] )
intf_DEPTH.sd= 'OBn ... OB1 depth ==> OBn ... OB1 n'
internal_syms['depth']= intf_DEPTH # Register 'depth'.

def intf_YANK(E):
    """Takes a number off the stack and then finds that levels object
    (if there  is one) and pulls it down to be the first item on the
    stack. The original is removed."""
    level= E.The.StackPop()
    # This comically allows getting from stack level 3.2, etc.
    grabhere= E.The.StackSize() - int(level.val)
    object2yank= E.The.Stacklist[grabhere]
    del E.The.Stacklist[grabhere]
    E.The.StackPush(object2yank)
    E.Undo.StackPush( [ level, objectifier.StackOB_SYM('placen') ] )
intf_YANK.sd= '... OBn ... OB1 n yank ==> ... OBn+1 OBn-1 ... OB1 OBn'
internal_syms['yank']= intf_YANK # Register function.

def intf_PLACEN(E):
    """Removes a number from the stack that specifies where the next
    stack item should be placed. That item is then put at the specified
    level."""
    level= E.The.StackPop()
    object2put= E.The.StackPop()
    puthere= E.The.StackSize() - int(level.val) + 1
    E.The.Stacklist.insert(puthere, object2put)
    E.Undo.StackPush( [ level, objectifier.StackOB_SYM('yank') ] )
intf_PLACEN.sd= '... OBn ... OB1 n placen ==> ... OBn OB1 OBn-1 ... OB2'
internal_syms['place']= intf_PLACEN # Register function.

def intf_DUPN(E):
    """Duplicate n items of the stack."""
    level= E.The.StackPop()
    n= level.val
    start_at= int(E.The.StackSize()-n)
    # Notice here that this slicing causes a copy of the Python object
    # and not just a copy of the reference. This is lucky here.
    # Update- Actually, this is fine except for lists which are
    # still copied by  reference. This means that wake of one will
    # wake all. This might not be so bad though. PickN has the same issue.
    dupedpart_orig= E.The.Stacklist[start_at:]

    dupedpart_new= list()
    for d in dupedpart_orig:
        if d.whatami == "LST":
            dupedpart_new.append( d.deep_copy() )
        else:
            dupedpart_new.append( d )

    E.The.Stacklist.extend(dupedpart_new)
    E.Undo.StackPush( [ level, objectifier.StackOB_SYM('dropn') ] )
intf_DUPN.sd= '... OBn ... OB1 n dupn ==> ... OBn ... OB1 OBn ... OB1'
internal_syms['dupn']= intf_DUPN # Register function.

def intf_PICKN(E):
    """Picks an object off the stack replacing the level specified
    level number with that level's object. Original is preserved."""
    level= E.The.StackPop() # For future undo use too.
    n= int( E.The.StackSize() - level.val )
    #n -= 1 # Subtract one to account for specifier n itself.
    d= E.The.Stacklist[n]
    if d.whatami == "LST":
        dupedpart_new= d.deep_copy()
    else:
        dupedpart_new= d
    E.The.StackPush( dupedpart_new )
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), level ] )
intf_PICKN.sd= '... OBn ... OB1 n pickn ==> ... OBn ... OB1 OBn'
internal_syms['pickn']= intf_PICKN # Register function.
internal_syms['pick']= intf_PICKN # Register function.

#   ... item_2 item_1 ==> SWAP ==> ... item_1 item_2 (2 YANK | 2 PUT)
internal_syms['swap']= build_GG_command('2 yank')
internal_syms['swap'].__doc__= 'aka: 2 yank'
internal_syms['swap'].sd= '... OB2 OB1 swap ==> ... OB1 OB2'

internal_syms['drop2']= build_GG_command('2 dropn')
internal_syms['drop2'].__doc__= 'aka: 2 dropn'
internal_syms['drop2'].sd= '... OB2 OB1 drop2 ==> ...'

internal_syms['drop3']= build_GG_command('3 dropn')
internal_syms['drop3'].__doc__= 'aka: 3 dropn'
internal_syms['drop3'].sd= '... OB3 OB2 OB1 drop3 ==> ...'

#   ... item_1 ==> DUP ==> ... item_1 item_1 (1 DUPN)
internal_syms['dup']= build_GG_command('1 dupn')
internal_syms['dup'].__doc__= 'aka: 1 dupn'
internal_syms['dup'].sd= '... OB1 dup ==> ... OB1 OB1'

#   ... item_2 item_1 ==> DUP ==> ... item_2 item_1 item_2 item_1 (2 DUPN)
internal_syms['dup2']= build_GG_command('2 dupn')
internal_syms['dup2'].__doc__= 'aka: 2 dupn'
internal_syms['dup2'].sd= '... OB2 OB1 dup ==> ... OB2 OB1 OB2 OB1'

internal_syms['dup3']= build_GG_command('3 dupn')
internal_syms['dup3'].__doc__= 'aka: 3 dupn'
internal_syms['dup3'].sd= '... OB3 OB2 OB1 dup ==> ... OB3 OB2 OB1 OB3 OB2 OB1'

#   ... item_3 item_2 item_1 ==> ROT ==> ... item_2 item_1 item_3 (3 YANK)
internal_syms['rot']= build_GG_command('3 yank')
internal_syms['rot'].__doc__= 'aka: 3 yank'
internal_syms['rot'].sd= '... OB3 OB2 OB1 rot ==> ... OB2 OB1 OB3'

#   ... item_2 item_1 ==> OVER ==> ... item_2 item_1 item_2 (2 PICKN)
internal_syms['over']= build_GG_command('2 pickn')
internal_syms['over'].__doc__= 'aka: 2 pickn'
internal_syms['over'].sd= '... OB2 OB1 over ==> ... OB2 OB1 OB2'
