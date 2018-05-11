#!/usr/bin/python
# fn_list.py - 2014-04-30
# This library contains functions which relate to management of
# list (LST) objects.

import inc
import objectifier
build_GG_command= objectifier.build_GG_command

# =============== Built In Functions ===========================
internal_syms= dict() # Establish the list of built-in functions.

internal_syms['size']= build_GG_command('len')
internal_syms['list->']= build_GG_command('wake !')
internal_syms['head']= build_GG_command('1 headn')
internal_syms['tail']= build_GG_command('1 tailn')

def intf_HEADN(E):
    """Returns a list or substring made of the first v1 items of a
    list or string (respectively) at v2."""
    if not inc.VAL(E,1) or not inc.listlike(E,2):
    # CHECK THE VAL ON v1.
        print("Input Error: headn")
        print(intf_HEADN.__doc__)
        return # Without doing much of anything.
    n= int(E.The.StackPop().val) # Position.
    ob2= E.The.StackPop() # List or text.
    if ob2.whatami == "TXT":
        out= objectifier.StackOB_TXT( ob2.val[0:n] )
    else:
        out= objectifier.StackOB_LST( ob2.val[0:n] )
    E.The.StackPush(out)
internal_syms['headn']= intf_HEADN # Register function.

def intf_TAILN(E):
    """Returns a list or substring made of the first v1 items of a
    list or string (respectively) at v2."""
    if not inc.VAL(E,1) or not inc.listlike(E,2):
        print("Input Error: tailn")
        print(intf_TAILN.__doc__)
        return # Without doing much of anything.
    n= int(E.The.StackPop().val) # Position.
    ob2= E.The.StackPop() # List or text.
    if ob2.whatami == "TXT":
        out= objectifier.StackOB_TXT( ob2.val[-n:] )
    else:
        out= objectifier.StackOB_LST( ob2.val[-n:] )
    E.The.StackPush(out)
internal_syms['tailn']= intf_TAILN # Register function.

def intf_GET(E):
    """Returns from v2 LST object the value of the list component
    whose position is specified by v1. `[1.1 2.2 3.3 4.4] 3 get -> 3.3`
    See GETN for specifying position by list name.
    """
    if not inc.VAL(E,1) or not inc.listlike(E,2):
        print("Input Error: get")
        print(intf_GET.__doc__)
        return # Without doing much of anything.
    n= int(E.The.StackPop().val) # Position.
    ob2= E.The.StackPop() # List or text.
    oblen= len(ob2.val)
    if oblen < n:
        n= oblen-1
    elif n < 1:
        n= 0
    else:
        n-= 1
    if ob2.whatami == "TXT":
        out= objectifier.StackOB_TXT( ob2.val[n] )
    else:
        out= objectifier.StackOB_LST( ob2.val[n] )
    E.The.StackPush(out)
internal_syms['get']= intf_GET # HP48.

def intf_GETN(E):
    """Returns from v2 LST object the value of the list component
    whose position is specified by v1 where v1 is a name from a named list.
    This can be specified as a SYM or TXT value. The alias is `>>`.
    `[1.1 2.2 3.3 4.4::x y z w] |z getn -> 3.3`
    `[1.1 2.2 3.3 4.4::x y z w] ''y'' >> -> 2.2`
    """
    if not inc.list_and_list_position(E,2,1):
        print("Input Error: getn")
        print(intf_GETN.__doc__)
        return # Without doing much of anything.
    if inc.VAL(E,1): # If a number is tried, hand over to GET.
        intf_GET(E)
        return
    n= E.The.StackPop().val # Name
    lstob= E.The.StackPop() # List or text.
    out= None
    if lstob.whatami == "SYM":
        symkey= lstob.val
        lstob= E.symtab[symkey]
        if n in lstob.names:
            out= lstob.val[lstob.names.index(n)]
    else: # Not a SYM, just a LST.
        out= lstob.named_item(n)
    if out is not None:
        E.The.StackPush(out)
