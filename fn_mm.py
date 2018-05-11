#!/usr/bin/python3
# fn_mmodel.py $Revision: 1.1 $ $Date: 2008/04/03 17:12:58 $
# This library contains functions which interact with and use the
# memory model.
import objectifier
import inc
import mm
import mmout

build_GG_command= objectifier.build_GG_command
MMEL= mm.EntityList()
#OUT= mmout.MMOut()
#OUT= mmout.MMOutSVG()
OUT= mmout.MMOutNONE()

SAVEFILE= '/tmp/savefile.gg'

# =============== Built In Functions ===========================
internal_syms= dict() # Establish the list of built-in functions.

#What is this? Just left here for a reference?
internal_syms['mm']= build_GG_command('memorymodel')

def intf_MMSVGOUT(E):
    """Send memory model to to2d and then show it in interpreter as it would be published."""
    OUT.default(MMEL,E)
internal_syms['svgout']= intf_MMSVGOUT # Register function.
internal_syms['redraw']= intf_MMSVGOUT # Register function.
internal_syms['refresh']= intf_MMSVGOUT # Register function.

def intf_MMDUMP(E):
    """Dump the memory model to interpreter."""
    print(mmout.mmdump(MMEL))
internal_syms['mmdump']= intf_MMDUMP # Register function.

def intf_MMLIST(E):
    """Dump the memory model to interpreter in a way that's helpful to the user."""
    print(MMEL.__repr__())
    #print(OUT.default(MMEL,E))
internal_syms['mmlist']= intf_MMLIST # Register function.
internal_syms['mm']= intf_MMLIST # Register function.

def intf_MMITEM(E):
    """Dump the memory model of only the supplied entity ID or list of entity
    IDs to interpreter in a way that's helpful to the user.
        <entID> mmitem ->  
        [<entID> <entID> <entID>] mmitem -> 
    """
    if not inc.entid_or_LST_of_entids(E.The,1):
        print("Input Error: mmitem\n" + intf_MMITEM.__doc__)
        return # Without doing much of anything.
    if not inc.entid_or_LST_of_entids(E.The,1):
        print("Input Error: mmitem")
        print(intf_MMITEM.__doc__)
        return # Without doing much of anything.
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of ints.
        myeids= [x.val for x in myeids] # Should now be a list of ints.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    for myeid in myeids:
        if myeid in MMEL.El:
            print(MMEL.El[myeid].mmlist_repr())
internal_syms['mmitem']= intf_MMITEM # Register function.
internal_syms['mmi']= intf_MMITEM # Register function.

def intf_MMSAVE(E):
    """Dump the memory model in such a way that it can be saved in a file.
    This will create GeoGad commands which can approximately rebuild the
    current memory model (for example, using the `source` function).
    The default file name is `/tmp/savefile.gg` but can be changed using
    the `mmsaveas` command which takes a single TXT argument from the stack
    which is used as the file name to write to."""
    global SAVEFILE
    with open(SAVEFILE,'w') as f:
        f.write( MMEL.simplistic_mm_save_format() )
    print("Model script written to: %s\n" % SAVEFILE)

internal_syms['mmsave']= intf_MMSAVE # Register function.

def intf_MMSAVEAS(E):
    """Dump the memory model in such a way that it can be saved in a file.
    This will create GeoGad commands which can approximately rebuild the
    current memory model (for example, using the `source` function).
    The `mmsaveas` command takes a single TXT argument from the stack
    which is used as the file name to write to. Subsequent operations
    with the `mmsave` command will continue to use this file name once set."""
    global SAVEFILE
    check= ''
    if E.The.StackSize() >= 1: # Ensure something is here.
        checkob= E.The.StackCopyItemLast() # Input verification. Next item on stack now.
        check=checkob.whatami
    if not check == "TXT":
        print("Input Error: mmsaveas")
        print(intf_MMSAVEAS.__doc__)
        return # Without doing much of anything.
    SAVEFILE= E.The.StackPop().val
    print("Current file set to: %s\n" % SAVEFILE)
    intf_MMSAVE(E) # Actual saving done in one location.
internal_syms['mmsaveas']= intf_MMSAVEAS # Register function.

def intf_VIEWSHOW(E):
    """Displays the to2d, SVG output, and view settings."""
    out=  "View Properties\n"
    out+=  "---------------\n"
    out+= "svgoutfile=%s\n" % OUT.outfile
    out+= "camera=%s        {camset}\n" % (','.join([str(x) for x in OUT.camera]))
    out+= "target=%s        {tarset}\n" % (','.join([str(x) for x in OUT.target]))
    out+= "opacity=%s       {hlr,hide}\n" % str(OUT.opacity)
    out+= "facelines=%s     {facelines}\n" % str(OUT.facelines)
    out+= "vlinewidth=%0.2f {vlw,viewlinewidth}\n" % OUT.vlinewidth
    out+= "vrefreshms=%d    {refreshms,viewrefreshms}\n" % OUT.vrefreshms
    out+= "vbox=(%d,%d)     {viewbox[xy]}\n" % (OUT.vboxX,OUT.vboxY)
    out+= "vtran=(%d,%d)    {vtran[xy],viewtran[xy]}\n" % (OUT.vtranX,OUT.vtranY)
    out+= "vscale=(%d,%d)   {vscale[xy],viewscale[xy]}\n" % (OUT.vscaleX,OUT.vscaleY)
    print(out)
internal_syms['viewshow']= intf_VIEWSHOW # Register function.
internal_syms['vshow']= intf_VIEWSHOW # Register function.

