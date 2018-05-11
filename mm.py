#!/usr/bin/python
# Chris X Edwards - Sat Apr  5 06:49:58 PDT 2014
# mm.py
# The memory model module is responsible for handling keeping all of the
# geometry organized in memory. It has a class to verify and work with
# 3d Coords. It provides a way to store points with automatic optimization
# through Point objects and a managed PointList object. It provides the entity
# definitions and features. It provides an EntityList to contain all the
# Entity objects which comprise the model.

# Eliminate tiny rounding errors so that actually identical points are truly so.
CLOSE_ENOUGH= .0000001

class Coords:
    """Stores just the coordinates of a possible point. For use in temporary
    calculations and tests. These are not reference counted or stored in the
    memory model in any way. So when checking, does some entity contain
    location P? P will be a Coords object. Initialize with a list of [X Y Z]."""
    def __init__(self, C):
        #print(C)
        try:
            self.x= C[0]
            self.y= C[1]
            self.z= C[2]
        except:
            self.x= C.x
            self.y= C.y
            self.z= C.z
    #def __cmp__(self, other): #IMPOSSIBLE to be ==
    #def __getitem__(self,i):
    #    return [self.x,self.y,self.z]
    def xyzlist(self):
        return [self.x, self.y, self.z]
    def distance_to_coord(self, C):
        """Returns Cartesian distance between self coord and supplied coord.
        Handy for checking sameness of location."""
        import math
        xd= self.x - C.x
        yd= self.y - C.y
        zd= self.z - C.z
        if zd:
            return math.sqrt((xd * xd) + (yd * yd) + (zd * zd))
        else:
            return math.sqrt((xd * xd) + (yd * yd))
    def __repr__(self):
        out= "Coord:  (%.2f, %.2f, %.2f)" % ( self.x, self.y, self.z )
        return out

class Point(Coords):
    """Stores data about a point needed for it to be tracked in memory model.
    Classwide register to always provide fresh ID numbers. Reference counting
    done here per point."""
    pidregister= int(0) # Used to assign unique sequential PIDs.
    def __init__(self, C):
        Coords.__init__(self,C)
        Point.pidregister += 1
        self.pid= Point.pidregister
        self.refcount= 1
    #def __cmp__(self, other): 
        #IMPOSSIBLE to be ==
    #def fancy_repr(self):
    #   out= "PID:%03d  (%.2f, %.2f, %.2f) {%d}" % (
    #           self.pid, self.x, self.y, self.z, self.refcount )
    #   return out
    def __repr__(self):
        out= "%03d %.2f %.2f %.2f" % (
                self.pid, self.x, self.y, self.z )
        return out
    def xyz_repr(self):
        out= "[%.2f %.2f %.2f]" % ( self.x, self.y, self.z )
        return out
    def to2d_repr(self):
        x= ("%s" % self.x).rstrip('0').rstrip('.')
        y= ("%s" % self.y).rstrip('0').rstrip('.')
        z= ("%s" % self.z).rstrip('0').rstrip('.')
        out= "%d %s %s %s\n" % (self.pid, x, y, z )
        return out
    def simplistic_save_repr(self):
        """Returns a string just like you'd need to type in the 
        interpreter to get this point."""
        outlist=  [ ("%f" % self.x).rstrip('0').rstrip('.'),
                    ("%f" % self.y).rstrip('0').rstrip('.'), 
                    ("%f" % self.z).rstrip('0').rstrip('.')]
        return ' '.join(outlist)

