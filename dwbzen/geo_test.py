'''
Created on Apr 26, 2021

@author: don_bacon
 1D avg: 0.3336056415465781     min distance: 6.953338937965015e-08    max distance 0.9991733125913103
 2D avg: 0.5218940528195612     min distance: 0.0002963836942284597    max distance 1.386732445768972
 3D avg: 0.6623875731449357     min distance: 0.006303274998869993     max distance 1.6275309823122912
 4D avg: 0.7786016428780859     min distance: 0.02219800547536187      max distance 1.817787360261562
 5D avg: 0.8795563100273328     min distance: 0.04582378971554501      max distance 1.9186141790261342
'''
import argparse, random, math, numpy as np

class Geo_test(object):
    
    def __init__(self, dims, iterations, trials):
        self.count = 0
        self.trial_count = 0
        self.dimensions = dims
        self.trials = trials
        self.iterations = iterations
        random.seed()
        self.average = 0.0
        self.verbose = 0
        self.max_dist = 0.0
        self.min_dist = 99.0
        self.std_normal = False
    
    def get_point(self):
        if self.std_normal:
            return np.random.randn(self.dimensions)
        else:
            return np.random.random(size=2)
    
    def distance_metric(self, point1, point2):  # 2 points in n-dimensions
        d = 0.0
        dim = len(point1)
        for i in range(0, dim):
            d = d + math.pow( point1[i] - point2[i], 2)
        d = math.sqrt(d)
        return d
        
    def run_trials(self):
        avg_sum = 0.0
        while self.trial_count < self.trials:
            avg_sum = avg_sum + self.run_trial()
            self.trial_count = self.trial_count + 1
            # random.seed()
        self.average = avg_sum / self.trials
        return self.average
        
    def run_trial(self):
        avg = 0.0
        if(self.dimensions == 1):
            avg = self.run_1d_trial()
        else:
            avg = self.run_nd_trial()
            
        if(self.verbose > 0):
            print("{}\t{}".format(self.trial_count, avg))
        return avg
    
    def run_nd_trial(self):
        dsum = 0.0
        for self.count in range(self.iterations):
            p1 = self.get_point()
            p2 = self.get_point()
            d = self.distance_metric(p1,p2)
            if d < self.min_dist:
                self.min_dist = d
            if d > self.max_dist:
                self.max_dist = d
            dsum = dsum+d
        return dsum / self.count
    
    def run_1d_trial(self):
        dsum = 0.0
        for self.count in range(self.iterations):
            p1=random.random()
            p2=random.random()
            d = math.fabs(p2-p1)
            if d < self.min_dist:
                self.min_dist = d
            if d > self.max_dist:
                self.max_dist = d
            dsum = dsum+d
        return dsum / self.count

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Point distance average.')
    parser.add_argument("dimensions", help="number of dimensions: 1 to 3", type=int )
    parser.add_argument("iterations", help="number of iterations per trial", type=int)
    parser.add_argument("--trials", help="number of trials", type=int, default = 1 )
    parser.add_argument('--verbose', '-v', action='count', default=0, help='verbose output level')
    parser.add_argument('--std', action='store_true', help="Use standard normal distribution")

    args = parser.parse_args()
    
    dimensions = args.dimensions
    trials = args.trials
    iterations = args.iterations
    geo_test = Geo_test(dimensions, iterations, trials)
    geo_test.verbose = args.verbose
    geo_test.std_normal = args.std
    avg = geo_test.run_trials()
    print("avg: {}\t min distance: {}\t max distance {}".format(avg, geo_test.min_dist, geo_test.max_dist))
    
    
    