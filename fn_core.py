#!/usr/bin/python3
# fn_core.py $Revision: 1.19 $ $Date: 2006/02/05 06:44:59 $
# This module prepares the internal functions for use by an evaluator.
# This approach allows for different internal sets and schemes to be
# used as requirements change.

internal_syms= dict() # Establish the list of built-in functions.
import objectifier
build_GG_command= objectifier.build_GG_command
import fn_stack
import fn_math
try: # What if there is no math library available...
    import fn_math2
    internal_syms.update(fn_math2.internal_syms)
except ImportError:
    print ("Sorry, no standard Python math library present. "+
           "Some math functions disabled.")
import fn_list
import fn_stat
import fn_vi
import fn_mm

# =============== Built In Functions ===========================
internal_syms.update(fn_stack.internal_syms)
internal_syms.update(fn_math.internal_syms)
internal_syms.update(fn_list.internal_syms)
internal_syms.update(fn_stat.internal_syms)
internal_syms.update(fn_vi.internal_syms)
internal_syms.update(fn_mm.internal_syms)

#def intf_XXX(E):
#    """Builtin Template"""
#    E.The.Stacklist # Work with this.
#internal_syms['xxx']= intf_xxx # Register function.

#internal_syms['xxxx']= build_GG_command('2 yyyy')

#SUPPORT COMMANDS
#----------------
# TODo: Define StackOB_LST of argv.
# TODo: Define functions to adjust settings (verbosity, special chars, etc.)
# TODo: Slices
# TODo: Better organized help - help by concept.
#       Need a xref attrib and an example usage attrib.
# TODo: time, date
# TODo: rand, rseed, nice stat distributions in "import random"
# TODo: factorial, combination, permutation, stddev, variance
# TODo: cd, ls, file_source, file_write, file_append

def intf_HELP(E):
    """Print help message."""
    sortedcommands= list(internal_syms.keys())
    sortedcommands.sort() # Only useful if indexed in order.
    allkeywords= dict() # Collect all keywords.
    for t in sortedcommands: # Go through all functions.
        if hasattr(internal_syms[t],'topic'): # Is there a topic?
            allkeywords[internal_syms[t].topic]= True # Add it.
    allkeywords= allkeywords.keys() # Keys are unique list of topics.
    print(32*'-=')
    print('Active general topics:')
    print(', '.join(allkeywords))
    print()
    print('Active commands:')
    print(', '.join(sortedcommands))
    print()
    print('For help on a particular command use the "?" command:')
    print("... ''helpall'' ? ==> ...")
    print('For help on a general topic use a list with the "?" command:')
    print('... [help] ? ==> ...')
    print(32*'-=')
intf_HELP.topic= 'help'
internal_syms['help']= intf_HELP # Register function.

def intf_HELPALL(E):
    """Print all help information for all commands."""
    sortedcommands= internal_syms.keys()
    sortedcommands.sort() # Only useful if indexed in order.
    for functionname in sortedcommands:
        thefunction= internal_syms[functionname]
        print(4*' '+ functionname )
        if hasattr(thefunction,'sd'): # Is there a stack diagram?
            print(8*' '+ thefunction.sd)
        print(8*' '+ str(thefunction.__doc__))
intf_HELPALL.topic= 'help'
internal_syms['helpall']= intf_HELPALL # Register function.

def intf_HELPITEM(E):
    """Takes one text item or symbol off the stack and if that is a
    command name, displays that command's help information (if any).
    If the object is a list, then the first item of the list is taken
    to be a help topic name and all functions associated with that
    topic are listed."""
    topic= E.The.StackPop() # Should be a string, command name.
    if 'LST' == topic.whatami: # List means that it's a topic name.
        topicname= topic.val[0].val
        print(32*'-=')
        print('=== TOPICNAME: '+topicname+' ===')
        topiclist= list()
        for f in internal_syms.keys():
            if hasattr(internal_syms[f],'topic'): # Is there a topic?
                topiclist.append(internal_syms[f].topic)
        topiclist.sort()
        if topicname in topiclist:
            for f in internal_syms.keys():
                if hasattr(internal_syms[f],'topic'): # Is there a topic?
                    if topicname == internal_syms[f].topic:
                        print(str(f) + ': ')
                        if hasattr(internal_syms[f],'sd'): # Is there a stack diagram?
                            print(str(internal_syms[f].sd))
                        print(internal_syms[f].__doc__)
                        print(32*'-=')
    else: # Must be sym or text
        topic= topic.val # Just get it's value.
        if topic in internal_syms:
            thefunction= internal_syms[topic]
            print(32*'-=')
            print(4*' '+ topic)
            if hasattr(thefunction,'sd'): # Is there a stack diagram?
                print(8*' '+ thefunction.sd)
            print(8*' '+ str(thefunction.__doc__))
            print(32*'-=')
