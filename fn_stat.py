#!/usr/bin/python3
# fn_stat.py - 2014-05-01
# This library contains functions for implementing statistics
# calculations. Many of these were inspired by the excellent
# statistics functions of the HP48.
# In Python 3.4 there is a module `statistics` which might be of interest.

import inc
import objectifier
build_GG_command= objectifier.build_GG_command

# =============== Built In Functions ===========================
internal_syms= dict() # Establish the list of built-in functions.

internal_syms['mean']= build_GG_command('avg')

def intf_RAND(E):
    """Returns a random value between 0 and 1."""
    import random
    x= random.random()
    answer= objectifier.StackOB_VAL( x )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop') ] )
internal_syms['rand']= intf_RAND # Register function.

def intf_RDZ(E):
    """Takes v1 off the stack and uses it to set the random seed. If
    the stack is empty or v1 is zero, use current time."""
    import random
    if E.The.StackSize() < 1:
        random.seed()
    else:
        v1= E.The.StackPop() # Numeric input object.
        x= v1.val # Value of it.
        if v1.whatami == "VAL" and v1.val == 0:
            random.seed()
        else:
            random.seed(repr(x))
        E.Undo.StackPush( [ v1 ] )
internal_syms['rdz']= intf_RDZ # Register function.
internal_syms['srand']= intf_RDZ # Register function.

