from IPython.display import clear_output
import numpy as np
from multiprocessing import Queue, Process
from key_test import capture_keys


def key_tk():
    
    current_state = keyboard.stash_state()    
    q = Queue()
    keys = Process(target=capture_keys, args=(q,))
    keys.start()
    k = KeyDisplay(q)
    

def notebook_keys():
    q = Queue()
    keys = Process(target=capture_keys, args=(q,))
    keys.start()
    result = q.get()
    print("Ctrl-ESC to stop")
    while result:
        arr_bytes, time, name = result        
        print("Ctrl-ESC to stop: {0}".format(name))        
        result = q.get()
    keys.join()