intf_HELPITEM.sd= ' OBsym ==> ' # Stack diagram.
intf_HELPITEM.topic= 'help'
internal_syms['?']= intf_HELPITEM # Register function.

def intf_VERSION(E):
    """Print version information and other administrativa. This
    builtin gets explicitly called at startup."""
    print("=== The Geometry Gadget ===")
    print("    GeoGad Interpreter - Version 103")
    print("    Chris X Edwards  -  www.xed.ch/p/gg")
    print("    Copyright 2005-2018 - GNU Public License")
intf_VERSION.sd= ' ==> ' # Stack diagram.
intf_VERSION.topic= 'info'
internal_syms['version']= intf_VERSION # Register 'version'.

def intf_EXIT(E):
    """Exit the interpreter."""
    intf_EXIT.sd= '... exit ==> <all items lost>'
    print("Thanks! Bye!")
    raise SystemExit
intf_EXIT.sd= '... exit ==> <all items lost>' # Stack diagram.
intf_EXIT.topic= 'system'
internal_syms['exit']= intf_EXIT # Register function.
internal_syms['quit']= intf_EXIT

def intf_SOURCE(E):
    """Source a file of gg command input simulating entering the
    contents of a file into a gg interpreter session. This function
    takes one TXT item which contains the filename.
    ''/fullpath/filename'' source ->"""
    # == Check Input ==
    # Check that there is one TXT item on the stack
    inputok= False # Assume the worst.
    if E.The.StackSize() >= 1: # Ensure something is here.
        # === Check Item #1 ===
        check= E.The.StackCopyItemLast() # Input verification. Next item on stack now.
        if check.whatami == "TXT":
            inputok= True
    if not inputok:
        print("Input Error: source")
        print(intf_SOURCE.__doc__)
        return # Without doing much of anything.
    fn= E.The.StackPop().val
    print("Sourcing from: %s" %fn)
    import interpreter
    Ttemp= interpreter.tokenizer.Tokenizer()
    with open(fn,'r') as f:
        for line_of_gg in f:
            interpreter.general_interpreter(Ttemp,E,line_of_gg.strip())
internal_syms['source']= intf_SOURCE # Register function.

def SimplePushForUndo(E):
    """This function is a bit different. It is not a user function. It
    basically exists to handle any housekeeping needed when no real
    action needs to occur but a value needs to be pushed onto the
    stack. It takes care of loading the Undo list properly, for
    example."""
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop') ] )

def intf_UNDO(E):
    """This function corrects the latest command, except undo itself,
    that was not undone. To undo the undo command itself, see redo. """
    #print("Diagnostic in intf_UNDO  - Before-UNDO Stack:")
    #E.Undo.StackDisplay()
    #print("Diagnostic in intf_UNDO  - Before-REDO Stack:")
    #E.Redo.StackDisplay()
    if not E.Undo.StackIsEmpty():
        Ucommand= objectifier.StackOB_LST(E.Undo.StackPop())
        Ucommand.dead= False
        if E.redoing_now: # Redone commands must be reverse orderd.
            print("Problems here?")
            #Ucommand.val.reverse() # This is odd, but how it is. 
        E.Undo, E.Redo= E.Redo, E.Undo # Cool! When undoing, the undo is redo.
        E.evaluate(Ucommand)
        E.Undo, E.Redo= E.Redo, E.Undo # Ok, now put it back.
    else:
        print("There is nothing to undo!")
    print("Diagnostic in intf_UNDO  - After-UNDO Stack:")
    E.Undo.StackDisplay()
    print("Diagnostic in intf_UNDO  - After-REDO Stack:")
    E.Redo.StackDisplay()
