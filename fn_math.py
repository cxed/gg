#!/usr/bin/python3
# fn_math.py $Revision: 1.8 $ $Date: 2006/02/05 01:03:45 $
# This library contains built-in math related functions.

import inc
import objectifier
build_GG_command= objectifier.build_GG_command

# =============== Built In Functions ===========================
internal_syms= dict() # Establish the list of built-in functions.

# CONSTANTS
# ---------
internal_syms['e_']= objectifier.StackOB_VAL( 2.7182818284590451 )
internal_syms['pi']= objectifier.StackOB_VAL( 3.1415926535897931 )

# FUNCTIONS
# ---------
def intf_MUL(E):
    """Item multiplication operator where the values are the focus. Compare to
    `:*` where lists are the focus. Valid inputs:
      SYM SYM   + -> (resolve any SYMs and proceed again) 
      VAL VAL * -> simple multiplication
      TXT VAL * -> replication of text into concatenated text, commutative input
      LST_of_VALs VAL * ->  list of each list item multiplied by VAL, commutative input
      LST_of_VALs LST_of_VALs * -> pad smaller with 1 and multiply each ith pos
    If two lists are multiplied, the shorter one is padded with ones to match the other.
    In the case of two lists and both have list names, the longest list's are used. 
    Examples:
      2 2 * -> 4
      2 [1 2 3] * -> [2 4 6]
      31.831 |diameter sto |diameter |pi * -> 100.000035756
      [pi pi pi] pi inv * -> [1 1 1]
      [1 2 3] 2 * -> [2 4 6]
      [1 2 3] [1 2] * -> [1 4 3]  Pad the shorter list with ones.
      [2 2] [4 4 4::x y z] * -> [8 8 4]<x y z>
      [1 2] [1 2 3] * -> [1 4 3]
      4 ''ha'' * -> ''hahahaha''
      ''backwards'' -2 * -> ''sdrawkcabsdrawkcab''
    """
    if not ( 
        ( inc.TXT(E,1) and inc.VAL(E,2) ) or ( inc.VAL(E,1) and inc.TXT(E,2) ) 
        or 
        ( (inc.VAL(E,1) or inc.LST_of_VALs(E,1) ) and
             (inc.VAL(E,2) or inc.LST_of_VALs(E,2) )     ) ):
        print("Input Error: mul")
        print(intf_MUL.__doc__)
        return # Without doing much of anything.
    v2= E.resolve_symbol( E.The.StackPop() )
    v1= E.resolve_symbol( E.The.StackPop() )
    if v1.whatami == 'VAL' and v2.whatami == 'VAL':
        E.The.StackPush(objectifier.StackOB_VAL(v1.val * v2.val))
    elif v1.whatami == "TXT":
        if v2.val < 0: v1.val,v2.val = v1.val[::-1],v2.val*-1 # Do this for `neg`.
        E.The.StackPush(objectifier.StackOB_TXT(v1.val * int(v2.val)))
    elif v2.whatami == "TXT":
        if v1.val < 0: v2.val,v1.val = v2.val[::-1],v1.val*-1 # It's silly, I know.
        E.The.StackPush(objectifier.StackOB_TXT(v2.val * int(v1.val)))
    elif ( (v1.whatami == 'LST' and v2.whatami == 'VAL') or
           (v1.whatami == 'VAL' and v2.whatami == 'LST')   ): # Mixed LST&VAL
        if v1.whatami == 'VAL': v1,v2= v2,v1 # Ensure LST 1st then VAL 2nd
        outlist= list()
        for i in v1.val:
            if i.whatami == 'SYM':
                i= E.resolve_symbol(i)
            outlist.append( objectifier.StackOB_VAL(i.val * v2.val) )
        outlistob= objectifier.StackOB_LST(outlist)
        outlistob.names= v1.names[:]
        E.The.StackPush( outlistob )
    elif v1.whatami == 'LST' and v2.whatami == 'LST':
        lv1,lv2= len(v1.val),len(v2.val)
        if lv1 < lv2:
            v1,v2= v2,v1 # Longest LST first.
            lv1,lv2= lv2,lv1 
        outlist= list()
        for n,i in enumerate(v1.val):
            if i.whatami == 'SYM':
                i= E.resolve_symbol(i)
            if n < lv2:
                if v2.val[n].whatami == 'SYM':
                    froml2= E.resolve_symbol(i)
                else:
                    froml2= v2.val[n]
                outlist.append( objectifier.StackOB_VAL(i.val * froml2.val) )
            else:
                outlist.append( objectifier.StackOB_VAL(i.val) )
        outlistob= objectifier.StackOB_LST(outlist)
        if not v1.names and v2.names: # If both have names go with v1's.
            v1,v2=v2,v1 
        outlistob.names= v1.names[:]
        E.The.StackPush(outlistob)
    else:
        print("Error: What the hell have you done!? This should never have happend. See `intf_MUL`.")
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), v2, v1 ] )
internal_syms['mul']= intf_MUL # Register function.
internal_syms['*']= intf_MUL # Register function.
internal_syms['neg']= build_GG_command('-1 mul')

