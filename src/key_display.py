from key_test import capture_keys
from tkanvas import TKanvas
# py 2.x compatibility
try: 
    import Tkinter as tkinter
    from Tkinter import mainloop
except ImportError:
    from tkinter import mainloop

import numpy as np
from multiprocessing import Queue, Process
import matplotlib
import time
import matplotlib.pyplot as plt
from rwo import RWO
from key_noise import Corrupter


def tkcolor(rgb):
    return "#" + "".join(("%02X" % (int(c * 255)) for c in rgb[:3]))

class KeyDisplay(object):
    def __init__(self, q):
        self.q = q
        self.keys = np.zeros(128, dtype=np.float32)
        self.last_t = 0.0
        self.block_size = 24
        self.canvas = TKanvas(draw_fn=self.draw, tick_fn=self.tick, w=self.block_size*17, h = self.block_size*10)
        self.rects = []
        self.first = True
        self.status = 'OK'
        self.rwo = RWO(128)
        self.cmap = plt.get_cmap("viridis")
        self.canvas.title("Ctrl-ESC-ESC-ESC to quit")

        
        np.random.seed(35325)
        random_permutation = np.eye(128)[np.random.permutation(128)]
        self.corrupter = Corrupter(            
            [random_permutation],
            sensor_noise=np.full((128,), 0.05),                        
            obs_alpha=0.9,
        )
        self.corrupt_keys = np.zeros_like(self.keys)

    def tick(self, dt):
        try:
            result = self.q.get(block=False)
            if result:
                arr_bytes, time, _ = result
                self.keys[:] = np.frombuffer(arr_bytes, dtype=np.float32)
                self.last_t = time
            else:
                self.canvas.quit(None)
        except:
            # no updates, do nothing
            pass

        self.corrupt_keys = self.corrupter.update(self.keys)
        self.rwo.update(self.corrupt_keys)

    def draw(self, src):        
        # draw the blank squares for the outputs
        if self.first:
            src.clear()
            self.text = src.text(self.block_size/2, src.h-self.block_size/2, text=str(self.status), fill="white", anchor='w', font=('Arial', 16))
            sz = self.block_size
            for i in range(16):
                for j in range(8):
                    ix = i * 8 + j
                    rect = src.rectangle(
                        sz/2 + i * sz, sz/2 +j * sz, sz/2 +(i + 1) * sz, sz/2 +(j + 1) * sz, fill="blue"
                    )
                    self.rects.append(rect)
            self.first = False
        else:
            src.canvas.itemconfig(self.text, text=str(self.rwo.n_vecs))
            # update the fill colours
            for i in range(16):
                for j in range(8):
                    ix = i * 8 + j
                    color = self.cmap(self.corrupt_keys[ix])[:3]
                    if self.keys[ix] == 0:
                        src.canvas.itemconfig(self.rects[ix], fill=tkcolor(color))
                    else:
                        src.canvas.itemconfig(self.rects[ix], fill=tkcolor(color))

def key_tk():    
    import keyboard
    current_state = keyboard.stash_state()    
    q = Queue()
    keys = Process(target=capture_keys, args=(q,))
    keys.start()
    k = KeyDisplay(q)
    return current_state


if __name__ == "__main__":
    import keyboard, atexit
    current_state = keyboard.stash_state()
    atexit.register(keyboard.restore_state, current_state)
    q = Queue()
    keys = Process(target=capture_keys, args=(q,))
    keys.start()
    k = KeyDisplay(q)
    mainloop()
    

