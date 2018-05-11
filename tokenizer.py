#!/usr/bin/python3
# tokenizer.py $Revision: 1.10 $ $Date: 2005/10/30 00:14:10 $
# This module provides a class that takes lines of possibly messy
# input and converts them into sensible tokens. This includes nested
# lists over multiple lines and multi-line text with complex escaping
# behavior. Instances of this class keep track of which tokens are
# available for processing.

class Tokenizer:
    def __init__(self):
        self.list_depth= 0          # Current level of list recursion.
        self.current_token= list()  # Temp var for building tokens.
        self.partial_pending= str() # Unfinished data from now and before.
        self.token_queue= list()    # Tokens pulled out of this line.
        self.specials= '|![]'       # All characters that get autospaced.
        self.diagnostic= False      # Set to True to get verbose diagnostic mode.
        self.object_limbo= True # Currently between objects flag? Default Yes.
        self.text_mode= False  # Currently working on a text object?
        self.possibly_text_mode= False  # First ' of '' has been typed?
        self.LS_delim_L= '[' # Character to start a list.
        self.LS_delim_R= ']' # Character to end a list.
        self.TX_delim= "'"   # Character to delimit text. Redef'd in obj.fier.
        self.TX_magic= '^'   # Character to help with problematic text input.
        self.OB_delim= ' '   # Character which separates objects.
        #Private:
        self.TX_d= 0         # Delimiter count for text parsing.
        self.TX_m= 0         # Magic count for text parsing.

    def diagnostic_on(self):
        "Turn on diagnostics for input."
        self.diagnostic= True

    def text_parse(self, c): 
        """This function is called if the character arrives while in
        textmode. Take characters one by one and build a text string
        while in text input mode. The clever part is knowing when the
        string is complete. Text mode ends with double quotes. However
        to include double quotes in the string, use "^". To include
        that, use "^^", etc."""
        #TODO: BUG- triple quotes at the end of a line don't work!
        s= self   # s is self (simplify the code).
        # Simplify these variables.
        # d is delimeter tally - m is magic tally 
        # M is magic char alias (^) - D is delimiter char alias (')
        # S is interobject delimiter (space)
        d= s.TX_d; m= s.TX_m; D= s.TX_delim; M= s.TX_magic; S= s.OB_delim
        def a(appendee): # Simple function to add a char to the current token.
            self.current_token.append(appendee)
            self.partial_pending += appendee
        # The is the logic to parse text. Converted from the Perl prototype.
        if (d == 0 and m == 0 and c == D): s.TX_d= 1; s.TX_m= 0; a('');  return
        if (d == 0 and m == 0 and c == M): s.TX_d= 0; s.TX_m= 0; a(M);   return
        if (d == 0 and m == 0           ): s.TX_d= 0; s.TX_m= 0; a(c);   return
        if (d == 0 and m == 1 and c == D): s.TX_d= 1; s.TX_m= 1; a('');  return
        if (d == 0 and m == 1 and c == M): s.TX_d= 0; s.TX_m= 1; a(M);   return
        if (d == 0 and m == 1           ): s.TX_d= 0; s.TX_m= 0; a(M+c); return
        if (d == 1 and m == 0 and c == D): s.TX_d= 2; s.TX_m= 0; a('');  return
        if (d == 1 and m == 0 and c == M): s.TX_d= 0; s.TX_m= 1; a(D);   return
        if (d == 1 and m == 0           ): s.TX_d= 0; s.TX_m= 0; a(D+c); return
        if (d == 1 and m == 1 and c == D): s.TX_d= 2; s.TX_m= 1; a('');  return
        if (d == 1 and m == 1 and c == M): s.TX_d= 0; s.TX_m= 1; a(D);   return
        if (d == 1 and m == 1           ): s.TX_d= 0; s.TX_m= 0; a(D+c); return
        if (d == 2 and m == 0 and c == D): s.TX_d= 2; s.TX_m= 0; a(D);   return
        if (d == 2 and m == 0 and c == M): s.TX_d= 0; s.TX_m= 1; a(D+D); return
        if (d == 2 and m == 0           ):
            if c == S: pass
            else:                        s.TX_d= 0; s.TX_m= 0; a(D+D+c); return
        if (d == 2 and m == 1 and c == D): s.TX_d= 2; s.TX_m= 0; a(D);   return
        if (d == 2 and m == 1 and c == M): s.TX_d= 0; s.TX_m= 1; a();    return
        if (d == 2 and m == 1           ):
            if c == S: pass
            else:                        s.TX_d= 0; s.TX_m= 0; a(D+D+c); return
        # Anything that made it through to here should conclude the object.
        self.token_queue.append(''.join(self.current_token)) # Add this text object.
        # Unpad anything that was convenience padded at the start of tokenizing.
        for spec in self.specials: # Special chars which don't need separation.
            self.token_queue[-1]= self.token_queue[-1].replace(' '+spec+' ', spec)
        # Reset things.
        self.TX_d= 0
        self.TX_m= 0
        self.text_mode= False
        self.partial_pending= str()
        if self.diagnostic:
            print( "In `text_parse()` current_token={%s" % '}{'.join(self.current_token) + '}')
            print( "In `text_parse()` token_queue={%s" % '}{'.join(self.token_queue) + '}')
        self.current_token= list()

    def tokenize_input(self, input):
        """Turn an input string into sensible input objects."""
        # Convenience padding of special chars with spaces so the user
        # can be lazy about separating things that are clearly separate.
        # Note that this has to be undone if it turns out to be TXT.
        if self.diagnostic:
            print( 'Pending:'+str(self.partial_pending))
        for spec in self.specials: # Special chars which don't need separation.
            input= input.replace(spec, ' '+spec+' ')
        # Looks like this function can be reduced quite a bit. 
        if input[-1] != self.OB_delim: # Convert returns to separators.
            input += self.OB_delim # If just return pressed, add space.
        # Single token being formed now. Grab last input's extra...
        self.current_token= [self.partial_pending] # ...if any.
        if self.diagnostic:
            print("Analyzing:"+input)  # DIAGNOSTIC
        # Can't go negative on list depth. Predict that here.
        depth_problem= ( input.count(self.LS_delim_L)
                       - input.count(self.LS_delim_R) 
                       + self.list_depth )
        if depth_problem < 0: # Check before messing up data.
            raise IOError("Error: A list was closed that wasn't open.")
        # -- Step through each character in the input string. --
        for character in input: # Now step through each character.
            # Currently in text mode?
            if self.text_mode: # If so, let that routine deal with it.
                self.text_parse(character)
                continue # No more thinking about this character.
            # Starting a text literal.
            if self.TX_delim == character and 0 == self.list_depth:
                if self.possibly_text_mode: # Was the first ' entered?
                    self.text_mode= True
                    self.possibly_text_mode= False # It's now definite!
                    self.partial_pending= str() # Reset.
                else: # This must be the first text delim.
                    self.possibly_text_mode= True
                    continue
            # Text char followed by unexpected thing not destined for text.
            if self.possibly_text_mode and not self.TX_delim == character:
                self.possibly_text_mode= False # Must have been a false alarm.
                self.token_queue.append(self.TX_delim) # Maybe it's part of a sym.
            # Starting a list.
            if self.LS_delim_L == character: # Descending deeper into sub list.
                self.list_depth += 1 # Always keep count.
                if not self.object_limbo and 0 == self.list_depth: # For text[then list].
                    self.token_queue.append(''.join(self.current_token))
                    self.partial_pending= str() # Reset. Is this needed?
                    self.current_token= [ self.LS_delim_L ]
                    self.object_limbo= True
                    continue
            # Ending a list.
            if self.LS_delim_R == character:
                self.list_depth -= 1
                if 0 == self.list_depth:
                    self.current_token.append(character)
                    self.token_queue.append(''.join(self.current_token))
                    # Unpad anything that was convenience padded at the start of tokenizing.
                    for spec in self.specials: # Special chars which don't need separation.
                        self.token_queue[-1]= self.token_queue[-1].replace(' '+spec+' ', spec)
                    self.partial_pending= str() # Reset.
                    self.current_token= list() # Reset.
                    self.object_limbo= True
                    continue
            # Completing a token.
            if self.OB_delim == character and 0 == self.list_depth:
                if not self.object_limbo:
                    self.token_queue.append(''.join(self.current_token))
                    self.partial_pending= str() # Reset.
                    self.current_token= list()
                self.object_limbo= True 
                continue
            self.object_limbo= False
            self.current_token.append(character) # Build token with this char.
        # -- After loop of input characters. --
        # -- Final clean up of stranded token being built. --
        if '' in self.token_queue: # This happens with `[''a''  ]`
            #self.token_queue= filter(lambda x:not x is '',self.token_queue) 
            self.token_queue= [x for x in self.token_queue if x is not '']
        if self.current_token:
            if self.diagnostic:
                print('current_token:'+'-'.join(self.current_token))
            if self.text_mode: # If enter pressed during text mode...
                self.current_token.append('\n') #...add the literal LF.
                self.partial_pending= ''.join(self.current_token)
            else:
                if 0 == self.list_depth: # Then make line's final token.
                    self.token_queue.append(''.join(self.current_token))
                    self.partial_pending= str() # Reset.
                else: # Else this token isn't finished, save for later.
                    self.partial_pending= ''.join(self.current_token)
        if self.diagnostic:
            if self.token_queue:
                print('token_queue separated by dash>'+('-'.join(self.token_queue))+'<')  # DIAGNOSTIC
            else:
                print('** Expecting more input. **')

    def get_token_queue(self):
        if self.diagnostic:
            for token in self.token_queue:
                print('TOKEN>>' + token + '<<') # DIAGNOSTIC
        flushed_from_queue= self.token_queue
        self.token_queue= list()
        return flushed_from_queue