def intf_LMUL(E):
    """List multiplication operator where lists are the focus. Compare to `*` where
    items are the focus. All SYMs are resolved to their referent. The input
    requires only that v1 or v2 or both must resolve to a VAL. All other
    combinations are valid. A negative VAL as the multiplier will reverse the
    order of mulitplied lists.

        L V :* -> replication of list items in list, commutative
        T V :* -> put text item in list with copies, commutative
        V V :* -> put v2 in list with v1 copies, not commutative

    Examples:

        [1 2 3] 2 :* -> [1 2 3 1 2 3]
        2 [1 2 3] :* -> [1 2 3 1 2 3]
        ''abc'' 2 :* -> [''abc''  ''abc'']
        4 3 :* -> [4 4 4]
        3 4 :* -> [3 3 3 3]
        [0 1] -3 :* -> [1 0 1 0 1 0]
    """
    if not ( inc.VAL(E,1) or inc.VAL(E,2) ):
        print("Input Error: lmul")
        print(intf_LMUL.__doc__)
        return # Without doing much of anything.
    v2= E.resolve_symbol( E.The.StackPop() )
    v1= E.resolve_symbol( E.The.StackPop() )
    if not v2.whatami == 'VAL':
        v1,v2=v2,v1
    if v1.whatami == 'LST':
        outlist= v1.val * abs(int(v2.val))
    else: # Both are vals.
        outlist=  [v1] * abs(int(v2.val))
    if v2.val < 0:
        outlist= outlist[::-1]
    E.The.StackPush( objectifier.StackOB_LST(outlist) )
internal_syms['lmul']= intf_LMUL # Register function.
internal_syms[':*']= intf_LMUL # Register function.