class PointList:
    """This is a fancy point list that knows how to keep track of duplicate
    points by manipulating a Point entity's reference counting. It is stored
    as a dict so that when points are removed, they can all still keep the
    same look-up keys. With a list, if p[2] is removed, p[3] is now
    p[2]. With this scheme, p[2] is always p[2]. The order doesn't matter."""
    def __init__(self):
        # This is a dict so that deleted points won't mess up the numbering.
        # In other words, PLdict[16] is always the same even if PLdict[15] disappeared.
        self.PLdict= dict() # Key= P.pid, Val= P
    def find_point(self, C):
        for p in self.PLdict.values():
            if p.distance_to_coord(C) < CLOSE_ENOUGH:
                return p
        return None
    def __getitem__(self, k):
        return self.PLdict[k]
    def get_ob_from_id(self,i):
        return self.PLdict[i]
    def add_point(self, C):
        p_exists= self.find_point(C)
        if p_exists:
            p_exists.refcount += 1 # Add to it's ref.
            return p_exists.pid
        else:
            newP= Point(C)
            self.PLdict[newP.pid]= newP # Add it for real.
            #return Point.pidregister # Could be bad with concurrent ops.
            return newP.pid
    def del_point(self, P):
        if P: # Ignore if nothing.
            P.refcount -= 1
            if P.refcount < 1:
                self.PLdict.pop(P.pid)
    def __repr__(self):
        out= ''
        for p in self.PLdict.values():
            out+= repr(p) + '\n'
        return out

