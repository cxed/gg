#!/usr/bin/python
# mmout.py - 2014-04-22
# Helper functions and code involved in outputting the memory model
# beyond the running gg interpreter.
# This includes...
#   * creating HTML/SVG graphical output
#   * generic output object with
#     - camera/target views
#     - can segregate geometry between attribute sets
#     - ability to run to2d to convert 3d to 2d
#   * SVG output object 
#     - derived from generic output object
#     - can write SVG tagging attributes correctly
#     - can write encapsulate SVG in HTML
#     - can put the HTML where it needs to be
#   - Proper save file
#   - PostScript Output
import mm
import objectifier

# Blender object. `import mmout` in Blender. Then `mmout.B=bpy` and 
# this module has all the knowledge of the Blender session.
B= None

class MMOut():
    """A base class for any output functionality. Could be SVG, could be
    PostScript, could be TK. It can take the model and view parameters
    and generate a 2d version ready for specialized formatting."""
    def __init__(self):
        """These are the initial defaults."""
        self.outfile= '/tmp/gg.html'
        self.camera= [0, 0, 1]
        self.target= [0, 0, 0]
        self.opacity= True
        self.facelines= False
        self.vlinewidth= 2.0
        self.vrefreshms= 1500
        self.vboxX= 900
        self.vboxY= 900
        self.vtranX= 300
        self.vtranY= -(self.vboxY/2) # This does not get refreshed!
        self.vscaleX= 1
        self.vscaleY= -1
    def get_user_settings_from_var(self,E):
        if 'vw' in E.symtab:
            self.outfile= E.resolve_complex_symbol('vw.fi').val
            self.camera[0]= E.resolve_complex_symbol('vw.ca.x').val
            self.camera[1]= E.resolve_complex_symbol('vw.ca.y').val
            self.camera[2]= E.resolve_complex_symbol('vw.ca.z').val
            self.target[0]= E.resolve_complex_symbol('vw.ta.x').val
            self.target[1]= E.resolve_complex_symbol('vw.ta.y').val
            self.target[2]= E.resolve_complex_symbol('vw.ta.z').val
            self.opacity= E.resolve_complex_symbol('vw.op').val
            self.facelines= E.resolve_complex_symbol('vw.fl').val
            self.vrefreshms= E.resolve_complex_symbol('vw.ms').val
            self.vlinewidth= E.resolve_complex_symbol('vw.lw').val
            self.vboxX= E.resolve_complex_symbol('vw.bx.x').val
            self.vboxY= E.resolve_complex_symbol('vw.bx.y').val
            self.vtranX= E.resolve_complex_symbol('vw.tr.x').val
            self.vtranY= E.resolve_complex_symbol('vw.tr.y').val
            self.vscaleX= E.resolve_complex_symbol('vw.sc.x').val
            self.vscaleY= E.resolve_complex_symbol('vw.sc.y').val
        else:
            self.put_user_settings_in_a_var(E)
    def put_user_settings_in_a_var(self,E):
        fi= objectifier.StackOB_TXT(self.outfile)
        ca= objectifier.StackOB_LST([
            objectifier.StackOB_VAL(self.camera[0]),
            objectifier.StackOB_VAL(self.camera[1]),
            objectifier.StackOB_VAL(self.camera[2]) ])
        ca.names= ['x','y','z']
        ta= objectifier.StackOB_LST([
            objectifier.StackOB_VAL(self.target[0]),
            objectifier.StackOB_VAL(self.target[1]),
            objectifier.StackOB_VAL(self.target[2]) ])
        ta.names= ['x','y','z']
        op= objectifier.StackOB_VAL(self.opacity)
        fl= objectifier.StackOB_VAL(self.facelines)
        lw= objectifier.StackOB_VAL(self.vlinewidth)
        ms= objectifier.StackOB_VAL(self.vrefreshms)
        bx= objectifier.StackOB_LST([
            objectifier.StackOB_VAL(self.vboxX),
            objectifier.StackOB_VAL(self.vboxY) ])
        bx.names= ['x','y']
        tr= objectifier.StackOB_LST([
            objectifier.StackOB_VAL(self.vtranX),
            objectifier.StackOB_VAL(self.vtranY) ])
        tr.names= ['x','y']
        sc= objectifier.StackOB_LST([
            objectifier.StackOB_VAL(self.vscaleX),
            objectifier.StackOB_VAL(self.vscaleY) ])
        sc.names= ['x','y']
        vw= objectifier.StackOB_LST( [fi,ca,ta,op,fl,lw,ms,bx,tr,sc] )
        vw.names= ['fi','ca','ta','op','fl','lw','ms','bx','tr','sc'] 
        E.symtab['vw']= vw
    def point_obs_for_subset_of_ents(self,Es):
        subsets_pobs= list()
        for E in Es:
            for p in E.epts:
                pob= mm.Entity.allplist.get_ob_from_id(p)
                subsets_pobs.append(pob)
        return set(subsets_pobs)
    def convert_to_2d(self,Es):
        o= ''
        o+= "# The points\n"
        for P in self.point_obs_for_subset_of_ents(Es):
            #print(P.xyz_repr())
            o+= P.to2d_repr()
        o+= "# The entities\n"
        for E in Es:
            o+= ' '.join(map(lambda x:str(x),list(E.epts)))
            o+= '\n'
        return o
    def run_to2d(self,to2d_input):
        """Send the text that the `to2d` program wants to see to it and collect
        its output."""
        import subprocess
        to2dcmd= '/usr/local/bin/to2d'
        camera= ','.join([str(x) for x in self.camera])
        target= ','.join([str(x) for x in self.target])
        cmdlist= [to2dcmd,'-c',camera,'-t',target,'-f','-o','-']
        if not self.opacity:
            cmdlist.remove('-o')
        if not self.facelines:
            cmdlist.remove('-f')
        pro= subprocess.Popen(cmdlist,shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        pro.stdin.write(to2d_input)
        return pro.communicate()[0]
    def default(self,MMEL,E):
        """Generic method for normal thing to do for output for this kind of object."""
        self.get_user_settings_from_var(E)
        E_att_sets= MMEL.divide_by_attribute_set()
        print("Generic MMOut")
        for key in E_att_sets:
            #print("key:>%s<" %key)
            #print(self.convert_to_2d(E_att_sets[key]))
            print(self.run_to2d(self.convert_to_2d(E_att_sets[key])))

class MMOutNONE(MMOut):
    def __init__(self):
        pass
    def default(self,MMEL,E):
        print("In MMOutNONE.default()")
        if B is not None:
            print(B.app.version)
        pass
    def run_to2d(self,to2d_input):
        pass
    def convert_to_2d(self,Es):
        pass

class MMOutSVG(MMOut):
    def default(self,MMEL,E):
        """The ordinary output behavior. For MMOutSVG, write an HTML file with
        the correct SVG markup."""
        self.get_user_settings_from_var(E)
        E_att_sets= MMEL.divide_by_attribute_set()
        #print("SVG MMOut")
        o= ''
        for key in E_att_sets:
            sets_3d_points= self.run_to2d(self.convert_to_2d(E_att_sets[key]))
            # Not needed now, but if the output of to2d changes....
            #sets_3d_svg= self.to2d_output_to_SVG(sets_3d_points)
            sets_3d_svg= sets_3d_points
            o+= self.wrapSVGatts(key,sets_3d_svg)
        o= self.wrap_in_html(o)
        self.publish_html(o)
    def wrapSVGatts(self,attkey,svglines):
        """Put the '<g ....> <line ... /> </g>' tags around SVG lines to supply
        correct display attributes."""
        if not attkey: 
            return svglines
        svgattribs= self.attkey_to_SVG_attribs(attkey)
        o= ('<g %s>\n' % svgattribs) 
        o+= svglines 
        o+= ('</g> <!-- %s -->\n' % svgattribs)
        return o
    def attkey_to_SVG_attribs(self,k):
        """Convert attribute keys from something like 'Cred@W2.5@S4,4' to
        'stroke="red" stroke-width="2.5" stroke-dasharray="4,4"'
        Currently counts on the value being literally placed in the SVG. It
        would be easy enough to add small translations so that ''C@centerline''
        would translate into 'stroke-dasharray="5,5,20,5"' """
        atts= k.split('@')
        o= ''
        acodes= {'C':'stroke','W':'stroke-width','S':'stroke-dasharray','O':'stroke-opacity'}
        for a in atts:
            if a[0] in acodes:
                o+= '%s="%s" ' % (acodes[a[0]],a[1:])
#           elif a[0] == 'S': # Maybe do something special like this.
#               o+= 'stroke-dasharray="%" ' % a[1:]
        return o
    def wrap_in_html(self,svgofmodel):
        """Here's an ugly mess which just gets the SVG into a useful HTML document.
        This could be heavily embellished and also cleaned up."""
        html= '''<html>\n%s\n%s\n%s\n</g></g></g></svg></body></html>\n'''
        svgbody= '''<body onload="javascript:setTimeout(&quot;location.reload(true);&quot;,%d);">\n''' % self.vrefreshms
        svgbody += "<h4>GeoGad</h4>"
        svghead= '<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" width="%dpx" height="%dpx">\n'
        svghead= svghead % (self.vboxX,self.vboxY)
        svghead+= '<rect x="1" y="1" width="%d" height="%d" fill="none" stroke="blue" stroke-width="4"/>\n'% (self.vboxX,self.vboxY)
        svghead+= '<g fill="none" stroke="black" stroke-width="%0.2f">\n' % self.vlinewidth
        svghead+= '<g transform="scale(%0.2f,%0.2f)">\n' % (self.vscaleX,self.vscaleY)
        svghead+= '<g transform="translate(%0.2f,%0.2f)">\n' % (self.vtranX,self.vtranY)
        return html % (svgbody,svghead,svgofmodel)
    def publish_html(self, readyhtml):
        """With the correct view's HTML ready, this function actually writes it to the place
        the browser is hopefully looking for it. A good place to add error
        checking (disk full?, etc)."""
        with open(self.outfile,'w') as f_out:
            f_out.writelines(readyhtml)

def mmdump(MMEL):
    """Dump the memory model into a string of input suitable for `to2d`."""
    mm_out= "# == All Entity Points ==\n"
    mm_out+= mm.Entity.allplist.__repr__()
    mm_out+= "# == All Entities In Entity List ==\n"
    mm_out+= MMEL.xed3d_repr()
    return mm_out

if __name__ == "__main__":
    with SVGsettings('stroke-width="1.5"'):
        with SVGsettings('stroke="red"'):
            print('<line x1="3" y1="0" x2="25" y2="44"/>')
