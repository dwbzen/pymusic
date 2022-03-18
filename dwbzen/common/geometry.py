import math

class Geometry(object):
    
    @staticmethod    
    def polygon_points(nsides = 24, radius = 400):
        theta = math.radians(360/nsides)
        points = []
        for i in range(nsides + 1):
            p = ( round(radius * math.cos(i * theta), 4), round(radius * math.sin(i * theta), 4) )
            points.append(p)
        return points

    @staticmethod    
    def points_dist(p1:(float,float), p2:(float,float)) -> float:
        '''Calculates the distance between two points.
        
        '''
        d = math.sqrt( (p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 )
        return d

    @staticmethod    
    def segment_points(p1:(float,float), p2:(float,float), nsegments=4):
        points = []
        #
        # add in the points between p1 and p2
        #
        xd = (p2[0] - p1[0])/nsegments
        yd = (p2[1] - p1[1])/nsegments
        for n in range(nsegments):
            p = (p1[0] + n*xd, p1[1] + n*yd)
            points.append(p)
        points.append(p2)
        return points

    @staticmethod
    def polygon_segment_points(nsides = 12, radius = 400, nsegments = 4):
        """Get all segment points for a polygon.
            Arguments:
                nsides - polygon number of sides, default is 12
                radius - polygon radius in units, default is 400
                nsegments - number of segments to divide each pair of points, default is 4
            Returns:
                a dict having the polygon segment number (0 to nsegments-1) as the key, and the segment points as the value
            Segments are numbered counter-clockwise order with the first segment coordinate at x=nradius, y=0

        """
        points = Geometry.polygon_points(nsides=nsides, radius=radius)
        seg_points = {}
        for i in range(nsides):
            sp = Geometry.segment_points(points[i], points[i+1], nsegments)
            key = i # (points[i], points[i+1])
            seg_points[key] = sp
        return seg_points
