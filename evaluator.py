#!/usr/bin/python3
# evaluator.py $Revision: 1.19 $ $Date: 2014/04/11 06:20:14 $
# This module can take stack objects (created by the objectifier) and
# do the correct thing with them. This includes functions like placing
# on the stack, dereferencing symbols, executing builtins and weak
# lists. This is where the stack (TheStack) and symbol table (symtab)
# are defined.

# Load the internal functions (builtins).
#import internals
import fn_core

class Stack:
    """Although this can be used where needed, its primary place is to
    produce the object that will be the main stack for the system. By
    making this a separate class, interesting things with multiples
    stacks can be done. The special thing about this class as opposed
    to just using a list is that it comes with a bunch of utility
    functions."""
    def __init__(self):
        self.Stacklist= list() # Actually holds the data.

    def StackPush(self,O):
        """Put an object on the end of the stack. Shift the other
        objects one place. Basically a normal push."""
        self.Stacklist.append(O)

    def StackSize(self):
        """Returns how many items are on the stack."""
        return len(self.Stacklist)

    def StackIsEmpty(self):
        """Check if the stack is empty. True if empty."""
        if self.StackSize() < 1:
            return True
        else:
            return False

    def StackCopyItemN(self,N):
        """Leave stack unmodified, but return a copy from
        (LILO) end minus N."""
        #depth += 1
        #taillist= self.Stacklist[len(self.Stacklist)-depth:]
        #if len(taillist) > 1:
            #return taillist
        #else:
            #return taillist[0]
        if self.StackIsEmpty():
            return None 
        else:
            obatN= self.Stacklist[-N]
            if obatN.whatami == "LST": # Then true deep *copy* is needed.
               return obatN.deep_copy() 
            return obatN

    def StackCopyItemLast(self):
        """Leave stack unmodified, but return copy of last object from
        (LILO) end."""
        return self.StackCopyItemN(1)
        if self.StackIsEmpty():
            return None 
        else:
            return self.Stacklist[-1]

    def StackPop(self, depth=1):
        """Delete and return the last 'depth' items."""
        # Ok, for now, it just pops one.
        if self.StackIsEmpty():
            return None 
        else:
            return self.Stacklist.pop()

    def StackDisplay(self):
        """Show the current state of the stack."""
        lev= len(self.Stacklist)
        if lev:
            print("      /--------------------")
            #print("      | Stack State...")
            #print("      |--------------------")
            for n in self.Stacklist:
                print('      | ('+ str(lev) + ') ' + str(n))
                lev -= 1
            print('      \--------------------')
        else:
            print('      ** Empty Stack **')