internal_syms['getn']= intf_GETN
internal_syms['>>']= intf_GETN

def intf_PUT(E):
    """Takes list from v3 and a position from v2 and replaces the v3
    item at v2 with the value of v1. This should also take a SYM of a
    list. If that is the case, the output should be nothing but the SYM
    should contain the updated list. If a LST is supplied as v3, then an
    updated list is returned."""
    if not inc.VAL(E,2) or not inc.listlike(E,3):
        print("Input Error: put")
        print(intf_PUT.__doc__)
        return # Without doing much of anything.
    ob1= E.The.StackPop() # List or text.
    n= int(E.The.StackPop().val) # Position.
    ob3= E.The.StackPop() # List or text.
    oblen= len(ob3.val)
    if oblen < n:
        n= oblen-1
    elif n < 1:
        n= 0
    else:
        n-= 1
    if ob3.whatami == "TXT":
        listified= list(ob3.val) # Python strings are immutable.
        listified[n]= ob1.val
        ob3= objectifier.StackOB_TXT( ''.join(listified) )
    else:
        if ob3.whatami == "SYM":
            ref2= E.resolve_symbol(ob3)
            if hasattr(ref2,'whatami') and ref2.whatami == 'LST':
                ref2.val[n]= ob1
            else:
                print("Confusion.")
        else:
            ob3.val[n]= ob1
    E.The.StackPush(ob3)
internal_syms['put']= intf_PUT # HP48.

def intf_PUTN(E):
    """Takes list from v3 and a position from v2 and replaces the v3
    item at v2 with the value of v1. This should also take a SYM of a
    list. If that is the case, the output should be nothing but the SYM
    should contain the updated list. If a LST is supplied as v3, then an
    updated list is returned."""
    if not inc.list_and_list_position(E,3,2):
        print("Input Error: putn")
        print(intf_PUTN.__doc__)
        return # Without doing much of anything.
    if inc.VAL(E,2): # If a number is tried, hand over to PUT.
        intf_PUT(E)
        return
    newob= E.The.StackPop() # New object to insert.
    n= E.The.StackPop().val # Name
    lstob= E.The.StackPop() # List or text.
    symonly= False
    if lstob.whatami == "SYM":
        symkey= lstob.val
        lstob= E.symtab[symkey]
        symonly= True
    if n in lstob.names:
        lstob.val[lstob.names.index(n)]= newob
    if symonly:
        E.symtab[symkey]= lstob
    else:
        E.The.StackPush(lstob)
internal_syms['putn']= intf_PUTN 
internal_syms['<<']= intf_PUTN 

def intf_DECORATE(E):
    """Takes a list from v2 and a name list from v1 and replaces the v2
    list's name space with the value of v1. The name list must be composed
    of only TXT or SYM objects. If they are SYM objects, they are not
    resolved but used as names (the SYMs need not be defined).
    This should also take a SYM of a list. If that is the case, the output
    should be nothing but the SYM should contain the updated list. If a LST is
    supplied as v2, then an updated list is returned. Any existing names are
    lost.
        [1 2 3] [one two three] decorate -> [1 2 3]<one two three>
        [7 8 9] |X sto |X [i j k] decorate X.j -> 8
    """
    if not inc.listlike(E,2) or not inc.LST_of_TXTs_or_SYMs(E.The,1):
        print("Input Error: decorate")
        print(intf_DECORATE.__doc__)
        return # Without doing much of anything.
    noblist= E.The.StackPop().val # Name list
    lstob= E.The.StackPop() # List item.
    symonly= False
    if lstob.whatami == "SYM":
        symkey= lstob.val # This is a problem if X.Y or A=B=VAL
        #lstob= E.symtab[symkey]
        lstob= E.resolve_symbol(lstob)
        symonly= True
    if lstob.whatami == "LST":
        namelist= map(lambda x:x.val, noblist)
        lstob.names= namelist[:]
    if symonly:
        E.symtab[symkey]= lstob
    else:
        E.The.StackPush(lstob)
