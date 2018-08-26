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


class TKMatrix(object):
    def __init__(self, canvas, shape, size, origin=None, cmap=None):
        self.origin = origin or (size / 2, size / 2)
        self.cmap = cmap or plt.get_cmap("viridis")
        self.shape = shape
        self.size = size
        self.canvas = canvas
        self.create_rects()

    def create_rects(self):
        self.rects = []
        sz = self.size
        ox, oy = self.origin
        for i in range(self.shape[1]):
            for j in range(self.shape[0]):
                rect = self.canvas.rectangle(
                    ox + i * sz,
                    oy + j * sz,
                    ox + (i + 1) * sz,
                    oy + (j + 1) * sz,
                    fill="blue",
                )
                self.rects.append(rect)

    def update(self, matrix):
        assert matrix.shape == self.shape
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                ix = i * self.shape[1] + j
                color = self.cmap(matrix[i, j])[:3]
                self.canvas.canvas.itemconfig(self.rects[ix], fill=tkcolor(color))


class KeyDisplay(object):
    def __init__(
        self,
        q,
        shape=(8, 16),
        transform_fn=None,
        rwo_kwargs=None,
        alpha=0.9,
        noise=0.05,
    ):
        self.transform_fn = transform_fn or (lambda x: x)  # default to identity
        self.shape = shape
        self.state = np.zeros(shape)

        self.q = q  # keyboard input
        self.keys = np.zeros(128, dtype=np.float32)

        self.block_size = 24

        self.status = "OK"
        self.use_rwo = rwo_kwargs is not None
        if self.use_rwo:
            self.rwo = RWO(128, **rwo_kwargs)
        
        np.random.seed(35325)
        random_permutation = np.eye(128)[np.random.permutation(128)]
        self.corrupter = Corrupter(
            [random_permutation], sensor_noise=np.full((128,), noise), obs_alpha=alpha
        )
        self.corrupt_keys = np.zeros_like(self.keys)
        
        self.canvas = TKanvas(
            draw_fn=self.draw,
            tick_fn=self.tick,
            w=self.block_size * 17,
            h=self.block_size * 10,
        )
        self.canvas.title("Ctrl-ESC-ESC-ESC to quit")
        self.matrix_display = TKMatrix(self.canvas, self.shape, self.block_size)                
        self.text = self.canvas.text(
            self.block_size / 2,
            self.canvas.h - self.block_size / 2,
            text=str(self.status),
            fill="white",
            anchor="w",
            font=("Arial", 16),
        )


    def tick(self, dt):
        try:
            result = self.q.get(block=False)
            if result:
                arr_bytes, _, _ = result
                self.keys[:] = np.frombuffer(arr_bytes, dtype=np.float32)
            else:
                self.canvas.quit(None)
        except:
            # no updates, do nothing
            pass

        self.corrupt_keys = self.corrupter.update(self.keys)
        if self.use_rwo:
            self.rwo.update(self.corrupt_keys)
        self.state = self.transform_fn(self.corrupt_keys).reshape(self.shape)        

    def draw(self, src):
        # draw the blank squares for the outputs
        if self.use_rwo:
            src.canvas.itemconfig(self.text, text=str(self.rwo.n_vecs))
        self.matrix_display.update(self.state)


def key_tk(*args, **kwargs):
    import keyboard

    current_state = keyboard.stash_state()
    q = Queue()
    keys = Process(target=capture_keys, args=(q,))
    keys.start()
    k = KeyDisplay(q, *args, **kwargs)
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