intf_UNDO.sd= '... NewObs undo ==> ... OldObs' # Stack diagram.
intf_UNDO.topic= 'system'
internal_syms['undo']= intf_UNDO # Register 'undo'.

def intf_UNDON(E):
    """Takes a number off the stack and does that many undo
    operations."""
    if not E.The.StackIsEmpty():
        n= E.The.StackPop() # Get number of undos to do.
        E.Redo.StackPush([n]) # Don't lose number if undo is a mistake.
        for i in range(n.val): 
            intf_UNDO(E)
intf_UNDON.sd= '... N undon ==> ... [undo N times]' # Stack diagram.
intf_UNDON.topic= 'system'
internal_syms['undon']= intf_UNDON # Register 'undon'.

def intf_UNDOCHECK(E):
    """This function puts a live list on the stack that represents
    what would happen if an undo was executed. If you want to actually
    proceed with the undo, just eval it. If not, drop it."""
    if not E.Undo.StackIsEmpty():
        back_procedure= objectifier.StackOB_LST(E.Undo.StackPop())
        back_procedure.dead= False # Wake it up for potential action.
        E.The.StackPush( back_procedure ) # Send it out.
    else:
        print("There is nothing to undo!")
intf_UNDOCHECK.sd= '... undocheck ==> ... [next undo command]' # Stack diagram.
intf_UNDOCHECK.topic= 'system'
internal_syms['undocheck']= intf_UNDOCHECK # Register 'undocheck'.

def intf_REDO(E):
    """This function will undo an undo."""
    E.Undo, E.Redo= E.Redo, E.Undo # Cool! When redoing, the undo is redo.
    E.redoing_now= True
    intf_UNDO(E) # Use UNDO as a redo.
    E.redoing_now= False
    E.Undo, E.Redo= E.Redo, E.Undo # Put it back.
intf_REDO.sd= '... redo ==> ... [next redo command]' # Stack diagram.
intf_REDO.topic= 'system'
internal_syms['redo']= intf_REDO # Register 'redo'.

def intf_STO(E):
    """An object is stored in the symbol table as the provided symbol.
    No new object is created. It should now be possible to use
    this function to modify a named component of a list."""
    symname= E.The.StackPop().val
    valobject= E.The.StackPop() 
    # Find object of interest. Since it's an object, it should copy
    # as a reference and setting its `val` should put things in the
    # correct place. That's the theory anyway.
    ooi= E.resolve_complex_symbol(symname)
    if hasattr(ooi,'whatami'): # Was a complex symbol hiding in there.
        if ooi.whatami == valobject.whatami:
            ooi.val= valobject.val # Change the contents where they are.
            if hasattr(valobject,'names'):
                ooi.names= valobject.names # Change the contents where they are.
            return
        else:
            if '.' in symname: 
                # Hmmm. Don't know how to handle: [1 2::a b] |X sto ''T'' |X.b sto
                # Maybe just call it a known limitation because that isn't insane.
                print("Can't assign different types to named sub components with `sto`.")
                print("See `''put'' ?` for a way to do this.""")
    if E.localsyms:
        for locallevel in E.localsyms[::-1]: # Search reversed.
            if symname in locallevel:
                locallevel[symname]= valobject
                return
    #else: Not really an else because a localsyms might exist.
    E.symtab[symname]= valobject #Global table.
intf_STO.sd= '... OB SYM sto ==> ...' # Stack diagram.
intf_STO.topic= 'system'
internal_syms['sto']= intf_STO # Register 'sto'.

def intf_UNSTO(E):
    """This takes a symbol and removes it from the symbol list so that
    resources or confusion associated with that symbol are
    relieved. If there's a local version of this symbol, it alone is
    removed."""
    symname= E.The.StackPop().val
    if E.localsyms:
        for locallevel in E.localsyms[::-1]: # Search reversed.
            if symname in locallevel:
                locallevel[symname]= None
                return
    E.symtab[symname]= None #Global table.
intf_UNSTO.sd= '... SYM unsto ==> ...' # Stack diagram.
internal_syms['unsto']= intf_UNSTO # Register 'unsto'.