internal_syms['decorate']= intf_DECORATE 
internal_syms['name']= intf_DECORATE 

def intf_NAMES(E):
    """Takes a list or SYM of a list from v1 and if that list has a name
    component, they are extracted into a separate list as TXT objects. This
    can be used with `repl` and `decorate` to change the naming of items 
    in a list.
         [100 .9784 .8591 .5798::jpy usd franc pound] |money sto
         |money money names 3 [''chf'' ''gbp''] repl decorate
         money -> [100 .9784 .8591 .5798::jpy usd chf gbp]
    """
    if not inc.listlike(E,1):
        print("Input Error: names")
        print(intf_NAMES.__doc__)
        return # Without doing much of anything.
    lstob= E.The.StackPop() # List item.
    if lstob.whatami == "SYM":
        symkey= lstob.val
        lstob= E.symtab[symkey]
    if lstob.whatami == "LST":
        namelist= map(lambda x: objectifier.StackOB_TXT(x) , lstob.names)
        E.The.StackPush( objectifier.StackOB_LST(namelist))
internal_syms['names']= intf_NAMES 

def intf_REPL(E):
    """Takes a string or list object from v3 and a position from v2
    and a replacement string or list object from v1 and replaces the
    portion of v3 starting at v2 with v1. If v2 is less than 1 or
    greater than the `len` of v3, the items are simply concatenated,
    v1+v3 and v3+v1 respectively.
       [5 10 16 21 25] 3 [15 20] -> [5 10 15 20 25]
       ''abcdefghi'' 4 ''XYZ'' repl -> ''abcXYZghi''
    """
    if ( ( not inc.VAL(E,2) or not inc.listlike(E,1) or not inc.listlike(E,3) )
        or ( inc.TXT(E,1) != inc.TXT(E,3) ) ): # If types don't match.
            print("Input Error: repl")
            print(intf_REPL.__doc__)
            return # Without doing much of anything.
    ob1= E.The.StackPop() # Replacement text or list
    n= int(E.The.StackPop().val) # Position.
    ob3ob= E.The.StackPop() # Original list or text.
    outistxt= (ob3ob.val == "TXT")
    oblen= len(ob3ob.val)
    if oblen < n:
        ob3= ob3ob.val+ob1.val
    elif n < 1:
        ob3= ob1.val+ob3ob.val
    else:
        n-= 1
        if outistxt:
            ob3= list(ob3ob.val) # Python strings are immutable.
        else:
            ob3= ob3ob.val
        start= ob3ob.val[0:n]
        plusmid= start + ob1.val
        ob3= plusmid
        if len(plusmid) < oblen:
            ob3+= ob3ob.val[len(plusmid):]
    if outistxt:
        outob= objectifier.StackOB_TXT( ''.join(plusmid) )
    else:
        outob= objectifier.StackOB_LST( ob3 )
    E.The.StackPush(outob)
internal_syms['repl']= intf_REPL # HP48.

def intf_SUB(E):
    """Substring or sublist. Takes a string or list object from v3 and a start
    position from v2 and an end position from v1 and returns the sub-string or
    sub-list (respectively) from v2 to v1. If v1 is less than v2, an empty
    string or list is returned. Any positional value less than 1 is treated as
    1. Any positional value greater than the `len` of v3 will be treated as the
    `len` of v3. The positional values are inclusive such that if v2 is 2 and
    v3 is 4, both the 2nd (and 3rd) and 4th position items will be part of the
    returned sub-object. 
        ''abcdefghijklmnopqrstuvwxyz'' 19 21 sub -> ''stu''
    """
    if not inc.VAL(E,1) or not inc.VAL(E,2) or not inc.listlike(E,3):
        print("Input Error: sub")
        print(intf_SUB.__doc__)
        return # Without doing much of anything.
    n2= int(E.The.StackPop().val) # End position.
    n1= int(E.The.StackPop().val) # Start position.
    ob3= E.The.StackPop() # List or text.
    oblen= len(ob3.val)
    if oblen < n1:
        n1= oblen-1
    elif n1 < 1:
        n1= 0
    else:
        n1-= 1
    if oblen < n2:
        n2= oblen
    elif n2 < 1:
        n2= 0
    else:
        pass # Ok.
    out= ob3.val[n1:n2]
    if ob3.whatami == "LST":
        out= objectifier.StackOB_LST( out )
    elif ob3.whatami == "TXT":
        out= objectifier.StackOB_TXT( out )
    E.The.StackPush(out)