def intf_SHUFFLE(E):
    """Takes a list item from v1 and returns a list of the same objects
    in a completely random order. This will shuffle the entire stack.
        depth 2list shuffle wake !
    """
    if not inc.LST(E,1):
        print("Input Error: shuffle")
        print(intf_SHUFFLE.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # List to be shuffled.
    import random
    random.shuffle(v1)
    E.The.StackPush( objectifier.StackOB_LST( v1 ) )
internal_syms['shuffle']= intf_SHUFFLE # Register function.

def fact(n):
    if n > 170: return 0 # My current python dies beyond this.
    f= 1
    for i in range(1,n+1): f*=i
    return f

def mean(l):
    """Takes list of numerical values only. Returns arithmetic mean."""
    if not l: return None # Shouldn't send this empty lists.
    return float(sum(l))/len(l)

def variance(l,pop=False):
    """Calculates the variance of the values in the non-empty list.
    Sample variance if pop=False, population variance if pop=True"""
    # Maybe it shouldn't send 0 on error conditions.
    if not l: return 0 # Shouldn't send this empty lists.
    n= len(l)
    xm= mean(l)
    if pop:
        if (n == 0): return 0
        pre= 1/float(n)
    else:
        if (n-1 == 0): return 0
        pre= 1/float(n-1)
    return pre * sum( [ (x-xm)**2 for x in l ] )

def covariance(l1,l2,pop=False):
    """Calculates the covariance of the values in the two supplied
    non-empty equal-length lists.
    Sample covariance if pop=False, population covariance if pop=True"""
    # Maybe it shouldn't send 0 on error conditions.
    if not l1 or not l2: return 0 # Shouldn't send this empty lists.
    n= len(l1) # Assume lists are same length by now.
    if (n-1 == 0): return 0
    l1m= mean(l1)
    l2m= mean(l2)
    if pop:
        if (n == 0): return 0
        pre= 1/float(n)
    else:
        if (n-1 == 0): return 0
        pre= 1/float(n-1)
    return pre * sum( [ (l1[i] - l1m)*(l2[i] - l1m) for i in range(n) ] )

def intf_FACT(E):
    """Factorial (not a complete Gamma function) of the value of level one.
    Any value greater than 170 will return 0 because any argument larger
    than this will create an answer too big to safely handle.
      6 fact -> 720.0
    """
    X= E.The.StackPop() # Numeric input object.
    x= int(X.val) # Value of it.
    answer= objectifier.StackOB_VAL( fact(x) )
    E.The.StackPush(answer)
    E.Undo.StackPush( [ objectifier.StackOB_SYM('drop'), X ] )
internal_syms['fact']= intf_FACT # Register function.

def intf_COMB(E):
    """Number of possible combinations of v2 items taken v1 at a time.
       fact(v2) / (fact(v1) * fact(v2-v1))
    """
    if not inc.VAL(E,1) or not inc.VAL(E,2):
        print("Input Error: comb")
        print(intf_COMB.__doc__)
        return # Without doing much of anything.
    v1= int(E.The.StackPop().val) # Taken this many at a time.
    v2= int(E.The.StackPop().val) # Combination of this many items.
    d= v2-v1
    out= fact(v2) / (fact(v1) * fact(d))
    out= objectifier.StackOB_VAL( out )
    E.The.StackPush(out)
internal_syms['comb']= intf_COMB # HP48.

def intf_PERM(E):
    """Number of possible permutations of v2 items taken v1 at a time.
       fact(v2) / fact(v2-v1)
    """
    if not inc.VAL(E,1) or not inc.VAL(E,2):
        print("Input Error: perm")
        print(intf_PERM.__doc__)
        return # Without doing much of anything.
    v1= int(E.The.StackPop().val) # Taken this many at a time.
    v2= int(E.The.StackPop().val) # Combination of this many items.
    d= v2-v1
    out= fact(v2) / fact(d)
    out= objectifier.StackOB_VAL( out )
    E.The.StackPush(out)
internal_syms['perm']= intf_PERM # HP48.

def intf_MIN(E):
    """Return the minimum value from a list at v1.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] min -> 66
    [76 89 83 79 91 95 82 69 66 75 80 88] min -> 2.0
    """
    if not inc.LST(E,1):
        print("Input Error: min")
        print(intf_MIN.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: return # Input is empty list.
    m= v1[0]
    if m.whatami == "SYM":
        if m.val in E.symtab:
            mv= E.symtab[m.val].val
    else:
        mv= m.val
    for ob in v1[1:]:
        if ob.whatami == "SYM":
            if ob.val in E.symtab:
                q= E.symtab[ob.val].val
        else:
            q= ob.val
        if q < mv:
            m= ob
            mv= q
    E.The.StackPush(m)
internal_syms['min']= intf_MIN # HP48.

def intf_MAX(E):
    """Return the maximum value from a list at v1.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] max -> 3.6
    [76 89 83 79 91 95 82 69 66 75 80 88] max -> 95
    """
    if not inc.LST(E,1):
        print("Input Error: max")
        print(intf_MAX.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: return # Input is empty list.
    m= v1[0]
    if m.whatami == "SYM":
        if m.val in E.symtab:
            mv= E.symtab[m.val].val
    else:
        mv= m.val
    for ob in v1[1:]:
        if ob.whatami == "SYM":
            if ob.val in E.symtab:
                q= E.symtab[ob.val].val
        else:
            q= ob.val
        if q > mv:
            m= ob
            mv= q
    E.The.StackPush(m)
internal_syms['max']= intf_MAX # HP48.

def intf_SUM(E):
    """Calculate the sum of a list of values. There is an alias `tot`.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] sum -> 32.6
    [76 89 83 79 91 95 82 69 66 75 80 88] tot -> 973
    """
    if not inc.LST(E,1):
        print("Input Error: sum")
        print(intf_SUM.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: # Input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    numlist= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist.append(v)
    out= objectifier.StackOB_VAL( sum(numlist) )
    E.The.StackPush( out )
internal_syms['sum']= intf_SUM # Register function.
internal_syms['tot']= intf_SUM # HP48

def intf_AVG(E):
    """Calculate the average or arithmetic mean of a list of values. There
    is an alias `mean`.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] avg -> 2.71666666667
    [76 89 83 79 91 95 82 69 66 75 80 88] mean -> 81.0833333333
    """
    if not inc.LST(E,1):
        print("Input Error: avg")
        print(intf_AVG.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: # Input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    numlist= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist.append(v)
    out= objectifier.StackOB_VAL( mean(numlist) )
    E.The.StackPush( out )
internal_syms['avg']= intf_AVG # Register function.
internal_syms['mean']= intf_AVG # HP48

def intf_VAR(E):
    """Calculate the sample variance of a list of values. Use this when
    some of the members of the entire population are not represented.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] var -> 0.285151515152
    [76 89 83 79 91 95 82 69 66 75 80 88] var -> 77.1742424242
    """
    if not inc.LST(E,1):
        print("Input Error: var")
        print(intf_VAR.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: # Input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    numlist= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist.append(v)
    out= objectifier.StackOB_VAL( variance(numlist) )
    E.The.StackPush( out )
internal_syms['var']= intf_VAR # Register function.

def intf_PVAR(E):
    """Calculate the population variance of a list of values. Use this when
    all of the members of the entire population are represented.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] var -> 0.261388888889
    [76 89 83 79 91 95 82 69 66 75 80 88] var -> 70.7430555556
    """
    if not inc.LST(E,1):
        print("Input Error: pvar")
        print(intf_PVAR.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: # Input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    numlist= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist.append(v)
    out= objectifier.StackOB_VAL( variance(numlist,True) )
    E.The.StackPush( out )
internal_syms['pvar']= intf_PVAR # Register function.

def intf_SDEV(E):
    """Calculate the sample standard deviation of a list of values. Use this
    when some of the members of the entire population are not represented.
    This is the square root of the sample variance.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] sdev -> 0.533995800687
    [76 89 83 79 91 95 82 69 66 75 80 88] sdev -> 8.78488716059
    """
    if not inc.LST(E,1):
        print("Input Error: sdev")
        print(intf_SDEV.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: # Input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    import math
    numlist= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist.append(v)
    out= objectifier.StackOB_VAL( math.sqrt(variance(numlist)) )
    E.The.StackPush( out )
internal_syms['sdev']= intf_SDEV # Register function.

def intf_PSDEV(E):
    """Calculate the population standard deviation of a list of values. Use
    this when all of the members of the entire population are represented.
    This is the square root of the population variance
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] var -> 0.511262055006
    [76 89 83 79 91 95 82 69 66 75 80 88] var -> 8.41088910613
    """
    if not inc.LST(E,1):
        print("Input Error: psdev")
        print(intf_PSDEV.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: # Input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    import math
    numlist= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist.append(v)
    out= objectifier.StackOB_VAL( math.sqrt(variance(numlist,True)) )
    E.The.StackPush( out )
internal_syms['psdev']= intf_PSDEV # Register function.

def intf_COV(E):
    """Calculate the sample covariance of two lists of values taken from
    v1 and v2. The two lists should be the same length. Use this when some of
    the members of the entire population are not represented.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] 
    [76  89  83  79  91  95  82  69  66  75  80  88 ] cov -> 3.85303030303
    """
    if not inc.LST(E,1) and not inc.LST(E,2):
        print("Input Error: cov")
        print(intf_COV.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    v2= E.The.StackPop().val # A Python list of gg OBs.
    if not v1 or not v2 or len(v1) != len(v2): # An input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    numlist1= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist1.append(v)
    numlist2= list() # List of just numeric values.
    for v in v2:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist2.append(v)
    out= objectifier.StackOB_VAL( covariance(numlist1,numlist2) )
    E.The.StackPush( out )
internal_syms['cov']= intf_COV # Register function.

def intf_PCOV(E):
    """Calculate the population covariance of two lists of values taken from
    v1 and v2. The two lists should be the same length. Use this when all of
    the members of the entire population are represented.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] 
    [76  89  83  79  91  95  82  69  66  75  80  88 ] pcov -> 3.53194444444
    """
    if not inc.LST(E,1) and not inc.LST(E,2):
        print("Input Error: pcov")
        print(intf_PCOV.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    v2= E.The.StackPop().val # A Python list of gg OBs.
    if not v1 or not v2 or len(v1) != len(v2): # An input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    numlist1= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist1.append(v)
    numlist2= list() # List of just numeric values.
    for v in v2:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist2.append(v)
    out= objectifier.StackOB_VAL( covariance(numlist1,numlist2,True) )
    E.The.StackPush( out )
internal_syms['pcov']= intf_PCOV # Register function.

def intf_CORR(E):
    """Calculate the sample Pearson's correleation coefficient (r)
    between two lists of values taken from v1 and v2. The two lists should be
    the same length. Use this when some of the members of the entire population
    are not represented.
    [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] 
    [76  89  83  79  91  95  82  69  66  75  80  88 ] corr -> 0.821350253246
    """
    if not inc.LST(E,1) and not inc.LST(E,2):
        print("Input Error: corr")
        print(intf_CORR.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    v2= E.The.StackPop().val # A Python list of gg OBs.
    if not v1 or not v2 or len(v1) != len(v2): # An input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    numlist1= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist1.append(v)
    numlist2= list() # List of just numeric values.
    for v in v2:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist2.append(v)
    import math
    sd1= math.sqrt(variance(numlist1))
    sd2= math.sqrt(variance(numlist2))
    if not sd1 or not sd2: # That would be bad.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
    out= objectifier.StackOB_VAL( covariance(numlist1,numlist2) / (sd1*sd2) )
    E.The.StackPush( out )
internal_syms['corr']= intf_CORR # Register function.

def intf_PCORR(E):
    """Calculate the population Pearson's correleation coefficient (rho)
    between two lists of values taken from v1 and v2. The two lists should be
    the same length. Use this when all of the members of the entire population
    are represented. This function is probably not needed since it does not
    seem to matter if population or sample statistics are used to calculate
    the Pearson's correleation coefficient. See `corr`.
    """
    if not inc.LST(E,1) and not inc.LST(E,2):
        print("Input Error: pcorr")
        print(intf_PCORR.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    v2= E.The.StackPop().val # A Python list of gg OBs.
    if not v1 or not v2 or len(v1) != len(v2): # An input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    numlist1= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist1.append(v)
    numlist2= list() # List of just numeric values.
    for v in v2:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist2.append(v)
    import math
    sd1= math.sqrt(variance(numlist1,True))
    sd2= math.sqrt(variance(numlist2,True))
    if not sd1 or not sd2: # That would be bad.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
    out= objectifier.StackOB_VAL( covariance(numlist1,numlist2,True) / (sd1*sd2) )
    E.The.StackPush( out )
internal_syms['pcorr']= intf_PCORR # Register function.

def intf_DISTGAUSS(E):
    """Takes VALs from v1 and v2 and returns a value randomly generated by a
    function that produces values which are distributed in a Gaussian
    distribution. The v2 VAL is the mean of the distribution. The v1 VAL is
    the distribution's standard deviation.
        |[.5 .2 distgauss::!] 100000 repeat 100000 2list dup mean swap sdev ->
        0.500337044014 0.200301690936
    """
    if not inc.VAL(E,1) or not inc.VAL(E,2):
        print("Input Error: distgauss")
        print(intf_DISTGAUSS.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # Standard deviation.
    v2= E.The.StackPop().val # Mean.
    import random
    out= random.gauss(v2,v1)
    out= objectifier.StackOB_VAL( out )
    E.The.StackPush(out)
internal_syms['distgauss']= intf_DISTGAUSS # Python `random` special.
internal_syms['ndist']= intf_DISTGAUSS # HP48

def intf_DISTEXP(E):
    """Takes VAL from v1 and returns a value randomly generated by a
    function that produces values which are distributed in an exponential 
    distribution. The v1 VAL is Lambda which is a parameter of this kind
    of distribution. The formula is `f(x,Lambda)= Lambda * exp(-Lambda * x)`.
    The mean is 1/Lambda and the variance is 1/(Lambda*Lambda).
        |[.75 distexp::!] 100000 repeat 100000 2list 
        dup mean inv swap var inv sqrt -> 0.743701781531 0.742319134654
    """
    if not inc.VAL(E,1):
        print("Input Error: distexp")
        print(intf_DISTEXP.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # Lambda of the distribution, not Python's lambda.
    import random
    out= random.expovariate(v1)
    out= objectifier.StackOB_VAL( out )
    E.The.StackPush(out)
internal_syms['distexp']= intf_DISTEXP # Python `random` special.

def intf_DISTWEIBULL(E):
    """Takes VALs from v1 and v2, and returns a value randomly generated
    by a function that produces values which are distributed in a Weibull
    distribution. This is often used to model processes related to failure
    rates, survival analysis, and reliability. The v2 VAL is Lambda which is
    the scale parameter for this kind of distribution. The v1 VAL is k which is
    the shape parameter. Both must be greater than zero. If k is 1 this is
    equivalent to the exponential distribution. If k is 2 it is equivalent to
    the Rayleigh distribution. A value of k < 1 indicates that the failure rate
    decreases over time. This happens if there is significant "infant
    mortality", or defective items failing early and the failure rate
    decreasing over time as the defective items are weeded out of the
    population. A value of k = 1 indicates that the failure rate is constant
    over time. This might suggest random external events are causing mortality,
    or failure. A value of k > 1 indicates that the failure rate increases with
    time. This happens if there is an "aging" process, or parts that are more
    likely to fail as time goes on.
        |[.75 1 distweibull::!] 100000 repeat 100000 2list mean -> 0.751247734665
    """
    if not inc.VAL(E,1) or not inc.VAL(E,2):
        print("Input Error: distweibull")
        print(intf_DISTWEIBULL.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # k, beta, shape
    v2= E.The.StackPop().val # Lambda, alpha, scale
    import random
    out= random.weibullvariate(v2,v1)
    out= objectifier.StackOB_VAL( out )
    E.The.StackPush(out)
internal_syms['distweibull']= intf_DISTWEIBULL # Python `random` special.

# NOTE: There are other random distributions that can be easily added if needed.
# beta, gamma, lognormal, pareto.

def intf_WEIGHTEDMEAN(E):
    """The `weightedmean` function takes a list of numbers to be averaged
    from v2 and a list of weights to bias the result by. The lists must be
    or resolve to VALs and they must be the same length. This is commonly 
    used to calculate weighted grades. If a student gets grades of C, A, A,
    D, B (corresponding to [2 4 4 1 3]) in classes of 4, 3, 3, 4, 3 credits
    respectively, the weighted average of these two lists will give a GPA
    adjusted for the "importantance" based on credits. This could also be
    used to make recommendations based on how well rated an item is by a
    list of people (list v2) and how closely each of those people match the
    user's previous tastes (list v1, the weights).
        [2 4 4 1 3] [4 3 3 4 3] weightedmean -> 2.64705882353
        [2 4 4 1 3] mean -> 2.8
        [76  89  83  79  91  95  82  69  66  75  80  88 ] 
        [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] weightedmean -> 82.3834355828
        [76  89  83  79  91  95  82  69  66  75  80  88 ] mean -> 81.0833333333
    """
    if not inc.LST(E,1) and not inc.LST(E,2):
        print("Input Error: weightedmean")
        print(intf_WEIGHTEDMEAN.__doc__)
        return # Without doing much of anything.
    v2= E.The.StackPop().val # A Python list of gg OBs.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    n= len(v1)
    out= objectifier.StackOB_VAL(0)
    if not v1 or not v2 or n != len(v2): # An input is empty list.
        E.The.StackPush( out )
        return
    numlist1= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist1.append(v)
    numlist2= list() # List of just numeric values.
    for v in v2:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        numlist2.append(v)
    num= sum([numlist1[i]*numlist2[i] for i in range(n)])
    den= sum([numlist2[i] for i in range(n)]) 
    if den:
        out= objectifier.StackOB_VAL( num/den )
    E.The.StackPush( out ) 
internal_syms['weightedmean']= intf_WEIGHTEDMEAN # Register function.

def intf_TANIMOTO(E):
    """The `tanimoto` function takes a list of properties of
  item A from v2 and a list of properties of item B from v1 and
  calculates the Tanimoto similarity coefficient. The idea is to
  compute a measure of how similar these things A and B are based on
  their characteristics. For example, if you're an alien naturalist
  and you find a mystery animal with "horns", "tail", "beard", "red", 
  and "hoof", and you want to see if its more like a zebra ("tail",
  "stripes", "hoof", "mane") or a goat ("horns", "tail", "hoof",
  "beard") this might be helpful. In recommendation engines, this can
  be used to find people with similar properties. There is much
  confusion aboout the origin and use of this. It seems to be a
  generalization of the Jaccard Index applicable to sets, which is
  what this function assumes. The formula used here is `T=
  Ni/(Na+Nb-Ni)` where Ni is the number of items in both lists or the
  count of the intersection, Na is the number of items in list A, and
  Nb is the number of items in list B. Dissimilarity, a distance
  metric, can be acheived with `1 rot rot tanimoto -`. The properties
  can be specified as TXT or VAL or SYM. If they are SYM, they are
  resolved.
        [''horns'' ''tail'' ''beard'' ''red'' ''hoof''] |devil sto
        devil [''tail'' ''stripes'' ''hoof'' ''mane''] tanimoto -> 0.285714285714
        devil [''horns'' ''beard'' ''tail'' ''hoof''] tanimoto -> .8
    """
    if not inc.LST(E,1) and not inc.LST(E,2):
        print("Input Error: tanimoto")
        print(intf_TANIMOTO.__doc__)
        return # Without doing much of anything.
    v2= E.The.StackPop().val # A Python list of gg OBs.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    out= objectifier.StackOB_VAL(0)
    if not v1 or not v2: # An input is empty list.
        E.The.StackPush( out )
        return
    sl1= list() # List of numric or text values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        sl1.append(v)
    sl2= list() # List of just numeric values.
    for v in v2:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        sl2.append(v)

    C= len( set(sl1) & set(sl2) )
    num= float(C)
    den= len(sl1)+len(sl2)-C
    
    if den:
        out= objectifier.StackOB_VAL( num/den )
    E.The.StackPush( out )
internal_syms['tanimoto']= intf_TANIMOTO # Register function.

def intf_ENTROPY(E):
    """Calculate the Shannon entropy for a list of items. This is a measure
    of how surprising a random selection of the data is. It can be used to
    measure the amount of disorder in a set. Lowering entropy during an
    iterative classification process could be a sign that the data is becoming
    better organized. Symbols do get resolved although other data stays as is.
    The formula is `H(X)=-sum[i=1,n](p(x)*log2(p(x)))` where p(x) is the
    probability that X is in state x. The n is the number of unique items in
    the original list. The log2 aspect causes this function to return output
    measured in bits of entropy. This entropy calculation is likely not correct
    for cryptographic keys and passphrases since the probabilities of a certain
    value are generally lower than this process assumes (by counting extant
    examples).
        [2.2 2.4 3.1 2.5 3.5 3.6 2.5 2.0 2.2 2.6 2.7 3.3] entropy -> 3.25162916739
        [76 89 83 79 91 95 82 69 66 75 80 88] entropy -> 3.58496250072
        [''p'' ''a'' ''s'' ''s'' ''w'' ''o'' ''r'' ''d''] entropy -> 2.75
        [''3'' ''T'' ''^'' '','' ''d'' ''9'' ''9'' ''w''] entropy -> 2.75
        100000 range entropy -> 16.6096404744
    """
    if not inc.LST(E,1):
        print("Input Error: entropy")
        print(intf_ENTROPY.__doc__)
        return # Without doing much of anything.
    v1= E.The.StackPop().val # A Python list of gg OBs.
    if not v1: # Input is empty list.
        E.The.StackPush( objectifier.StackOB_VAL(0) )
        return
    import math
    l= list() # List of just numeric values.
    for v in v1:
        if v.whatami == "SYM":
            if v.val in E.symtab:
                v= E.symtab[v.val].val
        else:
            v= v.val
        l.append(v)
    log2= lambda x:math.log(x)/math.log(2)
    total= len(l)
    counts= dict()
    for item in l:
        counts.setdefault(item,0)
        counts[item]+= 1
    ent= 0
    for i in counts:
        p= float(counts[i])/total
        ent-= p*log2(p)
    out= objectifier.StackOB_VAL( ent )
    E.The.StackPush( out ) 
internal_syms['entropy']= intf_ENTROPY # Register function.



