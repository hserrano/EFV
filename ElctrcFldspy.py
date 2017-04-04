#!/usr/bin/python
#Copyright 2017 Hector Serrano
#This file is part of Arrow Plot and Flux Lines
#Arrow Plot and Flux Lines is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#Original version was writen in Java by Michael J. McGuffin, November 2004, University of Toronto
#http://profs.etsmtl.ca/mmcguffin/research/electrostatic/applet1/main.html
#
#Consulting performed with Matt Ruby at Agnes Scott

from Tkinter import *
import math

class ElectricCharge(object):
    def __init__(self,x,y,q):
        # pixel coordinate x y
        self.x = x 
        self.y = y
        # charge, positive or negative
        self.q = q

class ForceVector(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

class App:
    def __init__(self,master):
        self.userReadMe = Label(master,text="Click for positive charge. (Ctrl or Shift) + Click for a negative charge.")
        self.userReadMe.pack(side=TOP,anchor="w");
        
        self.frame = Frame(master);
        self.frame.pack();
        
        # in pixesl
        self.chargeRadius = 8;
        self.arrowPlotSpacing = 2 * self.chargeRadius;
        self.fluxLineSpacing = 2 * self.arrowPlotSpacing;
        self.fluxLinesPerCharge = 8;

        self.drawArrowPlot = True;
        self.drawFluxLines = True;
        self.isDragging = False;
        self.indexOfChargeBeingDragged = -1;
        self.previousX = 0;
        self.previousY = 0;

        #array of ElectricCharge objects
        self.ListElectricCharge = {};

        #array of Color Spectrum
        self.Spectrum = [];
        self.numColors = 16;
        self.bgcolor = '#000000';
        self.fg1color = {'r': 0.0,'g':1.0,'b':1.0};
        self.fg2color = {'r': 1.0,'g':0.0,'b':0.0};
      
        #Dimensions of each canvas
        self.width = 600;
        self.height =600;

        self.painted = False;
        self.isBackbufferDirty = True;

        #create color spectrum
        #HS verify color spectrum is being set
        #for x in xrange(self.numColors):
        #    self.u =float(x/float((self.numColors-1.0)));
        #    self.red = round((1-self.u) * self.fg1color['r'] + self.u * self.fg2color['r']);
        #    self.green = round((1-self.u) * self.fg1color['g'] + self.u * self.fg2color['g']);
        #    self.blue = round((1-self.u) * self.fg1color['b'] + self.u * self.fg2color['b']);
        #    self.rgb = self.rgbtohex(self.red,self.green,self.blue);
        #    print "red",self.red,"green",self.green,"blue",self.blue;
        #    self.Spectrum.append(self.rgb);
        self.Spectrum.append("dodger blue");
        self.Spectrum.append("deep sky blue");
        self.Spectrum.append("dark turquoise");
        self.Spectrum.append("medium turquoise");
        
        self.Spectrum.append("turquoise");
        self.Spectrum.append("aquamarine");
        self.Spectrum.append("light salmon");
        self.Spectrum.append("salmon");
        
        self.Spectrum.append("coral");
        self.Spectrum.append("tomato");
        self.Spectrum.append("orange red");
        self.Spectrum.append("red");
        
        self.Spectrum.append("red");
        self.Spectrum.append("red2");
        self.Spectrum.append("red3");
        self.Spectrum.append("red4");
            
        #a 2d array of flags used to map the screen
        for x in xrange(self.width/self.fluxLineSpacing+1):
            for y in xrange(self.height/self.fluxLineSpacing+1):
                self.map = {(x,y): False};

        #Create Canvas: ArrowPlot Left Canvas, FluxLines Right Canvas
        self.ArrowPlot = Canvas(self.frame, width=self.width, height=self.height, background= self.bgcolor, cursor='crosshair');
        self.FluxLines = Canvas(self.frame, width=self.width, height=self.height, background=self.bgcolor, cursor='crosshair');
        self.ArrowPlot.pack(side = LEFT,fill = 'both',expand=True);
        self.FluxLines.pack(side = RIGHT,fill = 'both',expand=True);
        
        #Bind mouse events
        self.ArrowPlot.bind("<ButtonPress-1>",self.onbuttonpress);
        self.FluxLines.bind("<ButtonPress-1>",self.onbuttonpress);

        #Return color as #rrggbb for the given color values.
    #def rgbtohex(self, r, g, b):
    #    return '#%02x%02x%02x' % (r, g, b)

        #returns electric force field at the given pixel
    def computeForce(self,X,Y):
        x=float(X);
        y=float(Y);
        v = ForceVector(0.0,0.0);
        for z in self.ListElectricCharge.itervalues():
            dx = (x - z.x)/float(self.arrowPlotSpacing);
            dy = (y - z.y)/float(self.arrowPlotSpacing);
            r2 = dx*dx + dy*dy;
            if ( r2 == 0):
                continue
            r = float(math.sqrt(r2));
            self.forceMagnitude = z.q / r2;
            v.x += self.forceMagnitude * dx/r;
            v.y += self.forceMagnitude * dy/r;
        return v;

    def mapForceMagnitudeToColor(self,forceMagnitude):
        # Consider radius r in units of arrowPlotSpacing,
        # and force f == 1/r^2.
        # If we map f linearly to colour, the high-intensity
        # colour are concentrated close to the centre of the charges,
        # and colour falls off very quickly as radius increases.
        # So, we instead map log10( force ) linearly to colour.
        # Maybe we would like r=0.3, i.e. f == 1/r^2 ~ 10,
        # to map to the max colour,
        # and r=4, i.e. f == 1/r^2 ~ 0.1,
        # to map to the min colour.
        # In other words, maybe we would like log10( 10 ) == 1
        # to map to the max colour,
        # and log10( 0.1 ) == -1
        # to map to the min colour.
        # This would correspond to
        #    ( math.log10( forceMagnitude ) + 1 )/2 * numColors
               
        colorIndex = int(((math.log(forceMagnitude)/math.log(10.0) + 3)/3)*self.numColors);

        # clamp the results
        if colorIndex < 0: colorIndex = 0;
        elif colorIndex >= self.numColors: colorIndex = self.numColors - 1;
        return self.Spectrum[colorIndex];
    
    #(x1,y1) is the origin of the arrow; (x2,y2) is the tip of the arrow
    def drawArrow(self,x1,y1,x2,y2,color):
        dx = float(x2-x1);
        dy = float(y2-y1);
        # length of arrow head over length of arrow stem
        
        f = float(1/3.0);
        # half-width of arrow head over length of arrow stem
        f2 = float(1/6.0);
        x3 = float(x2 - f*dx - f2*dy);
        y3 = float(y2 - f*dy + f2*dx);
        x4 = float(x2 - f*dx + f2*dy);
        y4 = float(y2 - f*dy - f2*dx);
        
        self.ArrowPlot.create_line(round(x1), round(y1), round(x2), round(y2),fill =color);
        self.ArrowPlot.create_line(round(x3), round(y3), round(x2), round(y2),fill=color);
        self.ArrowPlot.create_line(round(x4), round(y4), round(x2), round(y2),fill=color);

        
    def drawFluxArrow(self,x1,y1,x2,y2,color):
        dx = float(x2-x1);
        dy = float(y2-y1);
     
        # length of arrow head over length of arrow stem
        f = float(1/3.0);
        
        # half-width of arrow head over length of arrow stem
        f2 = float(1/6.0);
        x3 = float(x2 - f*dx - f2*dy);
        y3 = float(y2 - f*dy + f2*dx);
        x4 = float(x2 - f*dx + f2*dy);
        y4 = float(y2 - f*dy - f2*dx);
        
        self.FluxLines.create_line(round(x1), round(y1), round(x2), round(y2),fill =color);
        self.FluxLines.create_line(round(x3), round(y3), round(x2), round(y2),fill=color);
        self.FluxLines.create_line(round(x4), round(y4), round(x2), round(y2),fill=color);

    #x,y pixel location of point to start at
    #sign, +1 to travel with the field, -1 to travel against it
    #maxLength in pixels
    def defDrawFluxLine (self,X,Y,sign,maxLength):
        x=float(X);
        y=float(Y);
        s=float(sign);
        
        for k in xrange(maxLength):
            
            v = self.computeForce(x,y);
            v.x *= s;
            v.y *= s;
            
            self.forceMagnitude =math.sqrt(v.x*v.x+v.y*v.y);
            if self.forceMagnitude == 0:
                break
            v.x /= self.forceMagnitude;
            v.y /= self.forceMagnitude;

            newx = float(x + v.x);
            newy = float(y + v.y)
            setColor =self.mapForceMagnitudeToColor(self.forceMagnitude);
            self.FluxLines.create_line(round(x),round(y),round(newx),round(newy), fill=setColor);
            
            # every few pixels, draw an arrow
            if (k > 0 and (k % (5*self.arrowPlotSpacing) == 0 )):
                self.drawFluxArrow( x, y,x + sign*0.9*self.arrowPlotSpacing*v.x, y + sign*0.9*self.arrowPlotSpacing*v.y,setColor);
            x = newx;
            y = newy; 
            if ( x < 0 or x >= self.width or y < 0 or y >= self.height ):
            #we're outside the image's boundaries
                break;

            #mark this part of the image as occupied by a flux line
            self.map[int(x/self.fluxLineSpacing),int(y/self.fluxLineSpacing)] = True;


    def render(self):
        if self.drawArrowPlot:

            stop = self.width-self.arrowPlotSpacing;
            stop1= self.height-self.arrowPlotSpacing; 
            
            for x in xrange(self.arrowPlotSpacing,stop,self.arrowPlotSpacing):
                for y in xrange(self.arrowPlotSpacing,stop1,self.arrowPlotSpacing):
                    v = self.computeForce(x,y);
                    self.forceMagnitude=float(math.sqrt(v.x*v.x+v.y*v.y));
                    if self.forceMagnitude == 0.0:
                        continue;
                    setColor =(self.mapForceMagnitudeToColor(self.forceMagnitude));

                    #normalize the vector
                    v.x/=self.forceMagnitude;
                    v.y/=self.forceMagnitude;
                    
                    #draw the arrow
                    v.x *= 0.9 * self.arrowPlotSpacing;
                    v.y *= 0.9 * self.arrowPlotSpacing;
                    self.drawArrow(x, y, x + v.x, y + v.y,setColor);

        if self.drawFluxLines:

            #clear the map
            for index in self.map.iterkeys():
                self.map[index] = False;

            for y in reversed(sorted(self.ListElectricCharge.keys())):
                for j in xrange(self.fluxLinesPerCharge):
                    z = self.ListElectricCharge[y];
                    x0 = z.x + float(math.cos(2*math.pi*j/self.fluxLinesPerCharge));
                    y0 = z.y + float(math.sin(2*math.pi*j/self.fluxLinesPerCharge));
            
                    #Use the sign of the charge, so that we always travel away from the charge
                    self.defDrawFluxLine(x0,y0,1.0 if z.q > 0 else -1.0,max(self.width,self.height));
                                
            #Look for regions that are not occupied by flux lines
            for x,y in sorted(self.map.iterkeys()):
                if y is False:
                    
                    #place a seed point in the centre of the region
                    x0 = float((x+0.5)*self.fluxLineSpacing);
                    y0 = float((y+0.5)*self.fluxLineSpacing);
                    
                    #draw flux lines forward and backward through the seed point
                    self.defDrawFluxLine(x0,y0,1.0,max(self.width,self.height));
                    self.defDrawFluxLine(x0,y0,-1.0,max(self.width,self.height));

        #draw the charges
        #When we do the picking, we test for intersection in forward order.
        #Since we want occlusion to lead to predictable picking resolution,
        #we render in reverse order
        for z in reversed(sorted(self.ListElectricCharge.keys())):

            c = self.ListElectricCharge[z];
            x0 = c.x-self.chargeRadius;
            y0 = c.y-self.chargeRadius;
            x1 = c.x+self.chargeRadius;
            y2 = c.y+self.chargeRadius;
            if c.q > 0:
                self.ArrowPlot.create_oval(x0,y0,x1,y2,fill="White", outline='red');
                self.ArrowPlot.create_line(c.x, c.y-self.chargeRadius/2,c.x,c.y+self.chargeRadius/2,fill='black');
                self.ArrowPlot.create_line(c.x-self.chargeRadius/2,c.y,c.x+self.chargeRadius/2,c.y,fill='black');

                self.FluxLines.create_oval(x0,y0,x1,y2,fill="White", outline='red');
                self.FluxLines.create_line(c.x, c.y-self.chargeRadius/2,c.x,c.y+self.chargeRadius/2,fill='black');
                self.FluxLines.create_line(c.x-self.chargeRadius/2,c.y,c.x+self.chargeRadius/2,c.y,fill='black');
            else:
                self.ArrowPlot.create_oval(x0,y0,x1,y2,fill="White",outline='red');
                self.ArrowPlot.create_line(c.x-self.chargeRadius/2,c.y,c.x+self.chargeRadius/2,c.y,fill='black');
                
                self.FluxLines.create_oval(x0,y0,x1,y2,fill="White",outline='red');
                self.FluxLines.create_line(c.x-self.chargeRadius/2,c.y,c.x+self.chargeRadius/2,c.y,fill='black');
    
    def indexOfChargeUnderPixel(self,x,y):

       #return negative 1 if the given pixel does not fall on any charge
        for i in self.ListElectricCharge:
            c = self.ListElectricCharge[i];
            if ((x-c.x)*(x-c.x)+(y-c.y)*(y-c.y))<=self.chargeRadius*self.chargeRadius:
                return 1;
        return -1;
    
    def onbuttonpress(self, event):
        #Check if the canvas has been painted
        if self.painted:
            i = int(self.indexOfChargeUnderPixel(event.x,event.y));
            if event.state == 20 or event.state == 17 or event.state ==12 or event.state ==9:
                
                #delete the charge
                if i >=0:
                    for index, z in self.ListElectricCharge.iteritems():
                        if z.x == event.x and z.y == event.y:
                            self.ListElectricCharge.pop(index);
                            break
                    self.markBackbufferDirty();
                
                #add the negative charge
                else:
                    e = ElectricCharge(event.x,event.y,-1);
                    self.ListElectricCharge[(event.x,event.y)] = e;
                    self.markBackbufferDirty();
            else:
                e = ElectricCharge(event.x,event.y,1);
                self.ListElectricCharge[(event.x,event.y)] = e;
                self.markBackbufferDirty();
        else:
            i = int(self.indexOfChargeUnderPixel(event.x,event.y));
            if event.state == 20 or event.state == 17 or event.state == 12 or event.state ==9:
                e = ElectricCharge(event.x,event.y,-1);
                self.ListElectricCharge[(event.x,event.y)]=e;
                self.markBackbufferDirty();
            else:
                if i>0:
                    pass
                else:
                    e = ElectricCharge(event.x,event.y,1);
                    self.ListElectricCharge[(event.x,event.y)] = e;
                    self.markBackbufferDirty();

    def markBackbufferDirty(self):
        if self.painted is False: 
            self.render();
            self.painted = True;
        else:
            self.ArrowPlot.delete("all");
            self.FluxLines.delete("all");
            self.render();
            self.painted = True;

#use later to figure out proper clear command for both canvas
def Clear():
    app.ArrowPlot.delete("all");
    app.FluxLines.delete("all");
    app.painted = False;
    for key in app.map.keys():
        app.map[key]=False
    for key in app.ListElectricCharge.keys():
        del app.ListElectricCharge[key];

root = Tk()
app = App(root)
root.wm_title("Arrow Plot and FluxLines")
menubar = Menu(root)
menubar.add_command(label='Clear All',command=Clear)
root.config(menu=menubar)
root.mainloop()