internal_syms['sub']= intf_SUB # HP48.

def intf_POS(E):
    """Takes a LST or TXT item from v2. If v2 is a LST then take an
    item from v1 and return the position v1 is found in v2. If v2 is a
    TXT itme, then v1 must be a TXT item and the value returned is the
    position where the substring v2 is found in v1.
        ''abcdefghijklmnopqrstuvwxyz'' ''stu'' pos -> 19
    """
    # Not sure searching for a list inside a list works, but otherwise fine.
    if ( inc.TXT(E,2) and not inc.TXT(E,1) ) or not inc.listlike(E,2):
        print("Input Error: pos")
        print(intf_POS.__doc__)
        return # Without doing much of anything.
    i= E.The.StackPop() # Item to find.
    ob= E.The.StackPop() # List or text.
    if ob.whatami == "LST":
        vallist= map(lambda x:x.val, ob.val)
        if i.val in vallist:
            p= vallist.index(i.val) + 1
        else:
            p= 0
    elif ob.whatami == "TXT":
        p= ob.val.find(i.val) + 1
    out= objectifier.StackOB_VAL(p)
    E.The.StackPush(out)
internal_syms['pos']= intf_POS # HP48.

def intf_SORT(E):
    """Takes a LST object from v1 and returns a LST object where the
      components of v1 are sorted in ascending order. The items should all
      be TXT or VAL and of the same kind."""
      # Python text sorting= `''.join(sorted([n for n in s]))`
      # Check out MIN and MAX to see how to resolve SYM objects. Not done here yet.
    if not inc.listlike(E,1):
        print("Input Error: sort")
        print(intf_SORT.__doc__)
        return # Without doing much of anything.
    ob1= E.The.StackPop() # List or text.
    if ob1.whatami == "TXT":
        out= objectifier.StackOB_TXT( ''.join(sorted([n for n in ob1.val])) )
    else:
        if ob1.val and len(ob1.val) > 0:
            sortedvals= sorted([x.val for x in ob1.val])
            sortedvals= [objectifier.StackOB_VAL(x) for x in sortedvals]
            out= objectifier.StackOB_LST( sortedvals )
        else:
            out= ob1
    E.The.StackPush(out)
internal_syms['sort']= intf_SORT # Register function.

def intf_REVLIST(E):
    """Takes a LST object from v1 and returns a LST object where
       the components of v1 are reversed in order. This allows for a
       descending sort with `sort reverse`."""
      # Python text sorting= `''.join(sorted([n for n in s]))`
    if not inc.listlike(E,1):
        print("Input Error: revlist")
        print(intf_REVLIST.__doc__)
        return # Without doing much of anything.
    ob1= E.The.StackPop() # List or text.
    if ob1.whatami == "TXT":
        out= objectifier.StackOB_TXT( ob1.val[::-1] )
    else:
        if ob1.val and len(ob1.val) > 0:
            #revedvals= [x.val for x in ob1.val]
            revedvals= ob1.val[:]
            revedvals.reverse()
            out= objectifier.StackOB_LST( revedvals)
        else:
            out= ob1
    E.The.StackPush(out)
internal_syms['revlist']= intf_REVLIST # HP48 command.
internal_syms['rev']= intf_REVLIST # Register function.
