# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 11:50:08 2018

@author: DonB
"""
from __future__ import division
import math as m

def ic_brandt(IC, xloc, yloc, Mp):
    num_bolts = len(xloc)
    
    deltamax = 0.34
 
    ICx = IC[0]
    ICy = IC[1]
    xIC = []
    yIC = []
    di = []
    deltai = []
    ri = []
    
    fx = []
    fy = []
    moment = []
    
    for x in xloc:
        xICtemp = x - ICx
        xIC.append(xICtemp)
        
    for y in yloc:
        yICtemp = y - ICy
        yIC.append(yICtemp)
    
    i=0
    for i in range(num_bolts):
        ditemp = m.sqrt((xIC[i]*xIC[i])+(yIC[i]*yIC[i]))
        di.append(ditemp)
    
    dmax = max(di)
    
    i=0
    for i in range(num_bolts):
        deltaitemp = (di[i]/dmax)*deltamax
        deltai.append(deltaitemp)
        
    i=0
    for i in range(num_bolts):
        ritemp = m.pow(1-m.pow(m.e,-10.0*deltai[i]),0.55)
        ri.append(ritemp)
        
    i=0
    for i in range(num_bolts):    
        fxtemp = -1*(yIC[i]*ri[i])/di[i]
        fx.append(fxtemp)
        
    i=0
    for i in range(num_bolts):     
        fytemp = (xIC[i]*ri[i])/di[i]
        fy.append(fytemp)
        
    i=0
    for i in range(num_bolts):    
        momenttemp = ri[i]*di[i]
        moment.append(momenttemp)
    
    Mi = sum(moment)
    Rult = -1*Mp/Mi
    
    Rx = sum(fx) * Rult
    Ry = sum(fy) * Rult
    
    
    table = [xIC, yIC, di, deltai, ri, moment, fx, fy]
    
    return Rx, Ry, Mi, table
    
def brandt(xloc, yloc, P_xloc, P_yloc, P_angle):
    # Bolt Group Instantaneous Center using method by G. Donald Brandt
    # Rapid Determiniation of Ultimate Strength Of Eccentrically Loaded Bolt Groups
    # AISC Journal 1982 2nd Quarter
    
    detailed_output = []
    
    num_bolts = len(xloc)
    
    n = num_bolts
    
    detailed_output.append(num_bolts)
    
    #Bolt Group Centroid
    if len(xloc)<3:
        anchor_x_bar = (xloc[0]+xloc[1])/2.00
        anchor_y_bar = (yloc[0]+yloc[1])/2.00
    
    else:
        j=0
        x_tot=0
        y_tot=0
        
        for i in xloc:
            x_tot = x_tot+xloc[j]
            y_tot = y_tot+yloc[j]    
            j+=1
        
        anchor_x_bar = x_tot/len(xloc)
        anchor_y_bar = y_tot/len(yloc)
     
    cg_anchors = [anchor_x_bar, anchor_y_bar]
    detailed_output.append(cg_anchors)
    
    # J - Polar Moment of Inertial of Bolt Group
    # sum(x^2+y^2)
    sum_x_square = 0
    sum_y_square = 0
    
    i=0
    for i in range(num_bolts):
        sum_x_square = sum_x_square + (xloc[i]-anchor_x_bar)**2
        sum_y_square = sum_y_square + (yloc[i]-anchor_y_bar)**2
    
    J = sum_x_square + sum_y_square
    detailed_output.append(['J',J])
    
    Px = -1*m.cos(m.radians(P_angle))
    Py = -1*m.sin(m.radians(P_angle))
    
    detailed_output.append([Px,Py])
    
    Mo = (-1*Px*(P_yloc-anchor_y_bar))+(Py*(P_xloc-anchor_x_bar))
    
    detailed_output.append(Mo)
    
    ax = (-1*Py*J) / (n * Mo)
    ay = (Px*J) / (n*Mo)
    
    detailed_output.append([ax,ay])
    
    Mp = (-1*Px*(P_yloc-anchor_y_bar-ay))+(Py*(P_xloc-anchor_x_bar-ax))
    
    detailed_output.append(Mp)
    
    IC_initial = [anchor_x_bar+ax,anchor_y_bar+ay]
    
    Rx, Ry, Mi, table = ic_brandt(IC_initial,xloc,yloc, Mp)
    
    detailed_output.append([Rx, Ry, Mi, table,"First IC pass"])
    
    fxx = Px + Rx
    fyy = Py + Ry
    F = m.sqrt(fxx*fxx+fyy*fyy)
    
    detailed_output.append([fxx,fyy,F,"F"])
    
    ax_new = (-1*fyy*J)/(n*Mo)
    ay_new = (fxx*J) / (n*Mo)
    
    detailed_output.append(["ax",ax_new,"ay",ay_new])
    
    IC_new = IC_initial  
    
    count = 0
    iterations = 0
    while count<1000:
        
        IC_new = [IC_new[0]+ax_new,IC_new[1]+ay_new]
        Mp_new = (-1*Px*(P_yloc-IC_new[1]))+(Py*(P_xloc-IC_new[0]))
        
        Rx, Ry, Mi, table = ic_brandt(IC_new,xloc,yloc, Mp_new)
        
        fxx = Px + Rx
        fyy = Py + Ry
        F = m.sqrt(fxx*fxx+fyy*fyy)
        
        ax_new = (-1*fyy*J)/(n*Mo)
        ay_new = (fxx*J) / (n*Mo)
        
        if F <= 0.00001:
            iterations = count
            count = 1000          
            solution = 'yes'
        else:        
            count +=1
            solution = 'no'
    
    detailed_output.append([fxx,fyy,F])        
    detailed_output.append(IC_new)
    detailed_output.append([solution,iterations,count])
    
    detailed_output.append([Rx, Ry, Mi, table])
    
    
    
    Cu = abs(Mi/Mp_new)
    
    detailed_output.append([Mi,Mp_new,Cu])
    
    return detailed_output, IC_new, Cu

# Brandt's Method Testing Zone
x_b = [-1.5,-1.5,-1.5,-1.5,1.5,1.5,1.5,1.5]
y_b = [-4.5,-1.5,1.5,4.5,4.5,1.5,-1.5,-4.5]
P_xloc = 24
P_yloc = 0
P_angle = 60

brandt = brandt(x_b, y_b, P_xloc, P_yloc, P_angle) 
    
        