#def intf_CAMSET(E):
#    """Takes a list of 3 VAL from the stack. Sets the camera placement with it."""
#    if not inc.point_formatted_LST(E.The,1):
#        print("Input Error: camset")
#        print(intf_CAMSET.__doc__)
#        return # Without doing much of anything.
#    OUT.camera= [ xyz.val for xyz in E.The.StackPop().val ]
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['camset']= intf_CAMSET # Register function.
#internal_syms['eyept']= intf_CAMSET # HP48 alias.
#
#def intf_TARSET(E):
#    """Takes a list of 3 VAL from the stack. Sets the camera placement with it."""
#    if not inc.point_formatted_LST(E.The,1):
#        print("Input Error: tarset")
#        print(intf_TARSET.__doc__)
#        return # Without doing much of anything.
#    OUT.target= [ xyz.val for xyz in E.The.StackPop().val ]
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['tarset']= intf_TARSET # Register function.
#
#def intf_VTRANX(E):
#    """Set the value for the SVG display initial translate transform on X axis."""
#    OUT.vtranX= E.The.StackPop().val
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['viewtranx']= intf_VTRANX # Register function.
#internal_syms['vtranx']= intf_VTRANX # Register function.
#
#def intf_VTRANY(E):
#    """Set the value for the SVG display initial translate transform on Y axis."""
#    OUT.vtranY= E.The.StackPop().val
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['viewtrany']= intf_VTRANY # Register function.
#internal_syms['vtrany']= intf_VTRANY # Register function.
#
#def intf_VSCALEX(E):
#    """Set the value for the SVG display initial scale transform on X axis."""
#    OUT.vscaleX= E.The.StackPop().val
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['viewscalex']= intf_VSCALEX # Register function.
#internal_syms['vscalex']= intf_VSCALEX # Register function.
#
#def intf_VSCALEY(E):
#    """Set the value for the SVG display initial scale transform on Y axis."""
#    OUT.vscaleY= E.The.StackPop().val
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['viewscaley']= intf_VSCALEY # Register function.
#internal_syms['vscaley']= intf_VSCALEY # Register function.
#
#def intf_VIEWBOXX(E):
#    """Set the width in pixels of the view box. Choose a value the browser can display."""
#    OUT.vboxX= E.The.StackPop().val
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['viewboxx']= intf_VIEWBOXX # Register function.
#
#def intf_VIEWBOXY(E):
#    """Set the width in pixels of the view box. Choose a value the browser can display."""
#    OUT.vboxY= E.The.StackPop().val
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['viewboxy']= intf_VIEWBOXY # Register function.
#
#def intf_VIEWREFRSHMS(E):
#    """View refresh interval set. Takes a VAL from the stack and sets output to render
#    continuously waiting VAL milliseconds between browser reloads. This basically
#    affects how responsive the browser is to noticing changes."""
#    OUT.vrefreshms= E.The.StackPop().val
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['viewrefreshms']= intf_VIEWREFRSHMS # Register function.
#internal_syms['refreshms']= intf_VIEWREFRSHMS # Register function.
#
#def intf_VIEWLINEWIDTHSET(E):
#    """View line width set. Takes a VAL from the stack and sets output to render
#    lines that width."""
#    OUT.vlinewidth= E.The.StackPop().val
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['vlw']= intf_VIEWLINEWIDTHSET # Register function.
#internal_syms['viewlinewidth']= intf_VIEWLINEWIDTHSET # Register function.
#
#def intf_OPACITYSET(E):
#    """Toggles the "opacity" setting for to2d to do hidden line removal. 
#    Takes nothing off the stack."""
#    OUT.opacity= not OUT.opacity
#    if not OUT.opacity:
#        print("Wire frame rendering.")
#    else:
#        print("Removing hidden lines.")
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['hide']= intf_OPACITYSET # Register function.
#internal_syms['hlr']= intf_OPACITYSET # Register function.
#
#def intf_FACESET(E):
#    """Toggles the "faces" setting for to2d to render lines at
#    the vertices of all tri faces. Takes nothing off the stack."""
#    OUT.facelines= not OUT.facelines
#    if not OUT.facelines:
#        print("Renderer will add visible lines to tri faces.")
#    else:
#        print("Renderer will leave tri faces invisible.")
#    OUT.default(MMEL,E) # AUTODUMP 
#internal_syms['facelines']= intf_FACESET # Register function.

def intf_POINTFORM(E):
    """Take 3 values off the stack and make a point formatted list."""
    # Preserve the VAL obj (don't take .val) which will compose the gg list.
    z= E.The.StackPop()
    y= E.The.StackPop()
    x= E.The.StackPop()
    p= objectifier.StackOB_LST([x, y, z])
    p.names= ['x','y','z']
    E.The.StackPush(p)
internal_syms['pointform']= intf_POINTFORM # Register function.
internal_syms['p']= intf_POINTFORM # Register function.

# == Function to check if an item is point formatted. Useful for line and tri.
def is_stack_ob_a_pt(Q):
    """Check that stack item supplied as Q is a LST of 3 VALs. e.g. [1 2 3]"""
    if Q.whatami == "LST":
        if len(Q.val) == 3:
            #if not filter(lambda x:x.whatami!="VAL",Q.val): # NOT PY3 kosher.
            if all([x.whatami=="VAL" for x in Q.val]):
                return True
    return False
    
def intf_LINE(E):
    """Take 2 values off the stack and make a new line entity. Both items must
    be LST comprised of exactly 3 VALs representing 2 x,y,z cartesian points.
    e.g.[0 0 0::x y z] [10 -5 3.2::x y z] line"""
    # == Check Input ==
    # Check that there are 2 point items on the stack
    inputok= False # Assume the worst.
    if E.The.StackSize() >= 2: # Ensure something is here.
        # === Check Item #1 ===
        check= E.The.StackCopyItemLast() # Input verification. Next item on stack now.
        if is_stack_ob_a_pt(check):
            # === Check Item #2 ===
            check= E.The.StackCopyItemN(2)
            if is_stack_ob_a_pt(check):
                inputok= True
    if not inputok:
        print("Input Error: line")
        print(intf_LINE.__doc__)
        return # Without doing much of anything.
    # The pop is a StackOB_LST containing xyz StackOB_VAL which must be expanded.
    p1= [ xyz.val for xyz in E.The.StackPop().val ]
    p2= [ xyz.val for xyz in E.The.StackPop().val ]
    c1= mm.Coords(p1)
    c2= mm.Coords(p2)
    line_ent= mm.Line_Entity( [c1,c2] )
    MMEL.add_ent(line_ent)
    lines_eid= objectifier.StackOB_VAL(line_ent.eid)
    E.The.StackPush(lines_eid)
    OUT.default(MMEL,E) # AUTODUMP 