class Entity:
    eidregister= int(0) # Used to assign unique sequential EIDs.
    allplist= PointList()
    def __init__(self,inpts): # Always takes a list for spwan consistency. Here, empty.
        self.etype= "Unspecified"
        self.epts= list() # This entity's points, a normal list of Point.pid 
        self.eid= Entity.eidregister 
        Entity.eidregister += 1
        self.tags= list()
        #self.attriblist= None
    def mmlist_repr(self):
        o= str(self.eid) + ": "
        o += self.etype
        for p in self.epts:
            pob= Entity.allplist.get_ob_from_id(p)
            o += ' '+pob.xyz_repr()
        if self.tags:
            o += ' ['+' '.join(self.tags)+']'
        return o
    def fancy_repr(self):
        o= "EID:%03d Type:%s\n" % (self.eid, self.etype)
        for p in self.epts:
            o += "  " + str(Entity.allplist.PLdict[p]) +'\n'
        return o
    def __repr__(self):
        o= ' '.join(map(lambda x:str(x),list(self.epts)))
            #o += "  " + str(Entity.allplist.PLdict[p]) +'\n'
        if len(self.epts)<2: # Points are invisible in theory.
            o= "#"+o
        return o
    def simplistic_item_save_format(self):
        """Create a string that is appropriate for writing to a save file
        to store the memory model. This format will not be fancy with point
        optimization. It will just take what the Entity knows and output it
        in a way that it is possible to be read back in and reconstructed
        as if synthesizing it again. The data should be compatible with a
        "source" command."""
        o= str()
        for p in self.epts:
            o += Entity.allplist.PLdict[p].simplistic_save_repr() +' p '
        # Note: the # is to drop the unneeded eid that is produced.
        o+= "%s " % self.etype[0].lower()
        if self.tags:
            o+= "[''" + "'' ''".join(self.tags) + "''] tag "
        else:
            o+= " # "
        return o
    def __del__(self): # Deletes only one instance of each point.
        try:
            for p in self.epts:
                #print("deleting:: " + str(self.eid) + " points:" + str(Entity.allplist.PLdict[p]))
                Entity.allplist.del_point(Entity.allplist.PLdict[p])
        except TypeError:
            pass
            # Can't iterate over the point list while deleting the following entity:
            #print("Deleting %s entity #%d" % (self.etype,self.eid))
    def __lt__(self,other):
        """These comparater functions just sort on eid appearance. So Ea < Eb just
        returns true if Ea is actually newer than Eb."""
        if type(self) == type(None):
            if type(other) == type(None):
                return False # None == None
            else:
                return True # self==None IS LT not None
        elif type(other) == type(None):
            return False
        else:
            return self.eid < other.eid
    def __eq__(self,other):
        """The other operators are derived from __lt__(). Ea == Eb if they are the
        actual same entity with the same entity ID. See self.doubled() function to
        find if entities are in the same spot."""
        if type(self) == type(None):
            if type(other) == type(None):
                return True
            else:
                return False
        elif type(other) == type(None):
            return False
        else:
            return not self<other and not other<self
    def __ne__(self,other):
        return not __eq__(self, other)
    def __gt__(self,other):
        return other<self
    def __ge__(self,other):
        return not self<other
    def __le__(self,other):
        return not other<self     
    def doubled(self,other):
        """Returns true if all the points of this entity are exactly all the
        points of the other entity."""
        for ps in self.epts:
            ps_doubled= False # So far.
            for po in other.epts:
                if ps == po:
                    ps_doubled= True# This one is replicated
                    break
            if not ps_doubled:
                return False
        return True
    def duplicate(self):
        """Provides a function to replicate entities. This is the first step to
        having a clone of an object somewhere else. Note that a new EID is desired
        for the clone so they're not 100% identical. Also, point refcounts need to
        be incremented.
        Here is the E.__dict__ for an entity:
            {'etype': 'Line', 'tags': [], 'eid': 1, 'epts': [4, 5]}
        Instead of messing with that, this function just creates a new entity from
        scratch with the points from the old one.
        Q: Should the tags be duplicated too?"""
        pointoblist= [Entity.allplist.get_ob_from_id(i) for i in self.epts]
        newEntity= self.__class__(pointoblist)
        newEntity.tags= self.tags[:] # Don't have a ref'd list!
        return newEntity
    def relocate(self,incoords):
        ### THIS NEEDS A THOROUGH TESTING!! ###
        """Given a new list of coords, first check that the entity has the same number
        of points. If so, find and ignore any identical ones. Replace the rest.
        Do this by getting new points for everything (or refcount++) and then delete
        or (refcount--). This will allow still good points to be reused. (Imagine
        rotating an equilateral triangle about its center 60deg.) """
        N= len(incoords)
        if N != len(self.epts): return # Bogus. Different number of points.
        pids_to_delete= list()
        for n in range(N):
            oldpointob= Entity.allplist.get_ob_from_id(self.epts[n])
            if not oldpointob.distance_to_coord(incoords[n]) < CLOSE_ENOUGH:
                pids_to_delete.append(self.epts[n])
                updatedPid= Entity.allplist.add_point(incoords[n]) 
                self.epts[n]= updatedPid
        for d in pids_to_delete:
            Entity.allplist.del_point(Entity.allplist.PLdict[d])
    def translate(self,offsetvec):
        """Given an offset vector list (e.g. [2.5,-3,0]), apply this offset to 
        each point in an entity, i.e. just add the offset vector to each point.
        By using the `self.relocate` function, everything should be handled."""
        newcoords= list()
        N= range(len(offsetvec))
        for ept in self.epts:
            A= self.allplist[ept].xyzlist()
            newcoords.append( Coords([A[n]+offsetvec[n] for n in N]) )
        self.relocate(newcoords)
    def rotate(self,angle,axisP0,axisP1):
        """Takes 3 values. First is a float representing the angle (in
        degrees). Next two are points which define the axis of rotation.
        The order of the points dictates what direction is implied by a
        positive or negative rotation angle."""
        import math
        def matrix_multiply_3x3_by_xyz(M,P):
            x,y,z= P
            Q= P
            #[[a,b,c],[p,q,r],[u,v,w]]
            Q[0]= M['a']*x + M['b']*y + M['c']*z
            Q[1]= M['p']*x + M['q']*y + M['r']*z
            Q[2]= M['u']*x + M['v']*y + M['w']*z
            return Q
        def ptA_ptB_to_unit_vector(p0,p1):
            """Takes two [x,y,z] points representing a line and returns
            a single [x,y,z] vector which starts at [0,0,0] and ends 1
            unit away parallel to the supplied line points."""
            # Switch p0 and p1 if rotation is backwards.
            x,y,z= [ p1[n]-p0[n] for n in [0,1,2] ]
            pplen= math.sqrt( x*x + y*y + z*z ) 
            if pplen == 0:
                print("Error: Are the points supplied the same?")
            return [x/pplen,y/pplen,z/pplen]
        newcoords= list()
        Ux,Uy,Uz= ptA_ptB_to_unit_vector(axisP0,axisP1)
        for ept in self.epts: # For each point in entity.
            ent_coord= self.allplist[ept].xyzlist() # e.g. [1,2,3]
            # Move point by inverse of axisP0 so that axisP0 is the
            # origin of rotation. Move back into place later.
            inv_axisP0= [-x for x in axisP0]
            ent_coord= [ent_coord[n]+inv_axisP0[n] for n in [0,1,2] ]
            # ent_coord is an entity point in [1,2,3] format
            # new_coord is the rotated point in [1,2,3] format
            # == Actual Rotation Here == 
            """Where U is a unit vector of the arbitrary axis of rotation.
            Theta is the angle of rotation about the axis U.
            x,y,z are components of U (where x*x+y*y+z*z=1)
            C= cosine(theta) and  S= sine(theta)
            | x*x*(1-C)+C   | x*y*(1-C)-z*S  | x*z*(1-C)+y*S |
            | x*y*(1-C)+z*S | y*y*(1-C)+C    | y*z*(1-C)-x*S |
            | x*z*(1-C)+y*S | y*z*(1-C)+x*S  | z*z*(1-C)+C   |
                |a|b|c|        |x|   |ax+by+cz|
                |p|q|r| m_mult |y| = |px+qy+rz|
                |u|v|w|        |z|   |ux+vy+wz|
            """
            M= dict() # Transformation matrix.
            C= math.cos(math.radians(angle))
            S= math.sin(math.radians(angle))
            M['a']= Ux*Ux*(1-C) + C 
            M['b']= Ux*Uy*(1-C) - Uz*S
            M['c']= Ux*Uz*(1-C) + Uy*S
            M['p']= Ux*Uy*(1-C) + Uz*S
            M['q']= Uy*Uy*(1-C) + C
            M['r']= Uy*Uz*(1-C) - Ux*S
            M['u']= Ux*Uz*(1-C) + Uy*S
            M['v']= Uy*Uz*(1-C) + Ux*S
            M['w']= Uz*Uz*(1-C) + C
            new_coord= matrix_multiply_3x3_by_xyz(M,ent_coord)
            new_coord= [new_coord[n]+    axisP0[n] for n in [0,1,2] ]
            # == End of Actual Rotation ==
            newcoords.append( Coords(new_coord) )
        self.relocate(newcoords)
    def relocate_point_of_ent(self,thenewpt):
        """This is for relocating just one point of an entity, e.g. a single endpoint
        of a line. Or more efficiently, formulate the correct coords and call
        relocate or rewrite relocate in a more focused way."""
        pass
    def is_this_point_included(self,C):
        for p in self.epts:
            tempP= Coords(C)
            if self.allplist[p].distance_to_coord(tempP) < CLOSE_ENOUGH:
                return True
        return False
    def are_these_points_included(self,Clist):
        """Check to see if this entity is comprised (at least) of points which
        include the supplied points."""
        for c in Clist:
            if not self.is_this_point_included(c):
                return False
        return True
    def add_tag(self,t):
        self.tags.append(t)
    def del_tag(self,t):
        if self.has_tag(t): # Probably not needed.
            self.tags.remove(t)
    def has_tag(self,t):
        """True or false if entity contains the tag."""
        return t in self.tags
    def has_tag_starting_with(self,st):
        """True or false if entity contains a tag starting with input.
        Used to see if a tag is an attribute tag like ''C@red'' regardless
        of what the attribute value actually is. Returns any such tags
        or an empty list."""
        #return filter(lambda x:x[0:len(st)]==st, self.tags)
        return [x[0:len(st)]==st for x in self.tags]
    def attribute_tags(self):
        """Returns a dict taken from  tags in the attribute style.
        The keys are the one letter code preceeding the '@'. The
        values are everything after.
        C@color, W@width/weight, S@style/dasharray, O@opacity,
        A@arrow?, ;@ = highlight """
        #atttagsonly= filter(lambda x:(x+' ')[1]=='@',self.tags)
        atttagsonly= [(x+' ')[1]=='@' for x in self.tags]
        attdict= dict()
        for a in atttagsonly:
            attdict[a[0]]= a[2:] # Should be unique now.
        return attdict

