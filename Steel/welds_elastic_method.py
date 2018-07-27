# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import division
import math

def center_of_two_points(p1=[0,0],p2=[1,1]):
    x_center = (p1[0]+p2[0])/2.0
    y_center = (p1[1]+p2[1])/2.0
    
    return [x_center, y_center]
    
def length_between_two_points(p1=[0,0],p2=[1,1]):
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])

    length = (dx**2 + dy**2)**0.5

    return length

def parrallel_axis_theorem(momentofinertia=1, area=1, distancetoparallelaxis=1):
    '''
    Parralel axis theorem: I' = Ilocal + A*d^2
    '''
    return momentofinertia + (area*distancetoparallelaxis*distancetoparallelaxis)

def centroid_by_areas(areas=[0],areacenters=[[0,0]],referencepoint=[0,0]):
    '''
    computes the centroid x,y distances from a reference point
    and returns the global x,y coordinates relative to (0,0)
    
    length of areas and areacenters must be equal
    '''
    if len(areas) != len(areacenters):
        return 'Number of Areas needs to match the number of Area Centers'
    else:
        sumA = sum(areas)
        sumAx = 0
        sumAy = 0
        for area, areacenter in zip(areas, areacenters):
            cix = areacenter[0] - referencepoint[0]
            ciy = areacenter[1] - referencepoint[1]
            
            sumAx = sumAx + (area*cix)
            sumAy = sumAy + (area*ciy)
        
        Cx = sumAx/sumA
        Cy = sumAy/sumA
        
        global_center_x = Cx + referencepoint[0]
        global_center_y = Cy + referencepoint[1]
        
        return [global_center_x, global_center_y]
    
    
class weld_segment:
    def __init__(self, startcoordinates=[0,0], endcoordinates=[1,1]):
    
        self.start = startcoordinates
        
        self.end = endcoordinates
        
        self.m = self.end[0] - self.start[0]
        self.n = self.end[1] - self.start[1]
        
        self.center = center_of_two_points(self.start, self.end)
        
        self.length = length_between_two_points(self.start, self.end)
        self.area = self.length
        
        self.Ixo = (self.length*self.n*self.n)/12.0
        
        self.Iyo = (self.length*self.m*self.m)/12.0
        
        self.info_text = 'Weld @ i: ({0},{1}) j: ({2},{3}) - A = {4:.3f} Ixo = {5:.3f} Iyo = {6:.3f} -- Center: ({7:.3f},{8:.3f})'.format(self.start[0],self.start[1],self.end[0],self.end[1],self.area,self.Ixo,self.Iyo,self.center[0], self.center[1])
        self.global_info_text = ''
        
        self.x_coords = [self.start[0], self.end[0]]
        self.y_coords = [self.start[1], self.end[1]]
    
    def global_moments_of_inertia(self, referencepoint=[0,0]):
        
        Cx = self.center[0] - referencepoint[0]
        Cy = self.center[1] - referencepoint[1]
        
        self.Ix = parrallel_axis_theorem(self.Ixo, self.area, Cy)
        self.Iy = parrallel_axis_theorem(self.Iyo, self.area, Cx)
        
        self.global_info_text = ' -- Cx = {0:.3f}  Cy = {1:.3f} -- Ix = {2:.3f}  Iy = {3:.3f}'.format(Cx, Cy, self.Ix, self.Iy)
        
        return [self.Ix, self.Iy]