internal_syms['line']= intf_LINE # Register function.
internal_syms['l']= intf_LINE # Register function.

def intf_TRI(E):
    """Take 3 values off the stack and make a tri face entity.
    The 3 values must be lists each containing 3 coordinate values.
    e.g. [-20 -20 0] [20 -20 0] [0 20 0] tri"""
    # == Check Input ==
    # Check that there are 3 point items on the stack
    inputok= False # Assume the worst.
    if E.The.StackSize() >= 3: # Ensure something is here.
        # === Check Item #1 ===
        check= E.The.StackCopyItemLast() # Input verification. Next item on stack now.
        if is_stack_ob_a_pt(check):
            # === Check Item #2 ===
            check= E.The.StackCopyItemN(2)
            if is_stack_ob_a_pt(check):
                # === Check Item #3 ===
                check= E.The.StackCopyItemN(3)
                if is_stack_ob_a_pt(check):
                    inputok= True
    if not inputok:
        print("Input Error: tri")
        print(intf_TRI.__doc__)
        return # Without doing much of anything.
    # == Construct Tri ==
    p1= [ xyz.val for xyz in E.The.StackPop().val ]
    p2= [ xyz.val for xyz in E.The.StackPop().val ]
    p3= [ xyz.val for xyz in E.The.StackPop().val ]
    c1= mm.Coords(p1)
    c2= mm.Coords(p2)
    c3= mm.Coords(p3)
    tri_ent= mm.Tri_Entity( [c1,c2,c3] )
    MMEL.add_ent(tri_ent)
    tris_eid= objectifier.StackOB_VAL(tri_ent.eid)
    E.The.StackPush(tris_eid)
    OUT.default(MMEL,E) # AUTODUMP 
internal_syms['tri']= intf_TRI # Register function.
internal_syms['t']= intf_TRI # Register function.

def intf_ENTTAG(E):
    """From level two either an entity ID value or a list of entity ID values
    is taken off the stack. From level one, a TXT object or a list of TXT
    objects is taken off the stack. The specified entities are tagged with the
    text items.
        <entID> ''roof'' tag ->  
        [<entID> <entID> <entID>] ''roof'' tag -> 
        [<entID> <entID>] [''roof'' ''house''] tag -> 
        last ''door'' tag -> 
    """
    if not inc.entid_or_LST_of_entids(E.The,2) or not inc.TXT_or_LST_of_TXTs(E.The,1):
        print("Input Error: tag")
        print(intf_ENTTAG.__doc__)
        return # Without doing much of anything.
    refreshview= False # No need unless view attributes (@) have been set.
    mytags= E.The.StackPop().val
    if type(mytags)==type(list()):
        #mytags= map(lambda x:x.val, mytags) # Should now be a list of TXTs.
        mytags= [x.val for x in  mytags] # Should now be a list of TXTs.
    else:
        mytags= [ mytags ] # Also a (1 item) list of ints.
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of VALs.
        myeids= [x.val for x in  myeids] # Should now be a list of VALs.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            for mytag in mytags:
                if len(mytag) > 1 and '@' == mytag[1]:
                    refreshview= True
                    existing_att_tags= MMEL.El[myeid].has_tag_starting_with(mytag[0:2])
                    if existing_att_tags:
                        for et in  existing_att_tags:
                            MMEL.El[myeid].del_tag(et)
                print("Tagging entity #%d with tag ''%s''" % (myeid,mytag))
                if not MMEL.El[myeid].has_tag(mytag):
                    MMEL.El[myeid].add_tag(mytag)
        else:
            print("Warning: No entity #%d. Skipping." % myeid)
    if refreshview: OUT.default(MMEL,E) # AUTODUMP 
internal_syms['tag']= intf_ENTTAG # Register function.

def intf_ENTCHTAG(E):
    """ From level three either an entity ID value or a list of entity ID values
    off the stack. From level two, a TXT object of an existing tag is
    taken off the stack. Finally from level one, the TXT object of the new
    replacement tag is taken.
    Any specified entities which are tagged with the specified tags will have
    those tags removed and replaced with the new one.
        <entID> ''roof'' ''wall'' chtag ->  
        [<entID> <entID> <entID>] ''roof'' ''wall'' chtag -> 
    """
    if ( not inc.entid_or_LST_of_entids(E.The,3) or
         not inc.TXT(E,2) or not inc.TXT(E,1) ):
        print("Input Error: chtag")
        print(intf_ENTCHTAG.__doc__)
        return # Without doing much of anything.
    refreshview= False # No need unless view attributes (@) have been affected.
    newtag= E.The.StackPop().val
    oldtag= E.The.StackPop().val
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of VALs.
        myeids= [x.val for x in  myeids] # Should now be a list of VALs.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            if MMEL.El[myeid].has_tag(oldtag):
                print("Untagging entity #%d with tag ''%s''" % (myeid,oldtag))
                MMEL.El[myeid].del_tag(oldtag)
                MMEL.El[myeid].add_tag(newtag)
                if '@' in oldtag or '@' in newtag: refreshview= True
        else:
            print("Warning: No entity #%d. Skipping." % myeid)
    if refreshview: OUT.default(MMEL,E) # AUTODUMP 
internal_syms['chtag']= intf_ENTCHTAG # Register function.

