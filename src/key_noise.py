
import numpy as np

def add_noise(x, noise):
    return x + np.random.normal(0,1, noise.shape) * noise

class Corrupter:
    def __init__(self, mix_l, sensor_noise=0.0, obs_noise=0.0, vec_size=128, sensor_alpha=0.0, obs_alpha=0.0):
        self.mix_l = mix_l
        self.vecs = np.zeros((len(mix_l), vec_size))
        self.sensor_noise = np.array(sensor_noise)
        self.obs_noise = np.array(obs_noise)
        self.ix = 0 # buffer write position
        self.n = len(self.vecs)
        self.ix_array = list(range(self.n))
        self.sensor_alpha = sensor_alpha
        self.obs_alpha = obs_alpha
        self.last_output = np.zeros(vec_size,)
        self.last_sensor = np.zeros(vec_size,)
                
    def update(self, k_vec):
        self.last_sensor = (1-self.sensor_alpha) * k_vec  + self.sensor_alpha*self.last_sensor
        self.vecs[self.ix] = add_noise(self.last_sensor, self.sensor_noise)
        self.ix = (self.ix+1) % self.n
        ixs = self.ix_array[self.ix:] + self.ix_array[:self.ix]        
        output = np.sum([self.mix_l[i] @ self.vecs[ixs[i]] for i in range(self.n)], axis=0)
        self.last_output = (1-self.obs_alpha) * output  + self.obs_alpha*self.last_output
        return add_noise(self.last_output, self.obs_noise)