class Evaluator:
    """This class creates instances of complete processing engines. If
    desired, there can be multiple evaluators each with their own
    stack and symbol table. This might be helpful if creating an
    interface with multiple stacks or named stacks or even just to
    open a separate evaluator to read in and process a stream of
    commands from a file without disturbing normal interaction."""
    def __init__(self):
        self.symtab= fn_core.internal_syms
        self.localsyms= list() # A list of dicts, new dict every level.
        self.The= Stack() # It's THE (user) stack; the name works in context.
        self.defaultcommand= 'dup' # Use as input when there is none.
        self.Undo= Stack() # A stack for record of how to undo.
        self.Redo= Stack() # A stack for record of how to redo.
        self.redoing_now= False # Flag to know if currently in REDO mode.
        self.diagnostic= False

    def diagnostic_on(self):
        self.diagnostic= True

    def dump_syms(self):
        """Useful to diagnose annoying symbol problems. Also a template
        for preserving the symbols in a full-featured save."""
        for k in sorted(self.symtab.keys()):
            if "vw" in k:
                print("%s = %s" % (k, repr(self.symtab[k])))

    def loadlocals(self, names):
        # Use a list comprehension to create a list of None
        self.localsyms.append(
            dict(zip(names,[ None
                             for z in range(len(names))     ])) )

    def resolve_symbol_name(self, symname):
        """This function is just like resolve_symbol but it takes a
        string and not an actual symbol object. This name should be
        in the symtab or a None is produced."""
        for locallevel in self.localsyms[::-1]: # Search reversed.
            if symname in locallevel:
                return locallevel[symname]
        if symname in self.symtab:
            return self.symtab[symname]
        else:
            return None

    def resolve_complex_symbol(self, symname):
        """This function specializes in handling the complex symbol
        addressing scheme which can pick out named variables from
        lists. So if a list looks like this: [[1 2::x y][3 4::x y]::p1 p2]
        and is stored as variable A, then A.p1.y should resolve to 2."""
        subsymnamelist= list() # Where the components of the complex sym go.
        while '.' in symname: # Pull apart complex sym into a list.
            position= symname.index('.') # Find first sub symbol.
            subsymnamelist.append( symname[0:position] ) # Pull it out.
            symname= symname[position+1:] # Reset symbol without it.
        subsymnamelist.append( symname ) # Don't forget the final one.
        # Now there will be a list:['root', 'sub1', ... , 'subN']
        # The first entry (root) should be in the symtab - get it.
        rootsym= self.resolve_symbol_name( subsymnamelist[0] )
        currentob= rootsym # Start here and defualt if nothing found.
        count= 1 # Initialize the counter for the iteration (plus 1).
        for part in subsymnamelist[:-1]: # The last one won't have a sub.
            nextpartname= subsymnamelist[count]
            # Is this actually undef'd? I.e. referred to by undef'd sym?
            if not hasattr(currentob, 'whatami'):
                print("I respect your creativity but that's not really defined.")
                return None
            # Is this object a sym? If so, it might resolve to a list.
            if 'SYM' == currentob.whatami: # If a symbol, cash it in.
                currentob= self.resolve_symbol_name(currentob.val) 
            # Is this a list? If not, then being here is all invalid.
            if not 'LST' == currentob.whatami:
                return currentob # Whatever it is,  spit it out and stop.
            # Does the list have the next part in its namespacelist?
            if nextpartname in currentob.names: # Next symbol is found...
                #...in this list's namespace. Figure out the position.
                where= currentob.names.index(nextpartname)
                if where < len(currentob.val):
                    currentob= currentob.val[where]
                else:
                    print ("I respect your creativity but there doesn't seem to be a '%s'."
                            % currentob.names[where] )
                    return None
            else: # It's a list, but the subpart isn't in the namespace.
                return currentob # So punt here too.
            count += 1 # Advance the counter.
        return currentob

    def resolve_symbol(self, sym):
        """If an object is known to be a symbol, this function takes
        care of it including namespace combinations which can use this
        function recursively. This function also manages the stack. If
        the sym should be protected and put on the stack, this
        happens, so don't use this function where that's inappropriate.
        This should return the ultimate object the symbol refers to or None.
        If the input is not a SYM then just return that object."""
        outob= None # Default is no referent object needs to be processed.
        if not sym.whatami == 'SYM': # Easiest case - it's not even a sym...
            outob= sym               # ...send it back.
        #print("resolve_symbol:" + sym.val)
        elif "|" == sym.val: # Is it the protection char?
            self.The.StackPush(sym) # Send on through.
        # Sym preceeded by |? Push without resolving.
        elif not self.The.StackIsEmpty() and "|" == self.The.StackCopyItemLast().val:
            self.The.StackPop() # Get rid of the protection char.
            self.The.StackPush(sym) # Put the symbol in its place.
        else: # Resolve SYM...
            # Simple case the sym is found.
            trylookup= self.resolve_symbol_name( sym.val )
            if trylookup is not None: # Did that find something?
                outob= trylookup # Yes? Then finished.
            # Then maybe it calls namespace positions.
            elif (sym.val.count('.') # Must _contain_ the dot.
                  and not ( sym.val.startswith('.') 
                       or sym.val.endswith('.') ) ):
                outob= self.resolve_complex_symbol(sym.val)
            else: # This should go to STDERR.
                print('Warning: '+ sym.val +' is not defined.')
        if hasattr(outob,'whatami') and outob.whatami == 'SYM': # Dig deeper.
            outob= self.resolve_symbol(outob)
        return outob 

    def evaluate(self,object):
        """All input goes through this function which decides its fate."""
        # These sneak through with complex parsing. Just ignore Nones, but not 0!
        if object is None: return
        if self.diagnostic:
            print(object.whatami + ":" + str( object.val ))
        if "VAL" == object.whatami or "TXT" == object.whatami:
            self.The.StackPush(object) # Always push simple objects.
            fn_core.SimplePushForUndo(self)
        elif "LST" == object.whatami: # Handle a list.
            if object.dead: # Lists are normally inert, so...
                self.The.StackPush(object) #...just simply push it.
            elif not self.The.StackIsEmpty() and "|" == self.The.StackCopyItemLast().val:
                self.The.StackPop() # Clear protection blocker.
                self.The.StackPush(object) # Push protected live list.
            else: # It's live! Evaluate contents now.
                self.loadlocals(object.names)
                for n in object.val: # Iterate through contents.
                    self.evaluate(n) # Recursive call.
                self.localsyms.pop() # Drop this level's local var dict.
        else: # Must be a SYM
            referent= self.resolve_symbol(object)
            if referent is not None: # If some referent object was found, pretend...
                #print("Creating deep list copy in evaluate")
                if hasattr(referent,'whatami') and referent.whatami == 'LST':
                    referent= referent.deep_copy()
                try:
                    referent(self) #...it was submitted itself - call it.
                except SystemExit: # Don't make a fuss for clean exits.
                    raise # Reraise explicit exits from exit commands.
                except:
                    raise # Reraise to help in DEBUG work.
                    print( 'Oh no. That sucks. Something very ' +
                           'unpleasant happened. Sorry about that.' )
        # Status report please.
        if self.diagnostic:
            self.The.StackDisplay()