def intf_ENTUNTAG(E):
    """ From level two either an entity ID value or a list of entity ID values
    off the stack. From level one, a TXT object or a list of TXT objects is
    taken off the stack. Any specified entities which are tagged with any of
    the specified tags will have those tags removed.
        <entID> ''roof'' untag ->  
        [<entID> <entID> <entID>] ''roof'' untag -> 
        [<entID> <entID>] [''roof'' ''house''] untag -> 
        last ''door'' untag -> 
    """
    if not inc.entid_or_LST_of_entids(E.The,2) or not inc.TXT_or_LST_of_TXTs(E.The,1):
        print("Input Error: untag")
        print(intf_ENTUNTAG.__doc__)
        return # Without doing much of anything.
    refreshview= False # No need unless view attributes (@) have been set.
    mytags= E.The.StackPop().val
    if type(mytags)==type(list()):
        #mytags= map(lambda x:x.val, mytags) # Should now be a list of TXTs.
        mytags= [x.val for x in  mytags] # Should now be a list of TXTs.
    else:
        mytags= [ mytags ] # Also a (1 item) list of ints.
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of VALs.
        myeids= [x.val for x in myeids] # Should now be a list of VALs.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            for mytag in mytags:
                if MMEL.El[myeid].has_tag(mytag):
                    print("Untagging entity #%d with tag ''%s''" % (myeid,mytag))
                    MMEL.El[myeid].del_tag(mytag)
                    if '@' in mytag: refreshview= True
        else:
            print("Warning: No entity #%d. Skipping." % myeid)
    if refreshview: OUT.default(MMEL,E) # AUTODUMP 
internal_syms['untag']= intf_ENTUNTAG # Register function.

def intf_ENTDETAG(E):
    """Supply an entity ID or list of entity IDs  on the stack and this
    function will remove all tags from the supplied entities. To remove all
    tags from all entities, use `all detag`. Entity IDs are consumed."""
    if not inc.entid_or_LST_of_entids(E.The,1):
        print("Input Error: detag")
        print(intf_ENTDETAG.__doc__)
        return # Without doing much of anything.
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of ints.
        myeids= [x.val for x in  myeids] # Should now be a list of ints.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            MMEL.El[myeid].tags= list()
        else:
            print("WARNING: Entity ID# %d does not exist." % myeid)
    OUT.default(MMEL,E) # AUTODUMP 
internal_syms['detag']= intf_ENTDETAG # Register function.

def intf_TAGQUERY(E):
    """From level one, a TXT object or a list of TXT objects is taken off the
    stack. The entities which are tagged with the specified text items are
    returned in a list. An empty list is returned if no entities are tagged
    with the supplied tags.
    ''mytag'' tag? -> [<entID> <entID>]
    [''mytag1'' ''mytag2''] tag? -> [<entID> <entID]
    This will find any entities tagged with both "roof" and "house".
    [''roof'' ''house''] tag? -> [<entID> <entID>]
    This usage implies an *and* operation where all tags supplied must
    apply to the entity. To achieve an *or* effect use a construction like
    this.
    [''roof'' ''house''] tag? [''roof'' ''barn''] tag? + -> [<entID> <entID>]
    """
    if not inc.TXT_or_LST_of_TXTs(E.The,1):
        print("Input Error: tag?")
        print(intf_TAGQUERY.__doc__)
        return # Without doing much of anything.
    mytags= E.The.StackPop().val
    if type(mytags)==type(list()):
        #mytags= map(lambda x:x.val, mytags) # Should now be a list of TXTs.
        mytags= [x.val for x in mytags] # Should now be a list of TXTs.
    else:
        mytags= [ mytags ] # Also a (1 item) list of ints.
    qualifying_ents= list()
    for myeid in MMEL.El.keys():
        alltagshere= True # Assume they're here until one is not found.
        for mytag in mytags:
            #print("Searching entity #%d for tag ''%s''" % (myeid,mytag))
            if not MMEL.El[myeid].has_tag(mytag):
                alltagshere= False
                break
        if alltagshere:
            qualifying_ents.append( objectifier.StackOB_VAL(myeid) )
    E.The.StackPush( objectifier.StackOB_LST(qualifying_ents) )
internal_syms['tag?']= intf_TAGQUERY # Register function.

def intf_TAGNOTQUERY(E):
    """From level one, a TXT object or a list of TXT objects is taken off the
    stack. The entities which are NOT tagged with all the specified text items
    are returned in a list. An empty list is returned if no entities are tagged
    with the supplied tags.
    ''mytag'' nottag? -> [<entID> <entID>]
    [''mytag1'' ''mytag2''] nottag? -> [<entID> <entID]
    This will find any entities tagged with neither "roof" nor "house".
    [''roof'' ''house''] nottag? -> [<entID> <entID>]
    Actually right now it will find entities not tagged with *both* "roof" and
    "house".
    """
    if not inc.TXT_or_LST_of_TXTs(E.The,1):
        print("Input Error: nottag?")
        print(intf_TAGNOTQUERY.__doc__)
        return # Without doing much of anything.
    mytags= E.The.StackPop().val
    if type(mytags)==type(list()):
        #mytags= map(lambda x:x.val, mytags) # Should now be a list of TXTs.
        mytags= [x.val for x in mytags] # Should now be a list of TXTs.
    else:
        mytags= [ mytags ] # Also a (1 item) list of ints.
    disqualifying_ents= list()
    for myeid in MMEL.El.keys():
        atagishere= False # Assume they're here until one is not found.
        for mytag in mytags:
            #print("Searching entity #%d for tag ''%s''" % (myeid,mytag))
            if MMEL.El[myeid].has_tag(mytag):
                atagishere= True
                break
        if atagishere:
            disqualifying_ents.append( myeid )
    qualifying_ents= list() # For inverting.
    for myeid in MMEL.El.keys(): # Go through all ents again.
        if myeid not in disqualifying_ents: # Add ones not found before.
            qualifying_ents.append(myeid)
    # Objectify remaining.
    qualifying_ents= [objectifier.StackOB_VAL(m) for m in qualifying_ents] 
    E.The.StackPush( objectifier.StackOB_LST(qualifying_ents) )