def intf_LOCAL_LOAD(E):
    """Local load operation. If this is executed from a live list with
    a namespace, this iterates over each member of the name list and
    loads that local variable with a value pulled from the stack. This
    allows complex functions that take some parameters from the
    stack."""
    if E.localsyms:
        for L in E.localsyms[-1].keys():
             if '!' == L:
                 continue
             stob= E.The.StackPop() # Try to get a stack ob.
             if stob: # If there actually is an object for this...
                 E.localsyms[-1][L]= stob # ...then set it.
             else: # If there's no more stack left...
                 break #...don't waste any more time here.
intf_LOCAL_LOAD.sd= '... OB1 OB2 ... OBn -> ==> ...' # Stack diagram.
intf_LOCAL_LOAD.topic= 'system'
internal_syms['->']= intf_LOCAL_LOAD # Register '->'.

def intf_EVAL(E):
    """Takes an object from the stack and evaluates it as if it were
    not there and re-entered."""
    if E.The.StackSize(): # Is there something to eval?
        object= E.The.StackPop()
        E.evaluate(object)
intf_EVAL.sd= 'OB eval ==> <results>'
intf_EVAL.topic= 'system'
internal_syms['eval']= intf_EVAL # Register 'eval'.
internal_syms['!']= intf_EVAL # Register '!'.

def intf_WAKE(E):
    """Takes a list and returns the same list with an activated
    namespace."""
    object= E.The.StackPop()
    if "LST" == object.whatami:
        object.dead= False
    E.The.StackPush(object)
intf_WAKE.sd= '[1 2 3::x y z] wake ==> [1 2 3::!]'
intf_WAKE.topic= 'system'
internal_syms['wake']= intf_WAKE # Register function.

def intf_INERT(E):
    """Takes a list and returns the same list with an activated
    namespace."""
    object= E.The.StackPop()
    if "LST" == object.whatami:
        object.dead= True
    E.The.StackPush(object)
intf_INERT.sd= '[1 2 3::x y z] inert ==> [1 2 3::!]'
intf_INERT.topic= 'system'
internal_syms['inert']= intf_INERT # Register function.

def intf_2LIST(E):
    """Takes a number n and n more stack objects and produces a
    list of size n."""
    qty= E.The.StackPop().val # The quantity of list to create.
    if qty > E.The.StackSize() or qty < 1:
        qty= E.The.StackSize()
    templist= list()
    while qty:
        templist.append( E.The.StackPop() )
        qty -= 1
    templist.reverse()
    object= objectifier.StackOB_LST(templist)
    object.dead= True
    E.The.StackPush(object)
intf_2LIST.sd= '... OBn ... OB1 n 2list ==> ... [OBn ... OB1]'
intf_2LIST.topic= 'system'
internal_syms['2list']= intf_2LIST # Register function.

def intf_LEN(E):
    """Returns the length of a list or text object."""
    so= E.The.StackPop() # Copy or pop. Hard to say for this.
    if 'LST' == so.whatami or 'TXT' == so.whatami:
        size= objectifier.StackOB_VAL( len(so.val) )
        E.The.StackPush(size) # Put the size on stack.
intf_LEN.sd= '[OB1 ... OBn] len ==> n'
intf_LEN.topic= 'system'
internal_syms['len']= intf_LEN # Register 'depth'.

#FLOW CONTROL
#------------
#def intf_TRUTHTEST(E):
#    """Test function to see how objects are evaluating."""
#    testOb= E.The.StackPop() # Test object.
#    if testOb:
#        print('True :->')
#    else:
#        print('Not true :-<')
#internal_syms['tt']= intf_TRUTHTEST # Register function.

#RANGE 
def intf_RANGE(E):
    """Takes a positive integer off the stack and returns a list
    containing 0 through that number minus 1 in order. To get 1
    through N, try: N range |[++::!] map
    Or this might be easier: N range 1 +
    """
    n= E.The.StackPop() # Magnitude.
    # Make val ojects out of Python's range command.
    r= map(objectifier.StackOB_VAL, range(int(n.val)))
    E.The.StackPush(objectifier.StackOB_LST(r)) # New list on stack.
