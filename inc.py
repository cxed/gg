#!/usr/bin/python
# inc.py - 2014-04-22
# == Input Checking
# Utility functions for doing input checking. These functions can make it
# easier to preclude error-inducing input.

# Not using this because it may not be a good idea. What if the arg is
# `TXT:?` or `SYM:?`? Tricky.
#def help(S,h):
#    """Utility to check if the first stack item is a ''?'' and if so, 
#    remove it and return a True.
#    Use with something like this:
#    if inc.help(E.The, intf_MMITEM.__doc__): return 
#    """
#    if S.StackSize() >= 1:
#        if S.StackCopyItemLast().val == "?":
#            S.StackPop()
#            print "Help: mmitem\n" + h
#            return True
#    return False

def entid_or_LST_of_entids(S,N):
    """Utility function to check for entities ready to go on the
    stack, either alone as VAL or as a LST of VAL.
    Takes a complete stack and looks at it to make sure that the
    Nth item (N=1 is last, N=2 is penultimate, etc) is either a VAL
    or a list of VALs. This is used many places like ENTPTS, ENTDUP,
    ENTMOVE, ENTROTATE, and ENTERASE. It could be upgraded to resolve
    SYMs too."""
    inputok= False
    if S.StackSize() >= N: 
        # CHECK INPUT #1
        # Check that next ready stack item is a VAL or LST of VALs.
        check= S.StackCopyItemN(N) # Input verification. Next item on stack now.
        if check.whatami == "LST":
            #if not filter(lambda x:x.whatami!="VAL",check.val):
            if all([x.whatami=="VAL" for x in check.val]):
                inputok= True
        elif check.whatami == "VAL":
            inputok= True
    return inputok

def TXT(E,N):
    """Utility function to check for single TXT objects ready to go on the
    stack.
    Takes a complete stack and looks at it to make sure that the
    Nth item (N=1 is last, N=2 is penultimate, etc) is a TXT.
    This is used in places like ENTCHTAG. Could be in MMSAVEAS (but is not).
    It could be upgraded to resolve SYMs too."""
    inputok= False
    if E.The.StackSize() >= N: 
        check= E.The.StackCopyItemN(N) # Input verification. Next item on stack now.
        if is_essentially_a(E,check,"TXT"):
            inputok= True
    return inputok

def VAL(E,N):
    """Utility function to check for single VAL objects ready to go on the
    stack.
    Takes a complete stack and looks at it to make sure that the
    Nth item (N=1 is last, N=2 is penultimate, etc) is a VAL.
    This is used in places like HEADN, TAILN. Could be in MIDN (but is not).
    It could be upgraded to resolve SYMs too."""
    inputok= False
    if E.The.StackSize() >= N: 
        check= E.The.StackCopyItemN(N) # Input verification. Next item on stack now.
        if is_essentially_a(E,check,"VAL"):
            inputok= True
    return inputok

def LST(E,N):
    """Utility function to check for single LST objects ready to go on the
    stack.
    Takes a complete stack and looks at it to make sure that the
    Nth item (N=1 is last, N=2 is penultimate, etc) is a LST.
    This is used in places like MIN, MAX.
    It could be upgraded to resolve SYMs too."""
    inputok= False
    if E.The.StackSize() >= N: 
        check= E.The.StackCopyItemN(N) # Input verification. Next item on stack now.
        if is_essentially_a(E,check,"LST"):
            inputok= True
    return inputok

def is_essentially_a(E,O,T):
    """Takes an evaluator environment, a mystery object, and a type string,
    and figures out if the object is that type or a symbol referring to
    something that would ultimately resolve to that type. The important
    difference here is that this will recursively resolve SYMs to find
    their ultimate destiny and check for correct type."""
    if T not in ["TXT", "SYM", "VAL", "LST"]:
        return False
    isok= False
    if O.whatami == T:
        isok= True
    elif O.whatami == 'SYM':
        final_O= E.resolve_symbol(O)
        if final_O and final_O.whatami == T:
            isok= True
    return isok

def LST_of_VALs(E,N):
    """Utility function to check for single LST objects ready to go on the
    stack which contains only VALs or SYMs to VALs.
    Takes a complete stack and looks at it to make sure that the
    Nth item (N=1 is last, N=2 is penultimate, etc) is a LST.
    This is used in places like MIN, MAX.
    It could be upgraded to resolve SYMs too."""
    inputok= False
    if E.The.StackSize() >= N: 
        check= E.The.StackCopyItemN(N) # Input verification. Next item on stack now.
    if check.whatami == "SYM":
        if is_essentially_a(E,check,"LST"):
            check= E.resolve_symbol(check)
    if check.whatami == "LST" and (check.val is not None):
        #if not filter(lambda x:not is_essentially_a(E,x,'VAL'),check.val): # The crazy Py2 way.
            #inputok= True 
        inputok= all([is_essentially_a(E,x,'VAL') for x in check.val])
    return inputok