def intf_ADD(E):
    """Item addition operator where the values are the focus. Compare 
    to `:+` where lists are the focus. All SYMs are resolved. Valid inputs:
        TXT TXT + -> concatenate text
        VAL VAL + -> simple addition, commutative
        LST_of_VALs VAL + -> add VAL to all items in list (of values), commutative
        LST_of_VALs LST_of_VALs + -> pad smaller with zero and add each ith pos, commutative
    If two lists are added, the shorter one is padded with zeros to match the other.
    In the case of two lists and both have list names, the longest list's are used. 
    Examples:
        2 2 + -> 4
        |pi pi + 2deg -> 360
        [pi 10::a b] |Q sto -180 2rad Q.a + -> 0
        [4 8] 3 + -> [7 11]
        [4 8] [2 3] + -> [6 11]
        [4 8] [2 3] + -> [6 11]
        [4 8 3] [2 3] + -> [6 11 3]
        [4 8] [1 2 3] + -> [5 10 3] 
        [0 4] [1 2 3] + -> [1 6 3] 
        [1 2 3::a b c] [2 2 2::x y z] + -> [3 4 5]<a b c>
        ''xed'' ''.ch'' + -> ''xed.ch''
    """
    if not ( (inc.TXT(E,1) and inc.TXT(E,2)) or 
            ((inc.VAL(E,1) or inc.LST_of_VALs(E,1)) and
             (inc.VAL(E,2) or inc.LST_of_VALs(E,2)) ) ):
        print("Input Error: add")
        print(inc.LST_of_VALs(E,1))
        print(inc.LST_of_VALs(E,2))
        print(" Value 1:"+str(E.The.StackPop()))
        print(" Value 2:"+str(E.The.StackPop()))
        print(intf_ADD.__doc__)
        return # Without doing much of anything.
    v2= E.resolve_symbol( E.The.StackPop() )
    v1= E.resolve_symbol( E.The.StackPop() )
    if v1.whatami == 'TXT': # v2's been checked.
        E.The.StackPush(objectifier.StackOB_TXT(v1.val + v2.val))
    elif v1.whatami == 'VAL' and v2.whatami == 'VAL':
        E.The.StackPush(objectifier.StackOB_VAL(v1.val + v2.val))
    elif ( (v1.whatami == 'LST' and v2.whatami == 'VAL') or
           (v1.whatami == 'VAL' and v2.whatami == 'LST')   ): # Mixed LST&VAL
        if v1.whatami == 'VAL': v1,v2= v2,v1 # Ensure LST 1st then VAL 2nd
        outlist= list()
        for i in v1.val:
            if i.whatami == 'SYM':
                i= E.resolve_symbol(i)
            outlist.append( objectifier.StackOB_VAL(i.val + v2.val) )
        outlistob= objectifier.StackOB_LST(outlist)
        outlistob.names= v1.names[:]
        E.The.StackPush( outlistob )
    elif v1.whatami == 'LST' and v2.whatami == 'LST':
        lv1,lv2= len(v1.val),len(v2.val)
        if lv1 < lv2:
            v1,v2= v2,v1 # Longest LST first.
            lv1,lv2= lv2,lv1 
        outlist= list()
        for n,i in enumerate(v1.val):
            if i.whatami == 'SYM':
                i= E.resolve_symbol(i)
            if n < lv2:
                if v2.val[n].whatami == 'SYM':
                    froml2= E.resolve_symbol(i)
                else:
                    froml2= v2.val[n]
                outlist.append( objectifier.StackOB_VAL(i.val + froml2.val) )
            else:
                outlist.append( objectifier.StackOB_VAL(i.val) )
        outlistob= objectifier.StackOB_LST(outlist)
        if not v1.names and v2.names: # If both have names go with v1's.
            v1,v2=v2,v1 
        outlistob.names= v1.names[:]
        E.The.StackPush(outlistob)
    else:
        print("Error: What the hell have you done!? This should never have happend. See `intf_ADD`.")
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), v2, v1 ] )
internal_syms['add']= intf_ADD # Register function.
internal_syms['+']= intf_ADD # Register function.
internal_syms['sub']= build_GG_command('neg add')
internal_syms['-']= internal_syms['sub']

def intf_LADD(E):
    """List addition operator where lists are the focus. Compare to `+`
    where items are the focus. Given the existence of v1 and v2, all
    input possibilities are valid. Only SYMs that ultimately refer to LSTs are
    resolved prior to the actual operation. Name space lists are lost.
        L ? :+ -> append item to end of list
        ? L :+ -> prepend item to front of list
        L L :+ -> concatenate lists
        notL notL :+ -> make list containing [notL notL]
    Examples:
        [4 8] 7 :+ -> [4 8 7]
        4 [4 8] :+ -> [4 4 8]
        [1 2 3] |Q sto |Q 4 :+ -> [1 2 3 4]
        [2 ''two''] [3 3 3] :+ -> [2 ''two'' 3 3 3]
        [3 3 3] [2 2] :+ -> [3 3 3 2 2]
        ''listify'' ''me'' :+ [''listify'' ''me'']
    """
    v2= E.The.StackPop() 
    v1= E.The.StackPop() 
    if inc.is_essentially_a(E,v1,'LST'): v1= E.resolve_symbol( v1 )
    if inc.is_essentially_a(E,v2,'LST'): v2= E.resolve_symbol( v2 )
    if not v1.whatami == 'LST' and not v2.whatami == 'LST': # notL notL
        E.The.StackPush(objectifier.StackOB_LST([v1,v2]))
    elif v1.whatami == 'LST' and v2.whatami == 'LST':
        E.The.StackPush(objectifier.StackOB_LST(v1.val + v2.val))
    elif v2.whatami == 'LST': # v1 must be something else.
        E.The.StackPush(objectifier.StackOB_LST([v1] + v2.val))
    elif v1.whatami == 'LST': # v2 must be something else.
        E.The.StackPush(objectifier.StackOB_LST(v1.val + [v2]))
    else:
        print("Error: What the hell have you done!? This should never have happend. See `intf_LADD`.")