internal_syms['nottag?']= intf_TAGNOTQUERY # Register function.

def intf_ENTPTS(E):
    """Supply a number on the stack and this function will return
    the geometry of that entity. If a list of entity IDs is supplied,
    return geometry data for each."""
    if not inc.entid_or_LST_of_entids(E.The,1):
        print("Input Error: pts")
        print(intf_ENTPTS.__doc__)
        return # Without doing much of anything.
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of ints.
        myeids= [x.val for x in myeids] # Should now be a list of ints.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    for myeid in myeids:
        # NEEDS TO CHECK IF EID EXISTS!
        if myeid in MMEL.El: # Check if eid exists.
            pids= MMEL.El[myeid].epts # List of point IDs for this entity.
            for pid in pids:
                x= mm.Entity.allplist.PLdict[pid].x
                y= mm.Entity.allplist.PLdict[pid].y
                z= mm.Entity.allplist.PLdict[pid].z
                z= objectifier.StackOB_VAL(z) # Can't be just regular Python ints.
                y= objectifier.StackOB_VAL(y)
                x= objectifier.StackOB_VAL(x)
                p= objectifier.StackOB_LST([x, y, z])
                p.names= ['x','y','z']
                E.The.StackPush(p)
        else:
            print("Warning: No entity #%d. Skipping." % myeid)
internal_syms['entpts']= intf_ENTPTS # Register function.
internal_syms['pts']= intf_ENTPTS # Register function.

def intf_DIST(E):
    """Given two points (LSTs of three VALs) on stack level 2 and 1,
    compute distance between the two supplied points. For example:
        [5 5 5] [8 9 5] dist -> 5
    To get the length of a line use something like:
        <entID> pts dist ->
    """
    if    ( not E.The.StackSize() >= 2
            or not inc.point_formatted_LST(E.The,1)
            or not inc.point_formatted_LST(E.The,2) ):
        print("Input Error: dist")
        print(intf_DIST.__doc__)
        return # Without doing much of anything.
    import math
    P1object= E.The.StackPop()
    #P1= map(lambda x:x.val, P1object.val) # Should now be a list of floats.
    P1= [x.val for x in P1object.val] # Should now be a list of floats.
    P0object= E.The.StackPop()
    #P0= map(lambda x:x.val, P0object.val) # Should now be a list of floats.
    P0= [x.val for x in P0object.val] # Should now be a list of floats.
    dx= (P1[0]-P0[0])
    dy= (P1[1]-P0[1])
    dz= (P1[2]-P0[2])
    D= math.sqrt(dx*dx + dy*dy + dz*dz)
    d= objectifier.StackOB_VAL(D) # Can't be just regular Python ints.
    E.The.StackPush(d)
internal_syms['dist']= intf_DIST # Register function.

def intf_ANGLE(E):
    """Given 3 points (LSTs of three VALs) on stack level 3, 2 and 1, compute
    the angle in degrees between the two supplied points of level 3 and 2, and
    the two supplied points of level 2 and 1. For example:
        [5 5 0] [0 0 0] [-5 5 5] angle -> 90
    To get the angle between two line entities which share an endpointuse 
    something like:
        <entID1> pts <entID2> pts swap drop angle ->
    If the line entities do not share an endpoint, wait until the intersection
    function is complete.
    """
    if    ( not E.The.StackSize() >= 3
            or not inc.point_formatted_LST(E.The,1)
            or not inc.point_formatted_LST(E.The,2)
            or not inc.point_formatted_LST(E.The,3) ):
        print("Input Error: angle")
        print(intf_ANGLE.__doc__)
        return # Without doing much of anything.
    import math
    Cobject= E.The.StackPop()
    #C= map(lambda x:x.val, Cobject.val) # Should now be a list of floats.
    C= [x.val for x in Cobject.val] # Should now be a list of floats.
    Bobject= E.The.StackPop()
    #B= map(lambda x:x.val, Bobject.val) # Should now be a list of floats.
    B= [x.val for x in Bobject.val] # Should now be a list of floats.
    Aobject= E.The.StackPop()
    #A= map(lambda x:x.val, Aobject.val) # Should now be a list of floats.
    A= [x.val for x in Aobject.val] # Should now be a list of floats.
    v1= [ A[0]-B[0], A[1]-B[1], A[2]-B[2] ]
    v2= [ C[0]-B[0], C[1]-B[1], C[2]-B[2] ]
    v1mag= math.sqrt( v1[0]*v1[0] + v1[1]*v1[1] + v1[2]*v1[2] )
    v2mag= math.sqrt( v2[0]*v2[0] + v2[1]*v2[1] + v2[2]*v2[2] )
    try:
        v1norm= [x/v1mag for x in v1]
        v2norm= [x/v2mag for x in v2]
        dotprod= v1norm[0]*v2norm[0] + v1norm[1]*v2norm[1] + v1norm[2]*v2norm[2]
        a= math.acos(dotprod) * 180 / math.pi
    except ZeroDivisionError:
        print("The supplied points are not distinct or have some other math problem.")
        return
    d= objectifier.StackOB_VAL(a) # Can't be just regular Python ints.
    E.The.StackPush(d)
internal_syms['angle']= intf_ANGLE # Register function.