class Point_Entity(Entity):
    def __init__(self, inpt):
        Entity.__init__(self,[inpt])
        self.etype= "Point"
        self.epts= [Entity.allplist.add_point(inpt)]

class Line_Entity(Entity):
    def __init__(self, inpts):
        Entity.__init__(self,inpts)
        self.etype= "Line"
        self.epts= [Entity.allplist.add_point(inpts[0]),
                    Entity.allplist.add_point(inpts[1])]
        
class Tri_Entity(Entity):
    def __init__(self, inpts):
        Entity.__init__(self,inpts)
        self.etype= "Triface"
        self.epts= [ Entity.allplist.add_point(inpts[0]),
                     Entity.allplist.add_point(inpts[1]),
                     Entity.allplist.add_point(inpts[2])]
        
class EntityList:
    """Manages a collection (maybe all) of the entities."""
    def __init__(self):
        """Confusingly, the El, which stands for "entity list" is actually a 
        dict which is keyed on entity ID. The values are the entity objects.
        To get an entity object from an entity ID, use `MMEL.El[eid]`."""
        self.El= dict()
    def __repr__(self):
        """Changed this to show: 'eid etype p1 p2 [p3]' which is more user
        friendly since users shouldn't ever worry about pids in mm.""" 
        o= ''
        for e in self.El:
            o += self.El[e].mmlist_repr()
            o += '\n'
        return o
    def xed3d_repr(self,t=None):
        o= ''
        for e in self.El:
            if not t or self.El[e].has_tag(t):
                o += str(self.El[e])+'\n'
        return o
    def simplistic_mm_save_format(self):
        o= ''
        for e in self.El:
            o += self.El[e].simplistic_item_save_format()+'\n'
        return o
    def add_ent(self, E):
        self.El[E.eid]= E
        #self.lastent= E # Always keep up to date with youngest entity.
        return E
    def del_ent(self, eid):
        if eid is not None and eid in self.El: # Ignore if nothing.
            self.El.pop(eid)
    def del_all(self):
        """Delete *ALL* entities!"""
        self.El= dict() # Simple as that! __del__ method cleans up nicely.
    def last_ent(self):
        """Returns the last entity added."""
        lasteid= sorted(self.El.keys())[-1]
        return lasteid
    def find_ents_by_coords(self,Clist):
        """Take a list of one or more coordinates (lists). Return all entities
        whose composition includes at least each of the supplied coordinates."""
        goods= list()
        for k in self.El:
            if self.El[k].are_these_points_included(Clist):
                goods.append(self.El[k])
        return goods
    def find_doubles_of(self,E):
        """Use the `Entity.doubled(self,other)` function to find all the 
        doubles (different entity, exact same points) in the entlist.
        Return as a list of doubles."""
        dups= list()
        for k in self.El:
            if E.eid != k and self.El[k].doubled(E):
                dups.append(k)
        return dups
    def divide_by_attribute_set(self):
        """Return a dictionary of EIDs grouped by composite attribute
        properties. This uses a dictionary to achieve unique
        categories. The keys would be dictionaries of
        attribute_tag but that's not allow. :-/ Therefore the keys are 
        a specially composed string derived from the dict designed to be
        unique the values are lists of EIDs."""
        ents_by_att= dict()
        tris= list() # All tri faces go out with each set of lines.
        for E in self.El:
            Eob= self.El[E]
            if Eob.etype == "Triface":
                tris.append(Eob)
        for E in self.El:
            if self.El[E].etype == "Triface": continue # Not yet.
            att_tag_dict= self.El[E].attribute_tags()
            att_tag_key_list= list()
            for k in att_tag_dict:
                att_tag_key_list.append( k+att_tag_dict[k] )
            # Sorting needed here? Seems like it should be necessary.
            att_tag_key= '@'.join(att_tag_key_list)
            if not (att_tag_key in ents_by_att):
                ents_by_att[att_tag_key]= list()
            ents_by_att[att_tag_key].append( self.El[E] )
        for k in ents_by_att: # Add all tris for each group.
            ents_by_att[k] += tris
        return ents_by_att