internal_syms['ladd']= intf_LADD # Register function.
internal_syms[':+']= intf_LADD # Register function.

def intf_INCR(E):
    """An increment function. Will increment a value by adding 1. Will
    also try to add one to the value of a symbol (leaving nothing).
    Incrementing text will append an extra copy of the last letter of
    the original string. Lists increment by adding another copy of the
    last item."""
    term= E.The.StackPop()
    if term.whatami == 'SYM':
        if E.symtab[term.val].whatami == 'VAL':
            # Needs a new object to break old refs links.
            v= objectifier.StackOB_VAL( E.symtab[term.val].val + 1 )
            E.symtab[term.val]= v
        elif E.symtab[term.val].whatami == 'TXT':
            # Needs a new object to break old refs links.
            t= objectifier.StackOB_TXT( E.symtab[term.val].val +
                                        E.symtab[term.val].val[-1] )
            E.symtab[term.val]= t
        elif E.symtab[term.val].whatami == 'LST':
            # Needs a new object to break old refs links.
            t= objectifier.StackOB_LST( E.symtab[term.val].val +
                                       [E.symtab[term.val].val[-1]] )
            E.symtab[term.val]= t
        elif E.symtab[term.val].whatami == 'SYM':
            pass # This is not complete. Because it's hard.
    elif term.whatami == 'VAL':
        E.The.StackPush(objectifier.StackOB_VAL(term.val + 1))
    elif term.whatami == 'TXT':
        newseq= term.val+term.val[-1]
        E.The.StackPush(objectifier.StackOB_TXT(newseq))
    elif term.whatami == 'LST':
        newseq= term.val + [ term.val[-1] ] # Orig. list + last item.
        E.The.StackPush(objectifier.StackOB_LST(newseq))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), term ] )
internal_syms['++']= intf_INCR # Register function.

def intf_DECR(E):
    """A decrement function. Will decrease a value by subracting 1. Will
    also try to subtract one from the value of a symbol (leaving nothing).
    Decrementing text will remove the last letter of the original
    string. Lists decrement by removing the last item."""
    term= E.The.StackPop()
    if term.whatami == 'SYM':
        if E.symtab[term.val].whatami == 'VAL':
            # Needs a new object to break old refs links.
            v= objectifier.StackOB_VAL( E.symtab[term.val].val - 1 )
            E.symtab[term.val]= v
        elif E.symtab[term.val].whatami == 'TXT':
            # Needs a new object to break old refs links.
            t= objectifier.StackOB_TXT( E.symtab[term.val].val[0:-1] )
            E.symtab[term.val]= t
        elif E.symtab[term.val].whatami == 'LST':
            # Needs a new object to break old refs links.
            t= objectifier.StackOB_LST( E.symtab[term.val].val[0:-1] )
            E.symtab[term.val]= t
        elif E.symtab[term.val].whatami == 'SYM':
            pass # This is not complete. Because it's hard.
    elif term.whatami == 'VAL':
        E.The.StackPush(objectifier.StackOB_VAL(term.val - 1))
    elif term.whatami == 'TXT':
        newseq= term.val[0:-1]
        E.The.StackPush(objectifier.StackOB_TXT(newseq))
    elif term.whatami == 'LST':
        newseq= term.val[0:-1] 
        E.The.StackPush(objectifier.StackOB_LST(newseq))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), term ] )
internal_syms['--']= intf_DECR # Register function.

