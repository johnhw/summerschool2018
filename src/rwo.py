import scipy.spatial
import numpy as np

class RWO(object):

    def __init__(self, d, threshold=0.45):
        self.bag = None
        self.d = d
        self.threshold = threshold
        self.n_vecs = 0

    def update(self, vector):        
        if self.bag is None:
            self.bag = np.array(vector[None,:])
            self.n_vecs = 1
            return True
        ds = scipy.spatial.distance.cdist(self.bag, vector[None, :], 'euclidean')        

        if np.min(ds)>self.threshold:
            # add to the bag if new enough
            self.bag = np.concatenate((self.bag, vector[None, :]), axis=0)
            self.n_vecs = len(self.bag)
            return True
        return False
