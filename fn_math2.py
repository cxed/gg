#!/usr/bin/python
# fn_math.py $Revision: 1.3 $ $Date: 2014/04/11 04:45:53 $
# This library contains built-in math related functions.

import objectifier
import inc
# This library contains math related functions that all need the
# standard Python math library:
import math

build_GG_command= objectifier.build_GG_command

# =============== Built In Functions ===========================
internal_syms= dict() # Establish the list of built-in functions.

#COMPUTATIONAL
#-------------
# fabs(x) # name abs
def intf_ABS(E):
    """Absolute value."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    answer= objectifier.StackOB_VAL( math.fabs(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['abs']= intf_ABS # Register function.

# floor(x)
def intf_FLOOR(E):
    """Floor, lowest whole integer."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    answer= objectifier.StackOB_VAL( math.floor(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['floor']= intf_FLOOR # Register function.

# ceil(x)
def intf_CEIL(E):
    """Ceiling, highest whole integer."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    answer= objectifier.StackOB_VAL( math.ceil(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['ceil']= intf_CEIL # Register function.

# pow(x,y) # x to the y
def intf_POW(E):
    """Raises the value at level 2 to the value at level 1."""
    orig_num_1= E.The.StackPop() # Preserve this.
    orig_num_2= E.The.StackPop() # Preserve this.
    p= orig_num_1.val # Power part.
    b= orig_num_2.val # Base part.
    try:
        answer= objectifier.StackOB_VAL( math.pow(b,p) )
        E.The.StackPush(answer)
        E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'),
                                      orig_num_2, orig_num_1 ] )
    except ValueError:
        print('sqrt(-) - Second oldest trick in the book!')
        E.The.StackPush( orig_num_2 ) # Run away!
        E.The.StackPush( orig_num_1 ) # Run away!
internal_syms['pow']= intf_POW # Register function.

# XROOT - An HP48 synonym.
internal_syms['xroot']= build_GG_command('inv pow')
internal_syms['xroot'].__doc__= 'aka: inv pow'
internal_syms['xroot'].sd= '... OB2 OB1 xroot ==> ... OB1'

# sqrt(x)
def intf_SQRT(E):
    """Calculates the square root of level one."""
    X= E.The.StackPop() # Preserve this.
    x= X.val # Value of it.
    try:
        answer= objectifier.StackOB_VAL( math.sqrt(x) )
        E.The.StackPush(answer)
        E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
    except ValueError:
        print('sqrt(-) - Second oldest trick in the book!')
        E.The.StackPush( X ) # Run away!
internal_syms['sqrt']= intf_SQRT # Register function.

# SQ - An HP48 synonym.
internal_syms['sq']= build_GG_command('dup *')
internal_syms['sq'].__doc__= 'aka: dup *'
internal_syms['sq'].sd= '... OB1 sq ==> ... OB1'

# hypot(x,y)

# exp(x)

def intf_EXP(E):
    """Constant e to the value of level one."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    answer= objectifier.StackOB_VAL( math.exp(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['exp']= intf_EXP # Register function.

# log(x,b) # the base b logarithm of x
def intf_LOGBASE(E):
    """Logarithm of the value of level 2 with a base of the value of
    level 1."""
    orig_base=  E.The.StackPop() # Preserve in case of badness.
    orig_x=  E.The.StackPop() # Preserve in case of badness.
    b= orig_base.val
    x= orig_x.val
    try:
        E.The.StackPush(
             objectifier.StackOB_VAL( math.log(x,b) ) )
        E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), 
              orig_x, orig_base ] )
    except ZeroDivisionError:
        print('n/0 - Oldest trick in the book!')
        E.The.StackPush( orig_x ) # Run away!
        E.The.StackPush( orig_base ) # Run away!
internal_syms['logbase']= intf_LOGBASE # Register function.

# log(x) # the base e logarithm of x
def intf_LOG(E):
    """Base e logarithm of the value of level one."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    answer= objectifier.StackOB_VAL( math.log(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['log']= intf_LOG # Register function.

# log10(x) # the base 10 logarithm of x
def intf_LOG10(E):
    """Base 10 logarithm of the value of level one."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    answer= objectifier.StackOB_VAL( math.log10(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['log10']= intf_LOG10 # Register function.

# degrees(r)
def intf_2DEG(E):
    """Converts a radian value to degrees."""
    X= E.The.StackPop() # Numeric input object.
    r= X.val # Value of it.
    answer= objectifier.StackOB_VAL( math.degrees(r) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['2deg']= intf_2DEG # Register function.

# radians(d)
def intf_2RAD(E):
    """Sine of level one which should be in degrees."""
    X= E.The.StackPop() # Numeric input object.
    d= X.val # Value of it.
    answer= objectifier.StackOB_VAL( math.radians(d) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['2rad']= intf_2RAD # Register function.

# sin(x)
def intf_SIN(E):
    """Sine of level one which should be in degrees."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    x= math.radians(x)
    answer= objectifier.StackOB_VAL( math.sin(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['sin']= intf_SIN # Register function.

# cos(x)
def intf_COS(E):
    """Cosine of level one which should be in degrees."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    x= math.radians(x)
    answer= objectifier.StackOB_VAL( math.cos(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['cos']= intf_COS # Register function.

# tan(x)
def intf_TAN(E):
    """Tangent of level one which should be in degrees."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    x= math.radians(x)
    answer= objectifier.StackOB_VAL( math.tan(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['tan']= intf_TAN # Register function.

# asin(x)
def intf_ASIN(E):
    """Arcsine of level one."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    x= math.radians(x)
    answer= objectifier.StackOB_VAL( math.asin(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['asin']= intf_ASIN # Register function.

# acos(x)
def intf_ACOS(E):
    """Arccosine of level one."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    x= math.radians(x)
    answer= objectifier.StackOB_VAL( math.acos(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['acos']= intf_ACOS # Register function.

# atan(x)
def intf_ATAN(E):
    """Arctangent of level one in degrees."""
    X= E.The.StackPop() # Numeric input object.
    x= X.val # Value of it.
    answerinrad= math.atan(x)
    answerindeg= math.degrees(answerinrad)
    answer= objectifier.StackOB_VAL( answerindeg )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['atan']= intf_ATAN # Register function.

# atan2(y,x) # atan of y/x with signs considered.
# sinh(x)
# cosh(x)
# tanh(x)