def intf_DIV(E):
    """Floating point division. Watch that div by zero!"""
    orig_den=  E.The.StackPop() # Preserve in case of badness.
    orig_num=  E.The.StackPop() # Preserve in case of badness.
    if (orig_den.whatami == 'TXT' or orig_num.whatami == 'TXT'): # Refuse text.
        print('Can not divide text.')
        E.The.StackPush( orig_num ) # Run away!
        E.The.StackPush( orig_den ) # Run away!
        return
    elif (orig_den.whatami == 'VAL' and orig_num.whatami == 'LST'): # Numbers/a list.
        outlist= list()
        for i in orig_num.val:
            if i.whatami == 'SYM':
                i= E.resolve_symbol(i)
            if i.whatami == 'TXT':
                i.val= 0
            try:
                outlist.append( objectifier.StackOB_VAL(i.val / orig_den.val) )
            except ZeroDivisionError:
                print('n/0 - Oldest trick in the book!')
                E.The.StackPush( orig_num ) # Run away!
                E.The.StackPush( orig_den ) # Run away!
                return
        outlistob= objectifier.StackOB_LST(outlist)
        outlistob.names= orig_num.names[:]
        E.The.StackPush( outlistob )
    elif (orig_den.whatami == 'LST' and orig_num.whatami == 'VAL'): # A list/numbers.
        outlist= list()
        for po,i in enumerate(orig_den.val):
            if i.whatami == 'SYM':
                i= E.resolve_symbol(i)
            if i.whatami == 'TXT':
                i.val= 0 # Treat text as div by 0.
            try:
                outlist.append( objectifier.StackOB_VAL(orig_num.val / i.val) )
            except ZeroDivisionError:
                print('n/0 at position %d - Oldest trick in the book!' % po)
                E.The.StackPush( orig_den ) # Run away!
                E.The.StackPush( orig_num ) # Run away!
                return
        outlistob= objectifier.StackOB_LST(outlist)
        outlistob.names= orig_den.names[:]
        E.The.StackPush( outlistob )
    elif (orig_den.whatami == 'LST' and orig_num.whatami == 'LST'): # A list/B list.
        outlist= list()
        for po,i in enumerate(orig_den.val):
            j= orig_num.val[po]
            if i.whatami == 'SYM':
                i= E.resolve_symbol(i)
            if j.whatami == 'SYM':
                j= E.resolve_symbol(j)
            if i.whatami == 'TXT':
                i.val= 0 # Treat text as div by 0.
            if j.whatami == 'TXT':
                j.val= 0 # Treat text as div by 0.
            try:
                outlist.append( objectifier.StackOB_VAL(j.val / i.val) )
            except ZeroDivisionError:
                print('n/0 at position %d - Oldest trick in the book!' % po)
                E.The.StackPush( orig_den ) # Run away!
                E.The.StackPush( orig_num ) # Run away!
                return
        outlistob= objectifier.StackOB_LST(outlist)
        outlistob.names= orig_den.names[:]
        E.The.StackPush( outlistob )
    else: # Regular two value division.
        try:
            E.The.StackPush(
                 objectifier.StackOB_VAL(orig_num.val / orig_den.val) )
            E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), orig_num, orig_den] )
        except ZeroDivisionError:
            print('n/0 - Oldest trick in the book!')
            E.The.StackPush( orig_num ) # Run away!
            E.The.StackPush( orig_den ) # Run away!
internal_syms['div']= intf_DIV # Register function.
internal_syms['/']= intf_DIV # Register function.

# This doesn't quite work. It's close though. It doesn't preserve the
# stack through div/0.
internal_syms['inv']= build_GG_command('1 swap div')

def intf_IDIV(E):
    """Needs DIV to come back clean. Doesn't work with lists yet."""
    intf_DIV(E)
    answer=  E.The.StackPop() # 
    if answer.whatami == 'LST':
        print("List integer division, not yet implemented! Using FP division.")
        E.The.StackPush(answer)
    else:
        answer.val= int(answer.val)
        E.The.StackPush(answer)
internal_syms['idiv']= intf_IDIV # Register function.

#MOD
def intf_MOD(E):
    """Software engineer's special - modolo, i.e. remainder. Doesn't work with lists."""
    orig_den=  E.The.StackPop() # Preserve in case of badness.
    orig_num=  E.The.StackPop() # Preserve in case of badness.
    try:
        E.The.StackPush(
            objectifier.StackOB_VAL(
                orig_num.val % orig_den.val) )
        E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), orig_num, orig_den] )
    except ZeroDivisionError:
        print('n/0 - Oldest trick in the book!')
        E.The.StackPush( orig_num ) # Run away!
        E.The.StackPush( orig_den ) # Run away!
internal_syms['mod']= intf_MOD # Register function.

# modf(r,f)
# VECTORS
# -------
#CROSS
#DOT
#VADD
#VSUB