def TXT_or_LST_of_TXTs(S,N):
    """Utility function to check for TXT objects ready to go on the
    stack, either alone as TXT or as a LST of TXT.
    Takes a complete stack and looks at it to make sure that the
    Nth item (N=1 is last, N=2 is penultimate, etc) is either a TXT
    or a list of TXTs. This is used in places like ENTTAG.
    It could be upgraded to resolve SYMs too."""
    inputok= False
    if S.StackSize() >= N: 
        # Check that next ready stack item is a VAL or LST of VALs.
        check= S.StackCopyItemN(N) # Input verification. Next item on stack now.
        if check.whatami == "LST":
            #if not filter(lambda x:x.whatami!="TXT",check.val):
            #    inputok= True
            inputok= all([x.whatami=="TXT" for x in check.val])
        elif check.whatami == "TXT":
            inputok= True
    return inputok

def LST_of_TXTs_or_SYMs(S,N):
    """Looks for a list of items that can not be VALs or sub LSTs. This
    is used to check for a decorate list in DECORATE and REDECORATE."""
    inputok= False
    if S.StackSize() >= N: 
        # Check that next ready stack item is a LST of TXTs or SYMs.
        check= S.StackCopyItemN(N) # Input verification. Next item on stack now.
        if check.whatami == "LST":
            #if not filter(lambda x:x.whatami!="TXT" and x.whatami!="SYM",check.val):
            #    inputok= True
            inputok= all([ (is_essentially_a(E,x,'SYM') or is_essentially_a(E,x,'TXT')) for x in check.val])
    return inputok

def listlike(E,N):
    """Utility function to check that a LST object or a TXT object is ready to
    go on the stack v1. This is used in many list like functions like `pos` or `head`
    It could be upgraded to resolve SYMs too."""
    inputok= False
    if E.The.StackSize() >= N: 
        # CHECK INPUT #1
        # Check that next ready stack item is a LST or TXT object.
        check= E.The.StackCopyItemN(N) # Input verification. Next item on stack now.
        if check.whatami == 'SYM':
            if check.val in E.symtab and ( 
                   E.symtab[check.val].whatami == 'LST'
                or E.symtab[check.val].whatami == 'TXT' ):
                inputok= True
        elif check.whatami == "LST":
            inputok= True
            #if not filter(lambda x:x.whatami!="TXT",check.val):
        elif check.whatami == "TXT":
            inputok= True
    return inputok

def list_and_list_position(E,L,P):
    """This checks to see if the stack position L is listlike, and if so is
    P either a VAL or a SYM. If it's a SYM further checks to see that it is
    one of the named parts of the list. The VAL could be range checked here
    too, but sometimes it's correct to return a 0 for operations out of bounds."""
    S= E.The
    inputok1,inputok2= False,False
    if S.StackSize() >= max(L,P): 
        if listlike(E,L):
            inputok1= True
        check2= S.StackCopyItemN(P)
        if check2.whatami == "VAL":
            inputok2= True
        elif check2.whatami == "SYM" or check2.whatami == "TXT":
            check1= S.StackCopyItemN(L)
            if check1.whatami == "TXT":
                inputok2= False # Can't be text. Though this could be upgraded.
            elif check1.whatami == "SYM" and E.symtab[check1.val].whatami == 'LST':
                refto= E.symtab[check1.val]
                if hasattr(refto,'names') and check2.val in refto.names:
                    inputok2= True
            elif hasattr(check1,'names') and check2.val in check1.names:
                inputok2= True
    return inputok1 and inputok2

def point_formatted_LST(S,N):
    """Utility function to check that Nth ready stack item is a LST of 3 VALs.
    This is used for checking user supplied coordinates in functions such as 
    ENTMOVE, MIDN, 
    It could be upgraded to resolve SYMs.
    """
    inputok= False
    check= S.StackCopyItemN(N) # Input verification. Next item on stack now.
    if check.whatami == "LST":
        if len(check.val)==3:
            #if not filter(lambda x:x.whatami!="VAL",check.val):
            if all([x.whatami=="VAL" for x in check.val]):
                inputok= True
    return inputok
