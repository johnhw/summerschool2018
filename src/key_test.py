import keyboard

import numpy as np
from multiprocessing import Queue, Process

# recognise a sequence of integers (e.g. keypress scan codes)
def on_sequence(seq):
    ix = 0
    def update(elt):
        nonlocal ix        
        # match? Increment and return true if complete
        if elt==seq[ix]:            
            ix += 1
            if ix==len(seq):
                ix = 0
                return True
        else:
            # reset to start
            ix = 0
        return False
    return update

def capture_keys(queue):
    print("Ctrl-ESC to exit!")
    all_keys = np.zeros(128, dtype=np.float32)
    running = True
    # stash current state
    current_state = keyboard.stash_state()

    # ctrl-esc
    exit_seq = on_sequence([29,1])
    while running:
        k = keyboard.read_event(True)    
        if k.scan_code<len(all_keys) and k.scan_code>=0:
            if k.event_type=="up" and all_keys[k.scan_code]!=0:
                all_keys[k.scan_code] = 0.0
            if k.event_type=="down" and all_keys[k.scan_code]!=1:                
                all_keys[k.scan_code] = 1.0
                if exit_seq(k.scan_code):
                    running = False
        
        queue.put((all_keys.tobytes(), k.time))
    queue.put(None)
    keyboard.restore_state(current_state)        




if __name__=="__main__":    
    q = Queue()
    keys = Process(target=capture_keys, args=(q,))
    keys.start()
    result = q.get()
    while result:
        arr_bytes, time = result
        keys = np.frombuffer(arr_bytes, dtype=np.float32)
        print(keys)
        result = q.get()

    