def intf_MIDN(E):
    """Given two points (LSTs of three VALs) on stack level 3 and 2
    followed by a ratio N on level 1, compute the point on the line
    between the two supplied points N times the distance along the
    line. For example:
        [1 1 1] [6 11 16] .2 midn -> [2 3 4]
    Setting N to .5 returns the midpoint. This function can also
    extrapolate the supplied line as in:
        [0 0 0] [5 10 15] 2 midn -> [10 20 30]
    To get the midpoint of a line use something like:
        <entID> pts .5 midn
    Or use the built in alias for that:
        <entID> pts mid
    """
    inputok= False
    if E.The.StackSize() >= 3: # Ensure something is here.
        checkob= E.The.StackCopyItemLast() 
        if checkob.whatami == "VAL":
            inputok= True
    if not inputok or not inc.point_formatted_LST(E.The,2) or not inc.point_formatted_LST(E.The,3):
        print("Input Error: midn")
        print(intf_MIDN.__doc__)
        return # Without doing much of anything.
    ratio= E.The.StackPop().val
    P1object= E.The.StackPop()
    #P1= map(lambda x:x.val, P1object.val) # Should now be a list of floats.
    P1= [x.val for x in P1object.val] # Should now be a list of floats.
    P0object= E.The.StackPop()
    #P0= map(lambda x:x.val, P0object.val) # Should now be a list of floats.
    P0= [x.val for x in P0object.val] # Should now be a list of floats.
    x= (P1[0]-P0[0]) * ratio + P0[0]
    y= (P1[1]-P0[1]) * ratio + P0[1]
    z= (P1[2]-P0[2]) * ratio + P0[2]
    z= objectifier.StackOB_VAL(z) # Can't be just regular Python ints.
    y= objectifier.StackOB_VAL(y)
    x= objectifier.StackOB_VAL(x)
    p= objectifier.StackOB_LST([x, y, z])
    p.names= ['x','y','z']
    E.The.StackPush(p)
internal_syms['midn']= intf_MIDN # Register function.
internal_syms['%n']= intf_MIDN # Register function.

def intf_MID(E):
    """Given two points (LSTs of three VALs) on stack level 2 and 1,
    compute the midpoint on the line between the two supplied points.
    For example:
        [100 -10.1 2048] [0 0 0] mid -> [50 -5.05 1024]
    This is basically the same as:
        .5 midn ->"""
    pt5= objectifier.StackOB_VAL(.5)
    E.The.StackPush(pt5)
    intf_MIDN(E)
internal_syms['mid']= intf_MID # Register function.
internal_syms['%']= intf_MID # Register function.


def intf_LASTENTID(E):
    """Taking nothing from the stack, return the entity ID for the most
    recent entity."""
    #lasteid= sorted(MMEL.El.keys())[-1]
    lasteid= MMEL.last_ent()
    lasteid_so= objectifier.StackOB_VAL(lasteid)
    E.The.StackPush(lasteid_so)
internal_syms['last']= intf_LASTENTID # Register function.

def intf_LASTNENTID(E):
    """Takes a single VAL as n, returns the entity ID for the most recent
    entity's EID minus (n-1) in the list of extant entities."""
    n= int(E.The.StackPop().val)
    try:
        lasteid= sorted(MMEL.El.keys())[-n]
        lasteid_so= objectifier.StackOB_VAL(lasteid)
        E.The.StackPush(lasteid_so)
    except IndexError:
        print("Error: Not enough entities.")
internal_syms['lastn']= intf_LASTNENTID # Register function.

def intf_ALLENTID(E):
    """Returns a list of every entity ID in the memory model."""
    alleids= MMEL.El.keys()
    alleids_so= [objectifier.StackOB_VAL(eid) for eid in alleids]
    alleids_so= objectifier.StackOB_LST(alleids_so)
    E.The.StackPush(alleids_so)
internal_syms['all']= intf_ALLENTID # Register function.
internal_syms['allent']= intf_ALLENTID # Register function.

def intf_ENTDUPS(E):
    """Returns a list of every entity ID in the memory model which has
    an earlier (lower EID) corresponding entity which shares all of the
    exact same points. This is handy for managing duplicate entities.
    To completely clean up a model of duplicated entities, 
        all edup? ~ -> """
    if not inc.entid_or_LST_of_entids(E.The,1):
        print("Input Error: doubles")
        print(intf_ENTERASE.__doc__)
        return # Without doing much of anything.
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of ints.
        myeids= [x.val for x in myeids] # Should now be a list of ints.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    some_doubles= list()
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            if not myeid in some_doubles:
                new_doubles= MMEL.find_doubles_of(MMEL.El[myeid])
                some_doubles+= new_doubles
        else:
            print("WARNING: Entity ID# %d does not exist." % myeid)
    if some_doubles:
        some_doubles_so= [objectifier.StackOB_VAL(eid) for eid in some_doubles]
        some_doubles_so= objectifier.StackOB_LST(some_doubles_so)
        E.The.StackPush(some_doubles_so)
    else:
        E.The.StackPush( objectifier.StackOB_LST( list() ))
internal_syms['edup?']= intf_ENTDUPS # Register function.
internal_syms['doubles']= intf_ENTDUPS # Register function.

def intf_ENTERASE(E):
    """Supply an entity ID or a list of entity IDs on the stack and this
    function will delete it. Points used in the specified entity will be
    removed if not used elsewhere."""
    if not inc.entid_or_LST_of_entids(E.The,1):
        print("Input Error: erase")
        print(intf_ENTERASE.__doc__)
        return # Without doing much of anything.
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of ints.
        myeids= [x.val for x in myeids] # Should now be a list of ints.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            MMEL.del_ent(myeid)
        else:
            print("WARNING: Entity ID# %d does not exist." % myeid)
    OUT.default(MMEL,E) # AUTODUMP 
internal_syms['erase']= intf_ENTERASE # Register function.
internal_syms['~']= intf_ENTERASE # Register function.

def intf_ENTDUP(E):
    """Supply an entity ID or list of entity IDs  on the stack and this
    function will create a new entity of the same type and using the same
    points. The new entity id or list of ids will be returned to the stack."""
    if not inc.entid_or_LST_of_entids(E.The,1):
        print("Input Error: entdup")
        print(intf_ENTDUP.__doc__)
        return # Without doing much of anything.
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of ints.
        myeids= [x.val for x in myeids] # Should now be a list of ints.
        listify= True
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
        listify= False
    new_eid= list()
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            src_ent= MMEL.El[myeid]
            new_ent= src_ent.duplicate()
            MMEL.add_ent(new_ent)
            if listify:
                new_eid.append( objectifier.StackOB_VAL(new_ent.eid) )
            else:
                new_eid= objectifier.StackOB_VAL(new_ent.eid)
        else:
            print("WARNING: Entity ID# %d does not exist." % myeid)
    if new_eid:
        if listify:
            new_eid= objectifier.StackOB_LST(new_eid)
        E.The.StackPush(new_eid)