if __name__ == "__main__":
    # == Testing Coords Creation
    print("== STARTING TEST ==")
    print("== Creating Point (1,2,3):")
    some_p1= Coords([1,2,3])
    print("== Creating Point (4,5,6):")
    some_p2= Coords([4,5,6])
    print("== Output a PointXZY ('some_p1'):")
    print(some_p1)
    print("== Output a PointXZY ('some_p2'):")
    print(some_p2)
    print()

    # == Testing Point List
    print("== Creating PointList ('some_pl'):")
    some_pl= PointList()
    print("== Adding Points to PointList ('some_p1')...")
    some_pl.add_point(some_p1)
    print("== Adding Points to PointList ('some_p2')...")
    some_pl.add_point(some_p2)
    print("== Adding Points to PointList ('Coords[6,6,6]')...")
    some_pl.add_point(Coords([6,6,6]))
    print("== An Example Point List ('some_pl')")
    print(some_pl)

    # == Testing Generic Entity
    print("== Creating generic Entity ('some_e'):")
    some_e= Entity([])
    print(some_e.allplist)
    print(some_e.eid)
    print(some_e.etype)
    del(some_e)

    # == Testing Line Entities
    print("== Creating Line Entity ('some_p1') ('some_p2'):")
    some_le= Line_Entity( [some_p1, some_p2] )
    print("== Some Line Entity ('some_le'):")
    print(some_le)
    print()

    print("some_le.__dict__")
    print(some_le.__dict__)

    print("== Creating EntityList ('MMEL'):")
    MMEL= EntityList() # Memory Model Entity List
    print("== Adding to MMEL ('some_le'):")
    MMEL.add_ent( some_le )
    MMEL.El[MMEL.last_ent()].add_tag('foo')
    print(MMEL)

    print("== Creating a copy of some_le:")
    #copied_le= some_le.__copy__()
    copied_le= some_le
    print(some_le)
    #print(copied_le)
    #MMEL.add_ent( copied_le )
    print(MMEL)

    print("== Adding to MMEL ('Coords([1,2,3]), Coords([4,5,6])')")
    MMEL.add_ent( Line_Entity( [Coords([1,2,3]), Coords([4,5,6])] ) )
    print(MMEL)
    
    print("== Adding Point Entity (0,0,0):")
    MMEL.add_ent( Point_Entity( Coords([0,0,0])) )
    print(MMEL)

    print("== Adding Point Entity (7,8,9):")
    MMEL.add_ent( Point_Entity( Coords([7,8,9])) )
    print(MMEL)

    print("== Adding Point Entity (4,5,6):")
    MMEL.add_ent( Point_Entity( Coords([4,5,6])) )
    print(MMEL)

    print("== Adding Line Entity (3,2,1) (6,5,4):")
    MMEL.add_ent( Line_Entity( [Coords([3,2,1]), Coords([6,5,4])] ) )
    MMEL.El[MMEL.last_ent()].add_tag('foo')
    print(MMEL)

    print("== Adding Triface Entity with coords (0,0,0) (6,5,4) (2,2,2):")
    MMEL.add_ent( Tri_Entity([Coords([0,0,0]), Coords([6,5,4]), Coords([2,2,2])]) )
    print(MMEL)

    print("== Adding Triface Entity with coords (0,0,0) (1,1,1) (2,2,2):")
    MMEL.add_ent( Tri_Entity([Coords([0,0,0]), Coords([1,1,1]), Coords([2,2,2])]) )
    print(MMEL)

    print("== Delete Entity #3:")
    MMEL.del_ent(3)
    print(MMEL)

    print("== Delete Entity #5:")
    MMEL.del_ent(5)
    print(MMEL)

    print("== Get entity # by coords (0,0,0) (8,9,10) [nonexistant]:")
    print(MMEL.find_ents_by_coords(  [ [0,0,0], [8,9,10] ] ))

    print("== Get entity # by coords (2,2,2) [6,7]:")
    print(MMEL.find_ents_by_coords(  [ [2,2,2] ] ))

    print("== Get entity # by coords (1,2,3) (4,5,6) [#1]:")
    print(MMEL.find_ents_by_coords(  [ [1,2,3], [4,5,6] ] ))

    print('-'*40)

    print("# All entity points:")
    print(Entity.allplist)

    print("# All Entities in Entity List:")
    print(MMEL.xed3d_repr())

    print("# All Entities tagged 'foo'.")
    print(MMEL.xed3d_repr(t='foo'))