intf_RANGE.sd= 'N range ==> [1 ... N]'
intf_RANGE.topic= 'flow'
internal_syms['range']= intf_RANGE # Register function.

#REPEAT
def intf_REPEAT(E):
    """Repeat evaluation of level 2 object level 1 times."""
    N= int( E.The.StackPop().val ) # Number of times to iterate.
    O= E.The.StackPop() # The thing to repeat.
    for n in range(N): # Iterate N times.
        O(E) # Evaluate the object - cool!
intf_REPEAT.sd= 'OB N repeat ==> <results of OB evaluated n times>'
intf_REPEAT.topic= 'flow'
internal_syms['repeat']= intf_REPEAT # Register function.

#IF
def intf_IF(E):
    """Evaluate level 1 object if level 2 is true."""
    executeOb= E.The.StackPop() # Evaluation object.
    testOb= E.The.StackPop() # Test object.
    if testOb:
        #print("It's true!" # Just to help diagnose things.)
        executeOb(E) # Evaluate the object - cool!
intf_IF.sd= 'OBtest OBaction if ==> <results of OBa if OBtest is true>'
intf_IF.topic= 'flow'
internal_syms['if']= intf_IF # Register function.

#IFELSE
def intf_IFELSE(E):
    """Evaluate level 2 object if level 3 is true, evaluate level 1
    object if level 3 is false."""
    FexecuteOb= E.The.StackPop() # False evaluation object.
    TexecuteOb= E.The.StackPop() # True evaluation object.
    testOb= E.The.StackPop() # Test object.
    if testOb:
        #print("It's true!" # Just to help diagnose things.)
        TexecuteOb(E) # Evaluate the object - cool!
    else:
        #print("It's False!" # Just to help diagnose things.)
        FexecuteOb(E) # Evaluate the object - cool!
intf_IFELSE.sd= 'OBtest OBactionT OBactionF ifelse ==> <eval OBt if true, OBf if false>'
intf_IFELSE.topic= 'flow'
internal_syms['ifelse']= intf_IFELSE # Register function.

#WHILE
def intf_WHILE(E):
    """[ACTION] [TEST] while"""
    action= E.The.StackPop() # Action object.
    yesorno= E.The.StackPop() # Test.
    yesorno(E) # Run the test.
    try:
        while E.The.StackPop():
            action(E) # Do the action.
            yesorno(E) # Run the test.
    except KeyboardInterrupt:
        print("Getting out of hand?")
intf_WHILE.sd= 'OBtest OBaction while ==> <evaluate until OBtest eval is false>'
intf_WHILE.topic= 'flow'
internal_syms['while']= intf_WHILE # Register function.

#FOREACH
#FOR 
def intf_FOR(E):
    """Take two objects off the stack comprising of a list and an
    action object. For each item in the list, put that item on the
    stack and then evaluate the function object. Notice that this is
    more like the Python for or the Perl foreach than the C for. If
    you want a C for loop such as:
        for (i=20; i<50; i+=6) {leave_num_on_stack();}
    try this:
        20 |i sto |[i 50 <::!] |[i i 6 + |i sto::!] while"""
    fn= E.The.StackPop() # The function part.
    li= E.The.StackPop() # The list part.
    if "LST" == li.whatami:
        for i in li.val: # li.val being a list.
            E.The.StackPush(i) # Put the ith list item on stack alone.
            E.evaluate(fn)     # Evaluate the function object.
intf_FOR.sd= 'OBlist OBaction for ==> <action evaluated for all in list>'
intf_FOR.topic= 'flow'
internal_syms['for']= intf_FOR # Register function.
internal_syms['foreach']= intf_FOR # Register function.

