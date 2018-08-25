#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Self-organizing map
# Copyright (C) 2011  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License.
# -----------------------------------------------------------------------------
import numpy as np
import scipy.weave

def fromdistance(fn, shape, center=None, dtype=float):
    def distance(*args):
        d = 0
        for i in range(len(shape)):
            d += ((args[i]-center[i])/float(max(1,shape[i]-1)))**2
        return np.sqrt(d)/np.sqrt(len(shape))
    if center == None:
        center = np.array(list(shape))//2
    return fn(np.fromfunction(distance,shape,dtype=dtype))

def Gaussian(shape,center,sigma=0.5):
    ''' '''
    def g(x):
        return np.exp(-x**2/sigma**2)
    return fromdistance(g,shape,center)
    

    
def blitz_gaussian(shape, center, sigma=0.5):
    result = np.zeros(shape)
    w,h  = shape
    x, y = center
    code = """
    int i, j;
    double dx,dy;
    double d,g;
    for(i=0;i<w;i++) 
    {
        for(j=0;j<h;j++) 
        {
            dx = abs((double)i-(double)x);
            dy = abs((double)j-(double)y);
            if(dx>w/2)
                dx = w - dx;
            if(dy>h/2)
                dy = h - dy;
            dx /= float(w);
            dy /= float(h);
                
            
            d = sqrt(dx*dx+dy*dy);
            g = exp(-d*d/(sigma*sigma));            
            result(i,j) = g;
        }
    }    
    
    """    
    
    err = scipy.weave.inline(code,
                           ['result', 'w', 'h', 'x', 'y', 'sigma'],
                           type_converters=scipy.weave.converters.blitz,
                           compiler = 'gcc')
    return result


class SOM:
    ''' Self-organizing map '''

    def __init__(self, *args):
        ''' Initialize som '''
        self.codebook = np.zeros(args)
        self.reset()

    def reset(self):
        ''' Reset weights '''
        self.codebook = np.random.random(self.codebook.shape)

  
        
    def classify(self, sample):
        ''' classify a sample '''
        D = ((self.codebook-sample)**2).sum(axis=-1)
        winner = np.unravel_index(np.argmin(D), D.shape)        
        return winner
        
    def density(self, samples):
        w, h, d = self.codebook.shape
        density = np.zeros((w,h))
        
        
        for sample in samples:
            D = ((self.codebook-sample)**2).sum(axis=-1)
            winner = np.unravel_index(np.argmin(D), D.shape) 
            density[winner] += 1
            
        return density
            

            
        
    
    def get_nearest(self, x, y, data):
        print x,y
        D = ((self.codebook[x,y,:]-data)**2).sum(axis=-1)
        winner = np.argmin(D)
        return data[winner,:], winner
    
    
    def get_n_nearest_indices(self, x, y, data):
        D = ((self.codebook[x,y,:]-data)**2).sum(axis=-1)
        winner = np.argsort(D)
        return winner, D
    
    def learn(self, samples, epochs=10000, sigma=(10, 0.001), lrate=(0.5,0.005)):
        ''' Learn samples '''
        sigma_i, sigma_f = sigma
        lrate_i, lrate_f = lrate
                
        lrate = lrate_i
        sigma = sigma_i
        s = samples.shape[0]
        for i in range(epochs):
            if i%500==0:
                print "Epoch \t %d /\t %d \tLrate:%.2f\t Sigma:%.2f" % (i, epochs, lrate, sigma)
            # Adjust learning rate and neighborhood
            t = i/float(epochs)
            lrate = lrate_i*(lrate_f/float(lrate_i))**t
            sigma = sigma_i*(sigma_f/float(sigma_i))**t

            # Get random sample
            index = np.random.randint(0,s)
            data = samples[index]

            # Get index of nearest node (minimum distance)
            
            D = ((self.codebook-data)**2).sum(axis=-1)
            winner = np.unravel_index(np.argmin(D), D.shape)

            # Generate a Gaussian centered on winner
            G = Gaussian(D.shape, winner, sigma)
            G = np.nan_to_num(G)

            # Move nodes towards sample according to Gaussian 
            delta = self.codebook-data
            for i in range(self.codebook.shape[-1]):
                self.codebook[...,i] -= lrate * G * delta[...,i]


# -----------------------------------------------------------------------------
if __name__ == '__main__':

    import pylab
    
    pylab.figure(1)
    g =  Gaussian((20,10), (1,5), 1.0)
    pylab.imshow(g)
    pylab.figure(2)
    g =  blitz_gaussian((20,10), (1,8), 1.0)
    pylab.imshow(g)
    
    pylab.show()
    

    import matplotlib
    import matplotlib.pyplot as plt
    try:    from voronoi import voronoi
    except: voronoi = None

    def learn(network, samples, epochs=25000, sigma=(10, 0.01), lrate=(0.5,0.005)):
        network.learn(samples, epochs)
        fig = plt.figure(figsize=(10,10))
        axes = fig.add_subplot(1,1,1)
        # Draw samples
        x,y = samples[:,0], samples[:,1]
        plt.scatter(x, y, s=1.0, color='b', alpha=0.1, zorder=1)
        # Draw network
        x,y = network.codebook[...,0], network.codebook[...,1]
        if len(network.codebook.shape) > 2:
            for i in range(network.codebook.shape[0]):
                plt.plot (x[i,:], y[i,:], 'k', alpha=0.85, lw=1.5, zorder=2)
            for i in range(network.codebook.shape[1]):
                plt.plot (x[:,i], y[:,i], 'k', alpha=0.85, lw=1.5, zorder=2)
        else:
            plt.plot (x, y, 'k', alpha=0.85, lw=1.5, zorder=2)
        plt.scatter (x, y, s=50, c='w', edgecolors='k', zorder=3)
        if voronoi is not None:
            segments = voronoi(x.ravel(),y.ravel())
            lines = matplotlib.collections.LineCollection(segments, color='0.65')
            axes.add_collection(lines)
        plt.axis([0,1,0,1])
        plt.xticks([]), plt.yticks([])
        plt.show()

    # Example 1: 2d uniform distribution (1d)
    # -------------------------------------------------------------------------
    print 'One-dimensional SOM over two-dimensional uniform square'
    som = SOM(100,2)
    samples = np.random.random((10000,2))
    learn(som, samples)

    # Example 2: 2d uniform distribution (2d)
    # -------------------------------------------------------------------------
    print 'Two-dimensional SOM over two-dimensional uniform square'
    som = SOM(10,10,2)
    samples = np.random.random((10000,2))
    learn(som, samples)

    # Example 3: 2d non-uniform distribution (2d)
    # -------------------------------------------------------------------------
    print 'Two-dimensional SOM over two-dimensional non-uniform disc'
    som = SOM(10,10,2)
    samples = np.random.normal(loc=.5, scale=.2,size=(10000,2))
    learn(som, samples)

    # Example 4: 2d non-uniform disc distribution (2d)
    # -------------------------------------------------------------------------
    print 'Two-dimensional SOM over two-dimensional non-uniform ring'
    som = SOM(10,10,2)
    angles = np.random.random(10000)*2*np.pi
    radius = 0.25+np.random.random(10000)*.25
    samples = np.zeros((10000,2))
    samples[:,0] = 0.5+radius*np.cos(angles)
    samples[:,1] = 0.5+radius*np.sin(angles)
    learn(som, samples)

