#!/usr/bin/python3
# objectifier.py $Revision: 1.13 $ $Date: 2005/10/13 18:51:02 $
# This module provides functions to convert parsed tokens into stack
# objects. The stack object classes are defined here.

class StackOb:
    def __init__(self, value):
        self.val= value
        #raw_token_str= None
        self.whatami="unknown"
        self.dead= True
    def __call__(self, evaluator):
        #evaluator.stackpush(self)
        evaluator.evaluate(self)
    def __repr__(self):
        return self.whatami + ':' + str(self.val)
    def __str__(self):
        return self.__repr__()
    def deep_copy(self):
        """There are official __copy__ and __deepcopy__ methods but
        this avoids any unintentional side effects. This one is
        here because copying even a simple object is done by reference
        and even if the LST deep_copy is cool assinging self.val to
        clone.val still makes references, even of VALs and TXTs because
        they are objects, not simple values. This cures that."""
        clone= self.__class__(self.val)
        return clone
    def __nonzero__(self):
        """Standard function that is called to test the truth of the
        object. This allows the value of whatever object to dictate
        the truth of the entire object. Thus empty lists are false and
        null strings are false, and zeros are false, like normal
        python."""
        if self.val:
            return 1
        else:
            return 0

class StackOB_LST(StackOb):
    def __init__(self, value):
        self.val= value
        self.whatami= "LST"
        self.dead= True
        self.names= list()
    def __repr__(self):
        listextras=''
        if 'LST' == self.whatami:
            if self.dead and self.names:
                listextras= ' '.join(self.names)
                listextras= '<'+listextras+'>'
            elif self.dead:
                pass
            else:
                listextras= '<!>'
        return self.whatami+':'+str(self.val)+listextras
    def named_item(self,N):
        """Takes a str name, N, and returns the object contained
        in the list at N's position."""
        if N not in self.names:
            return None
        else:
            i= self.names.index(N)
            if i > len(self.val):
                return None
            else:
                return self.val[i]
    def deep_copy(self):
        """Probably could have used `self.__copy__()` or `self.__deepcopy__()`
        but was unsure about it's other side effects in the current codebase.
        This is just more explicit and solves problems where they need solving.
        Where they don't need solving, ref copy is probably fine - which is why
        the Python team wrote copy that way as default."""
        clone= StackOB_LST(list())
        for v in self.val[:]:
            if v is not None: # Don't bother if it's None
                clone.val.append(v.deep_copy())
        clone.dead= self.dead
        clone.names= self.names[:]
        return clone

class StackOB_SYM(StackOb):
    def __init__(self, value):
        self.val= value
        self.whatami= "SYM"
        self.dead= False
        #self.evaluator= E # in what context does this object exist?
    #def __call__(self):
        #self.evaluator.resolve_symbol_name( self.val )
   #def __nonzero__(self):
        #"""A special truth test for symbols. They are tested for truth
        #based on whether they refer to anything. Yes true, no false."""
        #if self():
        #    return True
        #else:
        #    return False

class StackOB_VAL(StackOb):
    def __init__(self, value):
        self.val= float(value)
        self.whatami= "VAL"
        self.dead= True

class StackOB_TXT(StackOb):
    def __init__(self, value):
        self.val= str(value)
        self.whatami= "TXT"
        self.dead= True

def objectify(token, verbose=None):
    """This takes a token string and converts it into a correct stack
    object by looking for clues left by the tokenizer. If it starts
    with a single quote ('), then it is text. If it starts and ends
    with brackets ([]), then it is a list. If it can be converted to a
    float, then it is a val. Otherwise, it is a symbol."""
    TX_delim= "'"   # Character to delimit text.
    if not token: # Blank null object as in an empty list?
        object= None
    elif TX_delim == token[0]: # TXT object.
        token= str( token[1:] ) # The str is needed for empty strings.
        object= StackOB_TXT(token)
    elif '[' == token[0]: # LST object. Strip brackets.
        # NOTE: It might be smart to have the tokenizer
        #       not bother putting right bracket on the
        #       list token since I'm just pulling them off
        #       here anyway. 
        object= create_list_object(token[1:-1], verbose)
    else:
        try: # Must be a VAL if this works.
            token= float(token)
            object= StackOB_VAL(token)
        except ValueError: # Oh well, must be a SYM.
            object= StackOB_SYM(token)
    return object

def create_list_object(liststr, verbose=None):
    namespacelist= list() # The default.
    if '::' in liststr: # Do this for good measure. Allows this:
        liststr= liststr.replace('::',' :: ') # all[1 2::x y]ok!
    import tokenizer
    Tsub= tokenizer.Tokenizer()
    if verbose:
        Tsub.diagnostic_on()
    Tsub.tokenize_input(liststr)
    tokenQ= Tsub.get_token_queue()
    if '::' in tokenQ:
        if tokenQ.count('::') > 1:
            raise IOError("Only one namespace section (::) allowed!")
        else: # Must be the correctly specified one.
            c= 0 # Counter
            for t in tokenQ: # Loop through tokens of this list content.
                c += 1 # Increment counter
                if '::' == t: # Found a namespace separator?
                    namespacelist= tokenQ[c:]
                    del tokenQ[c-1:]
    object_sublist= list()
    for token in tokenQ:
        if not token is None: # Avoid the `None` that pops up with [], etc.
            object_sublist.append(objectify(token)) # Possibly recursive!
    L= StackOB_LST(object_sublist)
    if '!' in namespacelist:
        L.dead= False
        #L.names= ['!'] # These are important now. Keep them.
    else:
        L.dead= True
    L.names= namespacelist
    return L

# =========== Assemble Built In Functions ======================
def build_GG_command(commandtext):
    """This function takes GeoGad program as a stream of text and
    parses it and forms it into activated lists of objects so that if
    the resulting object is called, it is executed macro style. This
    allows for the creation of built-in commands in both direct Python
    (the normal way) and in GeoGad itself (using this function)."""
    import objectifier
    import tokenizer
    CT= tokenizer.Tokenizer() # Set up a Command Tokenizer.
    CT.tokenize_input(commandtext) # Do it.
    buildinglist= list() # Temp construction list.
    for token in CT.get_token_queue():
        buildinglist.append( objectifier.objectify(token) )
    command_object= objectifier.StackOB_LST( buildinglist )
    command_object.dead= False
    return command_object

