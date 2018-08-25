from tkinter import *
import numpy as np
import json
import pfilter

from tkanvas import TKanvas 
from collections import defaultdict

class Recogniser(object):
    def __init__(self, pfilter, gestures): 
        self.screen_size = 500
        c = TKanvas(draw_fn=self.draw, event_fn=self.event, quit_fn=self.quit, w=self.screen_size, h=self.screen_size)     
        self.mouse = [0,0] # position of the mouse
        self.pfilter = pfilter
        self.pfilter.init_filter()
        self.toast_state = 50
        self.toast = "Start!"
        self.gestures = gestures
        
        self.complete_threshold = 0.9 # point at which gesture is considered complete
        self.entropy_threshold = 0.65 # point at which we will classify a gesture
        
    def quit(self, src):
        pass
        
    def event(self, src, event_type, event):
        if event_type=='mousemotion':
            self.mouse = (event.x, event.y)
            
            
        
    def draw(self, src):        
    
        src.clear()    
        self.toast_state -= 1
        
        
        colors = ["red", "blue", "yellow", "green", "orange", "cyan", "magenta"]
        letters = ["e", "s", "n", "d", "a", "r","",""]
        src.circle(self.mouse[0], self.mouse[1], 3, fill="grey")
        
        n_gestures = len(self.gestures)
        
        self.pfilter.update(np.array(self.mouse))
        particles = self.pfilter.original_particles
        observations = self.pfilter.hypotheses
        weights = self.pfilter.weights
        
        classes = np.zeros(n_gestures,)
        completed = np.zeros(n_gestures,)
        
        for pos,particle,weight in zip(observations, particles, weights):
            src.circle(pos[0], pos[1], 2, fill=colors[int(particle[0])])
            if not np.isnan(weight):
                ix = int(particle[0])
                classes[int(particle[0])] += weight
                gesture_length = len(self.gestures[ix])
                
                # count how many phases ar
                if particle[5]>self.complete_threshold * gesture_length:
                    completed[ix] += weight 
        
        entropy = np.sum([-p*np.log(p)/np.log(2) for p in classes])
        # we have a decision (possibly!)
        if entropy<self.entropy_threshold:
            if np.max(completed)>0.3:
                recognised = np.argmax(completed)
                self.toast = letters[recognised]
                self.toast_state = 100
                self.pfilter.init_filter() # force filter to restart
        
        x = 0
        width = 50
        
        for i in range(n_gestures):
            h = classes[i] * 50.0
            src.rectangle(x, src.h-h, x+width, src.h, fill=colors[i]) 
            src.text(x+width/2, src.h-20, text=letters[i], fill="white", font=("Arial", 20))
            x+=width
        
        if self.toast_state>0:
            src.text(src.w/2, src.h/2, text=self.toast, fill="gray", font=("Arial", 60))
        

def interactive_recogniser(dynamics, observation, prior, weight, gestures):
    
    pf = pfilter.ParticleFilter(initial=prior, 
                                    observe_fn=observation,
                                    n_particles=400,                                    
                                    dynamics_fn=dynamics,
                                    weight_fn=weight,                    
                                    resample_proportion=0.1)
    recogniser = Recogniser(pf, gestures)
   
    
    
class GestureData(object):
    def __init__(self, jsonfile):
        with open(jsonfile, "r") as f:
            gestures_json = json.load(f)
        self.screen_size = max(gestures_json["width"], gestures_json["height"])
        self.gestures = [np.array(path)-np.mean(np.array(path), axis=0) for path in gestures_json["gestures"]]
        self.n_gestures = len(self.gestures)
        
    def get_template(self, i, t):
        if 0<i<self.n_gestures:
            gesture = self.gestures[int(i)]
            t = np.floor(np.clip(t,0,len(gesture)-1))
       
            x, y = gesture[int(t)]
            return [x,y]
        else:
            return [0,0]
        
    def get_speed(self):
        return 1

class Gesture(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.master = Tk()
        self.master.call('wm', 'attributes', '.', '-topmost', True)
        self.w = Canvas(self.master, width=300, height=300)
        self.w.pack()
        self.gesture = None
        self.gestures = []
        self.w.bind('<Motion>', self.motion)
        self.w.bind('<Button-1>', self.click)        
        self.master.bind('<Escape>', self.exit)        
        
        self.ox, self.oy = None, None    
        
    def exit(self, event):
        if self.gesture is not None:
            self.click()
            
        with open("gestures.txt", "w") as f:
            f.write(self.json())
        print("%d gestures recorded to gestures.txt" % (len(self.gestures)))
        self.master.destroy()
        
        
    def redraw(self):        
        w.move(line_id, 0, 1)    
        master.after(50, redraw)
        
    def click(self, event):
        if self.gesture is None:
            self.gesture = []
        else:
            self.gestures.append(self.gesture)
            self.gesture = None
            self.w.delete("all")
    
    def motion(self,event):
        if self.gesture is not None:
            x, y = event.x, self.height - event.y
            self.gesture.append([x,y])
            self.w.create_line(self.ox, self.oy, x,y)
        self.ox, self.oy = x,y
        
    def json(self):
        return json.dumps({"width":self.width, "height":self.height, "gestures":self.gestures})

def record_gestures():
    gesture = Gesture(400,400)
    
    
        
    