#MAP 
def intf_MAP(E):
    """Take two objects off the stack, an object to perform some
    function on other objects and a list of those other objects. For
    each item in the list, put that item on the stack and then evaluate
    the function object. At the end, put all the stack items into a
    list except for the first n items where n is the size of the stack
    before the map command or its arguments were introduced. In
    English, this means that if you have a stack with some original
    items, those should remain on the stack after the map, but all of
    the objects the mapped function may produce will be rounded up
    into a list. Now the weird thing is that it is possible to
    have your mapped function eat more levels off the stack than just
    the one of the list. In that case, you could have a stack be
    smaller than n+1 items where n is the number of original items."""
    fn= E.The.StackPop() # The function part.
    li= E.The.StackPop() # The list part.
    Ns= E.The.StackSize() # Starting items on the stack unrelated to the mapping.
    if "LST" == li.whatami:
        for i in li.val: # li.val being a list.
            E.The.StackPush(i) # Put the ith list item on stack alone.
            E.evaluate(fn)     # Evaluate the function object.
    Ne= E.The.StackSize() # Ending items on the stack with mapping.
    net= Ne-Ns # Net object gain/loss.
    if net > 0: # If stuff was actually added.
        E.The.StackPush(objectifier.StackOB_VAL(net)) # Number of list items.
        intf_2LIST(E) # Make a list using that perfectly good function.
intf_MAP.sd= 'OBlist OBaction map ==> [list of action applied to each in OBlist]'
intf_MAP.topic= 'flow'
internal_syms['map']= intf_MAP # Register function.

#FILTER 
def intf_FILTER(E):
    """Take two objects off the stack, an object to perform some
    function on other objects and a list of those other objects. For
    each item in the list, put that item on the stack twice and then evaluate
    the function object. Then do an if. If the function object made a
    true value, then the copy will remain, if not, it goes. At the
    end, put all the stack items into a list except for the first n
    items where n is the size of the stack before the filter command or
    its arguments were introduced. In English, this means that if you
    have a stack with some original items, those should remain on the
    stack after the filter, but all of the objects the mapped function
    may produce will be rounded up into a list. Now the weird thing is
    that it is possible to have your filter function eat more levels
    off the stack than just the one of the list. In that case, you
    could have a stack be smaller than n+1 items where n is the number
    of original items. Example:
          1 |[dup 30 <::!] |[dup ++::!] while 0 2list |[7 mod not::!] filter -->
          LST:[VAL:7.0, VAL:14.0, VAL:21.0, VAL:28.0]"""
    fn= E.The.StackPop() # The function part.
    li= E.The.StackPop() # The list part.
    Ns= E.The.StackSize() # Starting items on the stack unrelated to the mapping.
    if "LST" == li.whatami:
        for i in li.val: # li.val being a list.
            E.The.StackPush(i) # Put the ith list item on stack alone.
            E.evaluate(fn)     # Evaluate the function object.
            E.The.StackPush(i) # Put the ith list item on stack alone.
            intf_IF(E)
    Ne= E.The.StackSize() # Ending items on the stack with mapping.
    net= Ne-Ns # Net object gain/loss.
    if net > 0: # If stuff was actually added.
        E.The.StackPush(objectifier.StackOB_VAL(net)) # Number of list items.
        intf_2LIST(E) # Make a list using that perfectly good function.
            #TorF= E.The.StackPop() # The true/false aspect of this item.
            #resultlist= [] # Start a result list.
            #if TorF: # If it is indeed true, add it.
            #    resultlist.append(i)
        #if resultlist:
            #E.The.StackPush(objectifier.StackOB_LST(resultlist)) # Number of list items.
intf_FILTER.sd= 'OBlist OBaction filter ==> [OBlist items where action makes true]'
intf_FILTER.topic= 'flow'
internal_syms['filter']= intf_FILTER # Register function.


#BREAK
#CONTINUE

#GT
def intf_GT(E):
    """True if level 2 is 'greater than' level 1."""
    B= E.The.StackPop() # Test object 2.
    A= E.The.StackPop() # Test object 1.
    if A.val > B.val:
        E.The.StackPush(objectifier.StackOB_VAL(1))
    else:
        E.The.StackPush(objectifier.StackOB_VAL(0))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), A, B ] )
intf_GT.sd= 'OB2 OB1 gt ==> <1|O>'
intf_GT.topic= 'logic'
internal_syms['gt']= intf_GT # Register function.
internal_syms['>']= intf_GT # Register function.

#LT
def intf_LT(E):
    """True if level 2 is 'less than' level 1."""
    B= E.The.StackPop().val # Test object 2.
    A= E.The.StackPop().val # Test object 1.
    if A < B:
        E.The.StackPush(objectifier.StackOB_VAL(1))
    else:
        E.The.StackPush(objectifier.StackOB_VAL(0))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), A, B ] )