class elastic_weld_group:
    def __init__(self, weld_segments=[weld_segment([0,0],[0,1])]):
        
        self.log = '--Elastic Weld Group Analysis--\nSegment Areas and Centroids:\n'
        
        self.gui_output_labels = []
        self.gui_output_equations = []
        self.gui_output_values = []
        
        # build lists of areas and center of areas for each weld segment to
        # pass into the centroid_by_areas function
        
        areas = [weld.area for weld in weld_segments]
        areacenters = [weld.center for weld in weld_segments]
        

        for area, areacenter in zip(areas,areacenters):
            self.log = self.log + 'Segment Area:{0:.3f} Segment Centroid: ({1:.3f},{2:.3f})\n'.format(area,areacenter[0],areacenter[1])
        
        # Determine the centroid coordinates for the weld group
        self.group_center = centroid_by_areas(areas, areacenters)
        
        self.gui_output_labels.extend(['Group Centroid x = ', 'Group Centroid y = '])
        self.gui_output_equations.extend(['(As1*cx1+...+Asi*cxi) / (As1+...+Asi) = ', '(As1*cy1+...+Asi*cyi) / (As1+...+Asi) = '])
        self.gui_output_values.extend([self.group_center[0],self.group_center[1]])
        
        self.log = self.log + '\nWeld Group Properties\nWeld Group Centroid: ({0:.3f},{1:.3f})\n'.format(self.group_center[0],self.group_center[1])
        
        self.Area = sum(areas)
        
        self.gui_output_labels.extend(['Area = '])
        self.gui_output_equations.extend(['(As1+...+Asi) = '])
        self.gui_output_values.extend([self.Area])
        
        self.log = self.log + '\nGroup Properties:\nArea = sum of lengths = {0:.3f}\n'.format(self.Area)

        # Determine Ix and Iy about the weld groupd centroidal axis
        self.Ix = 0
        self.Iy = 0
        
        self.gui_output_labels.extend(['Ix, x-axis moment of inertia about group center = ','Iy, y-axis moment of inertia about group center = '])
        
        self.log = self.log + '\nPer Segment Moment of Inertias:\n'
        for weld in weld_segments:
            
            Ixsegment = weld.global_moments_of_inertia(self.group_center)[0]
            Iysegment = weld.global_moments_of_inertia(self.group_center)[1]
            self.Ix = self.Ix + Ixsegment
            self.Iy = self.Iy + Iysegment
            
            self.log = self.log + 'Ix,segment = {0:.3f}\nIy,segment = {1:.3f}\n'.format(Ixsegment, Iysegment)
        
        self.log = self.log + '\nWeld Group Moment of Inertias:\nIx = sum of segment Ix = {0:.3f}\nIy = sum of segment Iy = {1:.3f}\n'.format(self.Ix, self.Iy)
        
        self.gui_output_equations.extend(['sum of segment Ix = ','sum of segment Iy = '])
        self.gui_output_values.extend([self.Ix, self.Iy])
        
        self.Ip = self.Ix + self.Iy
        
        self.gui_output_labels.extend(['Ip, polar moment of Inertia = '])
        self.gui_output_equations.extend(['Ix + Iy = '])
        self.gui_output_values.extend([self.Ip])
        
        self.log = self.log + 'Polar Moment of Inertia, Ip = Ix + Iy = {0:.3f}\n'.format(self.Ip)
        
        max_x = max(max([weld.start[0] for weld in weld_segments]), max([weld.end[0] for weld in weld_segments]))
        min_x = min(min([weld.start[0] for weld in weld_segments]), min([weld.end[0] for weld in weld_segments]))
        
        self.Cx_right = abs(max_x - self.group_center[0])
        self.Cx_left = abs(min_x - self.group_center[0])
        
        self.gui_output_labels.extend(['Cx,left = ','Cx,right = '])
        self.gui_output_equations.extend(['Min X coord - Centroid X = ','Max X coord - Centroid X = '])
        self.gui_output_values.extend([self.Cx_left, self.Cx_right])
        
        self.log = self.log + '\nLeft most Distance to Centroid, Cx,left = {0:.3f}\nRight most Distance to Centroid, Cx,right = {1:.3f}\n'.format(self.Cx_left, self.Cx_right)
        
        max_y = max(max([weld.start[1] for weld in weld_segments]), max([weld.end[1] for weld in weld_segments]))
        min_y = min(min([weld.start[1] for weld in weld_segments]), min([weld.end[1] for weld in weld_segments]))
        
        self.Cy_top = abs(max_y - self.group_center[1])
        self.Cy_bottom = abs(min_y - self.group_center[1])
        
        self.gui_output_labels.extend(['Cy,top = ','Cy,bottom = '])
        self.gui_output_equations.extend(['Max Y coord - Centroid Y = ','Min Y coord - Centroid Y = '])
        self.gui_output_values.extend([self.Cy_top, self.Cy_bottom])
        
        self.log = self.log + 'Top most Distance to Centroid, Cy,top = {0:.3f}\nBottom most Distance to Centroid, Cy,bottom = {1:.3f}\n'.format(self.Cy_top, self.Cy_bottom)        
        
        self.Sx_top = self.Ix/self.Cy_top
        self.log = self.log + '\nElastic Section Moduli:\nSx,top = Ix/Cy,top = {0:.3f}\n'.format(self.Sx_top)
        self.Sx_bottom = self.Ix/self.Cy_bottom
        self.log = self.log + 'Sx,bottom = Ix/Cy,bottom = {0:.3f}\n'.format(self.Sx_bottom)
        self.Sy_left = self.Iy/self.Cx_left
        self.log = self.log + 'Sy,left = Iy/Cy,left = {0:.3f}\n'.format(self.Sy_left)
        self.Sy_right = self.Iy/self.Cx_right
        self.log = self.log + 'Sy,right = Iy/Cy,right = {0:.3f}\n'.format(self.Sy_right)
        
        self.gui_output_labels.extend(['Sx,top = ','Sx,bottom = ', 'Sy,left = ','Sy,right = '])
        self.gui_output_equations.extend(['Ix/Cy,top = ','Ix/Cy,bottom = ','Iy/Cx,left = ','Iy/Cx,right = '])
        self.gui_output_values.extend([self.Sx_top, self.Sx_bottom,self.Sy_left,self.Sy_right])
                  
    
    def force_analysis(self, Fz, Fx, Fy, Mx, My, Mz):
        self.log = self.log + '\n\n---Elastic Force Analysis of Weld Group---\n**All Loads Assumed to be applied at the weld group centroid.**\n'
        self.log = self.log + 'Fz,Axial = {0:.3f}\nFx,Shear X = {1:.3f}\nFy,Shear Y = {2:.3f}\nMx,Moment about x-axis = {3:.3f}\nMy,Moment about y-axis = {4:.3f}\nMz,Torsion aboiut the z-axis = {5:.3f}\n'.format(Fz, Fx, Fy, Mx, My, Mz)
        #Component Forces
        fz = Fz/self.Area
        self.log = self.log + '\n--Component Forces--\nfz = Fz/Area = {0:.3f}\n'.format(fz)
        fx = Fx/self.Area
        self.log = self.log + 'fx = Fx/Area = {0:.3f}\n'.format(fx)
        fy = Fy/self.Area
        self.log = self.log + 'fy = Fy/Area = {0:.3f}\n'.format(fy)
        mx = max(Mx/self.Sx_top, Mx/self.Sx_bottom)
        self.log = self.log + 'mx = max[Mx/Sx,top and Mx/Sx,bottom] = {0:.3f}\n'.format(mx)
        my = max(My/self.Sy_left, My/self.Sy_right)
        self.log = self.log + 'my = max[My/Sy,left and My/Sy,right] = {0:.3f}\n'.format(my)
        mzy = max((Mz*self.Cx_left)/self.Ip, (Mz*self.Cx_right)/self.Ip)
        self.log = self.log + 'mzy = max[Mz*Cx,left/Ip and Mz*Cx,right/Ip] = {0:.3f}\n'.format(mzy)
        mzx = max((Mz*self.Cy_bottom)/self.Ip,(Mz*self.Cy_top)/self.Ip)
        self.log = self.log + 'mzx = max[Mz*Cy,top/Ip and Mz*Cy,bottom/Ip] = {0:.3f}\n'.format(mzx)
        
        self.component_forces = [fz,fx,fy,mx,my,mzy,mzx]
        self.component_forces_key = ['fz', 'fx', 'fy', 'mx', 'my', 'mzy', 'mzx']
        self.component_forces_eqs = ['Fz/Area','Fx/Area','Fy/Area','max[Mx/Sx,top and Mx/Sx,bottom]','max[My/Sy,left and My/Sy,right]','max[Mz*Cx,left/Ip and Mz*Cx,right/Ip]','max[Mz*Cy,top/Ip and Mz*Cy,bottom/Ip]']
        
        #Resultant Force
        self.resultant = math.sqrt(((fz+mx+my)*(fz+mx+my)) + ((fx+mzx)*(fx+mzx)) + ((fy+mzy)*(fy+mzy)))
        self.log = self.log + '\nResulatant force per unit length = [(fz+mx+my)^2 + (fx+mzx)^2 + (fy+mzy)^2]^(1/2) = {0:.3f}'.format(self.resultant)
        
        self.component_forces.extend([self.resultant])
        self.component_forces_key.extend(['Resultant'])
        self.component_forces_eqs.extend(['[(fz+mx+my)^2 + (fx+mzx)^2 + (fy+mzy)^2]^(1/2)'])
        
        return self.resultant
    
    def aisc_weld_check(self, resultant, Fexx, Fy_base1, Fu_base1, base_thickness1, Fy_base2, Fu_base2, base_thickness2, asd=0):
        
        base_thickness = min(base_thickness1,base_thickness2)
        
        self.aisclog = '---Weld Design---\n'
        if asd==0:        
            rn_weld = resultant/0.75
            rn_base_yield = resultant
            rn_base_rupture = resultant/0.75
            self.aisclog = self.aisclog + 'Ru,Ultimate Resultant Shear: {0:.3f}\n'.format(resultant)
            self.aisclog = self.aisclog + 'Fexx = {0:.3f}\nFy,base1 = {1:.3f}\nFu,base1 = {2:.3f}\nt,base1 material thickness = {3:.3f}\nFy,base2 = {4:.3f}\nFu,base2 = {5:.3f}\nt,base2 material thickness = {6:.3f}\n\n'.format(Fexx, Fy_base1, Fu_base1, base_thickness1, Fy_base2, Fu_base2, base_thickness2)
            self.aisclog = self.aisclog + 'Rn,weld/phi = Ru/0.75 = {0:.3f}\nRn,base yield/phi = Ru/1.0 = {1:.3f}\nRn,base rupture/phi = Ru/0.75 = {2:.3f}\n\n'.format(rn_weld,rn_base_yield,rn_base_rupture)
        else:
            rn_weld = resultant*2.0
            rn_base_yield = resultant*1.5
            rn_base_rupture = resultant*2.0
            self.aisclog = self.aisclog + 'Rn,Nominal Resultant Shear: {0:.3f}\n'.format(resultant)
            self.aisclog = self.aisclog + 'Fexx = {0:.3f}\nFy,base1 = {1:.3f}\nFu,base1 = {2:.3f}\nt,base1 material thickness = {3:.3f}\nFy,base2 = {4:.3f}\nFu,base2 = {5:.3f}\nt,base2 material thickness = {6:.3f}\n\n'.format(Fexx, Fy_base1, Fu_base1, base_thickness1, Fy_base2, Fu_base2, base_thickness2)
            self.aisclog = self.aisclog + 'Rn,weld*omega = Ru*2.0 = {0:.3f}\nRn,base yield*omega = Ru*1.5 = {1:.3f}\nRn,base rupture*omega = Ru*2.0 = {2:.3f}\n\n'.format(rn_weld,rn_base_yield,rn_base_rupture)
            
        Aweld = rn_weld/(0.6*Fexx)
        self.aisclog = self.aisclog + 'Required Effective Throat = Rn,weld / 0.6*Fexx [AISC Table J2.5] = {0:.3f}\n\n'.format(Aweld)
        
        fillet_weld_16th = math.ceil(rn_weld / ((math.sqrt(2)/2.0)*(1/16.0)*0.6*Fexx))
        fillet_weld = fillet_weld_16th/16.0
        self.aisclog = self.aisclog + 'As a Fillet Weld: {0:.1f} / 16" per loading\n\n'.format(fillet_weld_16th)
        
        # Minimum Fillet Weld - AISC Table J2.4
        if base_thickness > 0.75:          
            min_fillet_weld_16th = 5
            min_fillet_weld = 5/16.0
        elif 0.5 < base_thickness <= 0.75:
            min_fillet_weld_16th = 4
            min_fillet_weld = 1/4.0
        elif 0.25 < base_thickness <= 0.5:
            min_fillet_weld_16th = 3
            min_fillet_weld = 3/16.0
        else:
            min_fillet_weld_16th = 2
            min_fillet_weld = 2/16.0  
        self.aisclog = self.aisclog + 'Minimum Fillet Weld per AISC Table J2.4: {0:.1f}/16" or {1:.3f}"\n'.format(min_fillet_weld_16th,min_fillet_weld)
        
        # Max Fillet Weld - AISC J2b        
        if base_thickness < 0.25:
            max_fillet_weld_16th = 16.0*base_thickness
            max_fillet_weld = base_thickness
        else:           
            max_fillet_weld = base_thickness - (1/16.0)
            max_fillet_weld_16th = 16.0*max_fillet_weld
        self.aisclog = self.aisclog + 'Maximum Fillet Weld per AISC J2b: {0:.1f}/16" or {1:.3f}"\n\n'.format(max_fillet_weld_16th,max_fillet_weld)
        
        if fillet_weld < max_fillet_weld and fillet_weld < min_fillet_weld:
            self.aisclog = self.aisclog + 'Required Fillet < AISC Min - Use {0:.1f}/16" or {1:.3f}"\n\n'.format(min_fillet_weld_16th,min_fillet_weld)
        
        elif fillet_weld < max_fillet_weld and fillet_weld >= min_fillet_weld:
            self.aisclog = self.aisclog + 'Required Fillet > AISC Min - Use {0:.1f}/16" or {1:.3f}"\n\n'.format(fillet_weld_16th,fillet_weld)
        
        else:
            self.aisclog = self.aisclog + 'Required Fillet > AISC Maximum - **NG**\nIf Possible Increase Overall Weld Group Geometry\n\n'
            
        # Check if Base Material Ok
        Ag1 = base_thickness
        Anv1 = Ag1
        self.aisclog = self.aisclog + '--Base Material Checks--\nAg1 = Anv1 = t,base1*1.0 = {0:.3f}\n\n'.format(Ag1)
        
        # AISC J4.2 - Shear Yielding and Shear Rupture
        shear_yield_base1 = 0.6*Fy_base1*Ag1 # AISC eq J4-3
        self.aisclog = self.aisclog + 'AISC J4.2 - Shear Yielding of Base Material:\nRn1 = 0.60*Fy,base1*Ag1 (J4-3) = {0:.3f}\n'.format(shear_yield_base1)
        if shear_yield_base1/rn_base_yield > 1.0:
            shear_yield_status1 = 'OK'
            self.aisclog = self.aisclog + 'Rn1 > Rn,base yield: OK\n\n'
        else:
            shear_yield_status1 = '**NG**'
            self.aisclog = self.aisclog + 'Rn1 < Rn,base yield: **NG**\n\n'
        
        shear_rupture_base1 = 0.6*Fu_base1*Anv1 # AISC eq J4-4
        self.aisclog = self.aisclog + 'AISC J4.2 - Shear Rupture of Base Material:\nRn1 = 0.60*Fu,base1*Anv1 (J4-4) = {0:.3f}\n'.format(shear_rupture_base1)

        if shear_rupture_base1/rn_base_rupture > 1.0:
            shear_rupture_status1 = 'OK'
            self.aisclog = self.aisclog + 'Rn1 > Rn,base rupture: OK\n'
        else:
            shear_rupture_status1 = '**NG**'
            self.aisclog = self.aisclog + 'Rn1 < Rn,base rupture: **NG**\n'
        
        Ag2 = base_thickness2
        Anv2 = Ag2
        self.aisclog = self.aisclog + '\nAg2 = Anv2 = t,base2*1.0 = {0:.3f}\n\n'.format(Ag2)
        
        # AISC J4.2 - Shear Yielding and Shear Rupture
        shear_yield_base2 = 0.6*Fy_base2*Ag2 # AISC eq J4-3
        self.aisclog = self.aisclog + 'AISC J4.2 - Shear Yielding of Base Material:\nRn2 = 0.60*Fy,base2*Ag2 (J4-3) = {0:.3f}\n'.format(shear_yield_base2)
        if shear_yield_base2/rn_base_yield > 1.0:
            shear_yield_status2 = 'OK'
            self.aisclog = self.aisclog + 'Rn2 > Rn,base yield: OK\n\n'
        else:
            shear_yield_status2 = '**NG**'
            self.aisclog = self.aisclog + 'Rn2 < Rn,base yield: **NG**\n\n'
        
        shear_rupture_base2 = 0.6*Fu_base2*Anv2 # AISC eq J4-4
        self.aisclog = self.aisclog + 'AISC J4.2 - Shear Rupture of Base Material:\nRn2 = 0.60*Fu,base2*Anv2 (J4-4) = {0:.3f}\n'.format(shear_rupture_base2)

        if shear_rupture_base2/rn_base_rupture > 1.0:
            shear_rupture_status2 = 'OK'
            self.aisclog = self.aisclog + 'Rn2 > Rn,base rupture: OK\n'
        else:
            shear_rupture_status2 = '**NG**'
            self.aisclog = self.aisclog + 'Rn2 < Rn,base rupture: **NG**\n'
        
        
# Circle Helper
#segments = []
#r = 3
#for a in range(0,360):
#    x = r*math.sin(math.radians(a))
#    y = r*math.cos(math.radians(a))
#    x1 = r*math.sin(math.radians(a+1))
#    y1 = r*math.cos(math.radians(a+1))
#    
#    segments.append(weld_segment([x,y],[x1,y1]))

segments = [weld_segment([2,2],[2,8]),weld_segment([4,2],[4,8])]

weld_group = elastic_weld_group(segments)

#Loads:
Fz = 0
Fx = 5000
Fy = 5000
Mx = 50000
My = 0
Mz = 0

resultant = weld_group.force_analysis(Fz,Fx,Fy,Mx,My,Mz)

weld_group.aisc_weld_check(resultant,70000,36000,58000,0.5,36000,58000,0.5,0)

Ix = weld_group.Ix
Iy = weld_group.Iy
Ip = weld_group.Ip
center = weld_group.group_center

log = weld_group.log


    