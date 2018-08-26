import scipy.spatial
import numpy as np

class RWO(object):

    def __init__(self, d, threshold=0.45, bag=None, metric='euclidean'):        
        
        if bag is not None and "data" in bag and len(bag["data"])>0:
            self.bag = np.array(self.bag["data"])
        else:
            self.bag = None
        self.output = bag
                
        self.d = d
        self.metric = metric
        self.threshold = threshold
        self.n_vecs = 0

    def update(self, vector, t):        
        if self.bag is None:
            self.bag = np.array(vector[None,:])
            self.n_vecs = 1
            if self.output is not None:
                self.output["data"].append(vector)
                self.output["time"].append(t)
            return True
        ds = scipy.spatial.distance.cdist(self.bag, vector[None, :], self.metric)        

        if np.min(ds)>self.threshold:
            # add to the bag if new enough
            self.bag = np.concatenate((self.bag, vector[None, :]), axis=0)
            self.n_vecs = len(self.bag)
            if self.output is not None:
                self.output["data"].append(vector)
                self.output["time"].append(t)
            return True
        return False