internal_syms['entdup']= intf_ENTDUP # Register function.
internal_syms['edup']= intf_ENTDUP # Register function.

def intf_ENTMOVE(E):
    """Supply an entity ID number (or a list of IDs) followed by a coordinate
    list (e.g. [3.5 -2 0]) on the stack and this function will remove them from
    the stack and move each point in the entity by the ammounts in the
    coordinate list vector."""
    input1ok= False
    if E.The.StackSize() >= 2: 
        # CHECK INPUT #1
        # Check that next ready stack item is a LST of 3 VALs.
        check= E.The.StackCopyItemLast() # Input verification. Next item on stack now.
        # Probably should use inc.point_formatted_LST here. See ENTPGRAM.
        if check.whatami == "LST":
            if len(check.val)==3:
                #if not filter(lambda x:x.whatami!="VAL",check.val):
                if all([x.whatami=="VAL" for x in check.val]):
                    input1ok= True
    if not input1ok or not inc.entid_or_LST_of_entids(E.The,2):
        print("Input Error: move")
        print(intf_ENTMOVE.__doc__)
        return # Without doing much of anything.
    myoffset= [ xyz.val for xyz in E.The.StackPop().val ] # A list [3.5 -2 0].
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of ints.
        myeids= [x.val for x in myeids] # Should now be a list of ints.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            myent= MMEL.El[myeid]
            myent.translate(myoffset)
        else:
            print("WARNING: Entity ID# %d does not exist." % myeid)
    OUT.default(MMEL,E) # AUTODUMP 
internal_syms['move']= intf_ENTMOVE # Register function.
internal_syms['m']= intf_ENTMOVE # Register function.

def intf_ENTPGRAM(E):
    """Takes an entity or list of entities from v3 and two point formatted
    lists from v2 and v1 (which could come from a line entity number supplied
    to the `pts` function) and creates a parallelogram. This parallelogram
    consists of the original supplied line entity, a new parallel line entity,
    two new line entites connecting the endpoints of the other lines, and two
    trifaces which cover the entire area of the parallelogram."""
    # !! Need to check for some eids being TRIs. Filter that out.
    if ( not inc.entid_or_LST_of_entids(E.The,3) or 
         not inc.point_formatted_LST(E.The,2) or
         not inc.point_formatted_LST(E.The,1) ):
        print("Input Error: pgram")
        print(intf_ENTPGRAM.__doc__)
        return # Without doing much of anything.
    oB= [ xyz.val for xyz in E.The.StackPop().val ] # A list [3.5 -2 0].
    oA= [ xyz.val for xyz in E.The.StackPop().val ] # A list [3.5 -2 0].
    myeids= E.The.StackPop().val
    if type(myeids)==type(list()):
        #myeids= map(lambda x:x.val, myeids) # Should now be a list of ints.
        myeids= [x.val for x in myeids] # Should now be a list of ints.
    else:
        myeids= [ myeids ] # Also a (1 item) list of ints.
    neweidlist= []
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            src_ent= MMEL.El[myeid]
            new_ent= src_ent.duplicate()
            new_ent.translate([ oB[0]-oA[0], oB[1]-oA[1], oB[2]-oA[2] ])
            As= mm.Entity.allplist.PLdict[ src_ent.epts[0] ]
            Ae= mm.Entity.allplist.PLdict[ src_ent.epts[1] ]
            Bs= mm.Entity.allplist.PLdict[ new_ent.epts[0] ]
            Be= mm.Entity.allplist.PLdict[ new_ent.epts[1] ]
            neweidlist.append(new_ent.eid)
            MMEL.add_ent(new_ent)
            line_entS= mm.Line_Entity( [As,Bs] )
            neweidlist.append(line_entS.eid)
            MMEL.add_ent(line_entS)
            line_entE= mm.Line_Entity( [Ae,Be] )
            neweidlist.append(line_entE.eid)
            MMEL.add_ent(line_entE)
            tri_entA= mm.Tri_Entity( [As, Ae, Bs] )
            neweidlist.append(tri_entA.eid)
            MMEL.add_ent(tri_entA)
            tri_entB= mm.Tri_Entity( [Bs, Be, Ae] )
            neweidlist.append(tri_entB.eid)
            MMEL.add_ent(tri_entB)
        else:
            print("WARNING: Entity ID# %d does not exist." % myeid)
    if neweidlist:
        neweids= objectifier.StackOB_LST( [objectifier.StackOB_VAL(x) for x in neweidlist] )
        E.The.StackPush(neweids)
    OUT.default(MMEL,E) # AUTODUMP 
internal_syms['pgram']= intf_ENTPGRAM # Register function.
internal_syms['parallelogram']= intf_ENTPGRAM # Register function.