intf_LT.sd= 'OB2 OB1 lt ==> <1|O>'
intf_LT.topic= 'logic'
internal_syms['lt']= intf_LT # Register function.
internal_syms['<']= intf_LT # Register function.

#LE
def intf_LE(E):
    """True if level 2 is 'less than or equal' to level 1."""
    B= E.The.StackPop().val # Test object 2.
    A= E.The.StackPop().val # Test object 1.
    if A <= B:
        E.The.StackPush(objectifier.StackOB_VAL(1))
    else:
        E.The.StackPush(objectifier.StackOB_VAL(0))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), A, B ] )
intf_LE.sd= 'OB2 OB1 le ==> <1|O>'
intf_LE.topic= 'logic'
internal_syms['le']= intf_LE # Register function.
internal_syms['<=']= intf_LE # Register function.

#GE
def intf_GE(E):
    """True if level 2 is 'greater than or equal' to level 1."""
    B= E.The.StackPop().val # Test object 2.
    A= E.The.StackPop().val # Test object 1.
    if A >= B:
        E.The.StackPush(objectifier.StackOB_VAL(1))
    else:
        E.The.StackPush(objectifier.StackOB_VAL(0))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), A, B ] )
intf_GE.sd= 'OB2 OB1 ge ==> <1|O>'
intf_GE.topic= 'logic'
internal_syms['ge']= intf_GE # Register function.
internal_syms['>=']= intf_GE # Register function.

#EQ
def intf_EQ(E):
    """True if level 1 and level 2 are 'equal'."""
    B= E.The.StackPop().val # Test object 2.
    A= E.The.StackPop().val # Test object 1.
    if A == B:
        E.The.StackPush(objectifier.StackOB_VAL(1))
    else:
        E.The.StackPush(objectifier.StackOB_VAL(0))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), A, B ] )
intf_EQ.sd= 'OB2 OB1 == ==> <1|O>'
intf_EQ.topic= 'logic'
internal_syms['eq']= intf_EQ # Register function.
internal_syms['==']= intf_EQ # Register function.
internal_syms['same']= intf_EQ # Register function.
internal_syms['ne']= build_GG_command('eq not')
internal_syms['=']= intf_EQ # Why not? This error doesn't exist here!

#NOT t->F, f->T
def intf_NOT(E):
    """Logical 'not' of level 1."""
    A= E.The.StackPop() # Test object.
    if A:
        E.The.StackPush(objectifier.StackOB_VAL(0))
    else:
        E.The.StackPush(objectifier.StackOB_VAL(1))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), A ] )
intf_NOT.sd= 'OB2 OB1 not ==> <1|O>'
intf_NOT.topic= 'logic'
internal_syms['not']= intf_NOT # Register function.

#AND t t->T, t f->F, f t->F, f f->F
def intf_AND(E):
    """Logical 'and' of levels 1 and 2."""
    A= E.The.StackPop() # Test object.
    B= E.The.StackPop() # Evaluation object.
    if A and B:
        E.The.StackPush(objectifier.StackOB_VAL(1))
    else:
        E.The.StackPush(objectifier.StackOB_VAL(0))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), A, B ] )
intf_AND.sd= 'OB2 OB1 and ==> <1|O>'
intf_AND.topic= 'logic'
internal_syms['and']= intf_AND # Register function.
internal_syms['nand']= build_GG_command('and not')

#OR t t->T, t f->T, f t->T, f f->F
def intf_OR(E):
    """Logical 'or' of levels 1 and 2."""
    A= E.The.StackPop() # Test object.
    B= E.The.StackPop() # Evaluation object.
    if A or B:
        E.The.StackPush(objectifier.StackOB_VAL(1))
    else:
        E.The.StackPush(objectifier.StackOB_VAL(0))
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), A, B ] )
intf_OR.sd= 'OB2 OB1 or ==> <1|O>'
internal_syms['or']= intf_OR # Register function.
internal_syms['nor']= build_GG_command('or not')
#XOR t t->F, t f->T, f t->T, f f->F
internal_syms['xor']= build_GG_command('dup2 or 3 placen not swap not or and')
internal_syms['xnor']= build_GG_command('xor not')