def intf_ENTROTATE(E):
    """Rotate one or more entities around a provided axis by a provided angle.
       This function takes 3 items off the stack. In order of entry, the third
       item is either an entity ID value or a list of one or more entity IDs.
       These are the entities which will be modified by the rotation.
       The second item is the axis of rotation. It can be an entity ID value
       of a line entity (tri entities are not supported) or it can be a list
       containing precisely two lists which each contain three values. This
       list contains two coordinate lists for points on (defining) a line. This
       line is the axis of rotation. If you point your right thumb from the
       first point on this line to the second point, your fingers will curve in
       a postive rotation. Finally, the first item popped off the stack (last
       entered) is the angle in degrees of the rotation. An example is `[2 4
       13] [[0 0 0][0 0 1]] 45 rotate ->`, which would rotate entities 2, 4,
       and 13 by 45 degrees counter clockwise when seen looking from the second
       reference axis point ([0 0 1]) to the first ([0 0 0])."""
    # Input must be in one of the following forms:
    # A.  V V V ->
    # B.  V [[V V V][V V V]] V ->
    # C.  [V...V] V V ->
    # D.  [V...V] [[V V V][V V V]] V ->
    # == Check Input ==
    input1ok,input2ok= False,False
    if E.The.StackSize() >= 3: 
        # === Check Item #1 ===
        # Check that next ready stack item is a VAL (degrees to rotate).
        check= E.The.StackCopyItemLast() # Input verification. Next item on stack now.
        if check.whatami == "VAL":
            input1ok= True
            # === Check Item #2 === 
            # Check that stack item 2 (penultimate) is a LST of 2 LST, OR a VAL.
            check= E.The.StackCopyItemN(2)
            if check.whatami == "LST":
                if len(check.val) == 2:
                    #if not filter(lambda x:x.whatami!="LST",check.val):
                    if all([x.whatami=="LST" for x in check.val]):
                        #if (not filter(lambda x:x.whatami!="VAL",check.val[0].val) and
                        #    not filter(lambda x:x.whatami!="VAL",check.val[1].val) ):
                        if ( all([x.whatami=="VAL" for x in check.val[0].val]) and 
                             all([x.whatami=="VAL" for x in check.val[1].val]) ):
                            input2ok= True
            elif check.whatami == "VAL":
                input2ok= True # Might want to check here if entityID exists.
    if not input1ok or not input2ok or not inc.entid_or_LST_of_entids(E.The,3):
        print("Input Error: rotate")
        print(intf_ENTROTATE.__doc__)
        return # Without doing much of anything.
    # == Parse Input ==
    # === Parse Item #1 ===
    myangle= E.The.StackPop().val # degrees
    # === Parse Item #2 ===
    axisP0,axisP1= [0,0,0],[0,0,1] # Defaults if there are problems.
    axis_object= E.The.StackPop() # either 1 line eid VAL OR LST:[LST LST]]
    if axis_object.whatami == "LST":
        P0object= axis_object.val[0] # A LST of 3 VALs.
        if len(P0object.val) == 3:
            #axisP0= map(lambda x:x.val, P0object.val) # Should now be a list of floats.
            axisP0= [x.val for x in P0object.val] # Should now be a list of floats.
        else:
            print("Error: First axis point defined badly. Assuming: [0 0 0]")
        P1object= axis_object.val[1]
        if len(P1object.val) == 3:
            #axisP1= map(lambda x:x.val, P1object.val) # Should now be a list of floats.
            axisP1= [x.val for x in P1object.val] # Should now be a list of floats.
        else:
            print("Error: Second axis point defined badly. Assuming: [0 0 1]")
        # LST:[ LST:[ VAL VAL VAL ] LST:[ VAL VAL VAL ] ]
    elif axis_object.whatami == "VAL":
        axis_eid= int(axis_object.val)
        if axis_eid in MMEL.El: # Check if axis_eid exists.
            axis_ent= MMEL.El[axis_eid]
            if axis_ent.etype is "Line":
                x= mm.Entity.allplist.PLdict[ axis_ent.epts[0] ].x
                y= mm.Entity.allplist.PLdict[ axis_ent.epts[0] ].y
                z= mm.Entity.allplist.PLdict[ axis_ent.epts[0] ].z
                axisP0=[x,y,z]
                x= mm.Entity.allplist.PLdict[ axis_ent.epts[1] ].x
                y= mm.Entity.allplist.PLdict[ axis_ent.epts[1] ].y
                z= mm.Entity.allplist.PLdict[ axis_ent.epts[1] ].z
                axisP1=[x,y,z]
            else:
                print("Warning: Specified axis entity was not a line. Assuming: [[0 0 0][0 0 1]]")
        else:
            print("Warning: Specified axis entity did not exist. Assuming: [[0 0 0][0 0 1]]")
    else:
        print("Error: This should never happen. Input check in rotation function failed.")
        return
    # === Parse Item #3 ===
    myents_object= E.The.StackPop() # either 1 eid or a LST of eid VALs
    if myents_object.whatami=="LST":
        #myeids= map(lambda x:x.val, myents_object.val) # Should now be a list of ints.
        myeids= [x.val for x in myents_object.val] # Should now be a list of ints.
    else:
        myeids= [ myents_object.val ] # Also a (1 item) list of ints.
    # == Iterate Over Target Entities  ==
    for myeid in myeids:
        if myeid in MMEL.El: # Check if eid exists.
            myent= MMEL.El[myeid]
            #print('myent.rotate(%s,%s,%s)' % (myangle.__repr__(),axisP0.__repr__(),axisP1.__repr__()))
            # Looks like this: myent.rotate(22.5,[-1.0, -2.0, -3.0],[4.4, 5.5, 6.6])
            #DO THE ROTATION HERE!!!!!!!!!!!
            myent.rotate(myangle,axisP0,axisP1)
        else:
            print("WARNING: Entity ID# %d does not exist." % myeid)
    OUT.default(MMEL,E) # AUTODUMP 
internal_syms['rotate']= intf_ENTROTATE # Register function.

def intf_MMTEST(E):
    """Simple test of the creation of a mm function. Get rid of this when
    everything is working fine."""
    macro= "10 10 0 p dup 100 10 0 p dup rot l drop 50 100 0 p dup rot l drop l drop"
    oblistcontent= list()
    for s in macro.split(' '):
        try:
            s= float(s)
        except ValueError:
            pass
        if type(s) == type('str'):
            oblistcontent.append(objectifier.StackOB_SYM(s))
        else:
            oblistcontent.append(objectifier.StackOB_VAL(s))
    testmacro= objectifier.StackOB_LST(oblistcontent) 
    testmacro.dead= False
    E.The.StackPush(testmacro)
internal_syms['mmtest']= intf_MMTEST # Register function.
