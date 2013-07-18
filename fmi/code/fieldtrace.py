__authors__ = ["David PS"]
__email__ = "dps.helio-?-gmail.com"

import argparse
import sys
import hcpy
import numpy as np
import astropy.io.votable as votable

def vot2points(filename):
    vot = votable.parse_single_table(filename)
    types = ['x', 'y', 'z']
    points = np.empty((vot.nrows, 3))
    for idx, elem in enumerate(types):
        column = vot.get_field_by_id_or_name(elem)
        if column.ucd == 'pos.cartesian.' + elem:
            points[:, idx] = vot.array[column.ID].data
    return points

def netcdf2points(filename):
    pass
    
def ascii2points(filename):
    pass

def points2vot(filename, fieldlines, query):
    # as explained in
    # https://astropy.readthedocs.org/en/latest/io/votable/index.html#building-a-new-table-from-scratch
    vot = votable.tree.VOTableFile()

    resource = votable.tree.Resource()
    vot.resources.append(resource)
    # TODO: add information for the input (query)
    
    for lines in fieldlines:
        table = votable.tree.Table(vot)
        resource.tables.append(table)

        table = fields.extend([
            votable.tree.Field(votable, name='posx', datatype='double', arraysize='1', units='m', ucd='pos.cartesian.x'),
            votable.tree.Field(votable, name='posy', datatype='double', arraysize='1', units='m', ucd='pos.cartesian.y'),
            votable.tree.Field(votable, name='posz', datatype='double', arraysize='1', units='m', ucd='pos.cartesian.z')
        ])
        
        table.create_arrays(lines.shape[0])
    
        lines_mask = np.ma.masked_array(lines, mask = False)
        
        table.array = lines_mask
    
    votable.to_xml(filename)

class Fieldtrack(object):
    
    def __init__(self, hcfilename, 
                 stop_minradius=0, stop_box=None):
#        hc = hcpy(hcfilename)
#        self.hc = hc
        try:
            self.hc = hcpy.HCpy(hcfilename)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        self.stop_minradius = stop_minradius
        if stop_box is None:
            stop_box = self.hc.box
        try:
            stop_box = np.array(stop_box).reshape(3,2)
        except ValueError as e:
            print 'stop_box does not have the right dimension ', e

        #  Create a boolean array which contains the values within
        # model box
        box_bool = np.array([stop_box[:,0] >= self.hc.box[:,0], 
                             stop_box[:,1] <= self.hc.box[:,1]]).transpose()
        # Now, stop_box contains the limits within the box
        self.stop_box = stop_box * box_bool + self.hc.box * ~box_bool


    def track(self, points, vectorfield, stepsize=1, maxstep=1,
              direction='forward', method='midpoint'):

        self.stepsize = stepsize
        self.maxstep = maxstep
        self.vectorfield = vectorfield

        direction_sign = {'forward': 1., 'backward': -1}

        vectors = [vectorfield+x for x in ['x', 'y', 'z']]

        track_points = np.empty((maxstep+1, 3))

        track_points[0,:] = np.array(points)
        # midpoint implementation
        for n in range(maxstep):
            # Calculate the Vector direction for half of the step
            midpoint = self.follow_point(track_points[n,:], track_points[n,:], 
                                         0.5 * self.stepsize * direction_sign[direction], 
                                         vectors)
            if midpoint is False or not self._within(midpoint):
                break
            #  Apply midpoint direction to original point.
            endpoint = self.follow_point(midpoint, track_points[n,:], 
                                         self.stepsize * direction_sign[direction], 
                                         vectors)
            if endpoint is False or not self._within(endpoint):
                break
            track_points[n + 1, :] = endpoint
        return track_points[:n+1,:]


    def follow_point(self, initpoint, point0, stepsize, vectors):
        x = initpoint
        intpol3d = lambda v: self.hc.hcintpol([x[0]], [x[1]], [x[2]], [v], linear=False)[v][0]
        F = map(intpol3d, vectors)
        if np.dot(F, F) == 0:
            return False
        F = F / np.sqrt(np.dot(F, F))
        return point0 + F * stepsize


    def _within(self, points):
        ''' Check whether the point is within boundaries'''
        result = True
        for idx,element in enumerate(points):
            result = result and self.stop_box[idx,0] <= element <= self.stop_box[idx,1]
        if result:
            return np.sqrt(np.dot(points, points)) >= self.stop_minradius
        return False

        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('Calculates a fieldlines '
                                                  'from an hc model and a list '
                                                  'of starting points.'))
    parser.add_argument('hcfile', metavar='hcfile', type=argparse.FileType('r'),
                        help='File from which we want to extract the fieldlines',
                        required=True)
    parser.add_argument('-i', '--input', default=None, type=argparse.FileType('r'),
                        help=('File (netCDF, VOTable or ASCII) with '
                              'starting points for the field lines.'),
                        dest='mode')
    parser.add_argument('-ifmt','--informat', choices=['vot', 'netcdf', 'csv'],
                        default='csv', type=str,
                        help='Format of the input file')
    parser.add_argument('-c', '--coordinates', nargs=3, type=float,
                        help='x y z coordinates as starting point for field line',
                        dest='mode')
    #parser.add_argument('--savepath', default='./', type=str, 
    #                    help='Path where to save the result')
    parser.add_argument('-ofmt','--outformat', choices=['vot','netcdf'],
                        default="vot",
                        help=('Format for the output, they are either: '
                              'vot for votable, or netcdf'))
    parser.add_argument('-o','--output', default=None, type=argparse.FileType('w'),
                        help='Output file')

    parser.add_argument('--method', choices=['midpoint'], default='midpoint',
                        help='Method used to calculate the field line.')

    parser.add_argument('--direction', choices=['forward','backward'], 
                        default='forward',
                        help='Field line will follow such direction')
    paraser.add_argument('-vf','--vectorfield', default=None, type=str,
                         #nargs='*',
                         help=('Spaced list of all the vector fields desired to trace.'
                               ' All vectors are taken if ommited.'))
    parser.add_argument('-ss','--stepsize', type=float,
                        default=40000,#TODO: deffinition -> gridsize/4
                        help='Step size in units?') #TODO: Which units?
    parse.add_argument('-maxs','--maxstep', type=int,
                       default=400, #TODO: needs to be determined
                       help='Maximum number of steps per field/stream line')
    parse.add_argument('-minr','--minradius', type=float,
                       default=0,
                       help=('Field line tracing stops if distance from center '
                             'is smaller than this value. Units: ??')) #TODO: units?
    parse.add_argument('-b','--boxlimit', nargs=6, type=float,
                       default=None,
                       help=('Field line tracing stops if outside the box boundaries: '
                             'x1 x2 y1 y2 z1 z2. Units: ?'))#TODO: units?





    args = parser.parse_args([x for x in sys.argv[1:]])
    if not args.mode:
        args.error('One of --input or --coordinates must be given')

    

    # Check extension of initpoints and pass parser to get points
    field = Fieldtrack(args.hcfile,
                       stop_minradius=args.minradius,
                       stop_box=args.boxlimit)

    # Handle input formats
    if args.informat == 'vot':
        try:
            votable.is_votable(args.input)
        except:
            print 'The input file is not formatted as votable'
        
        points = vot2points(args.input)

    # Calculate field lines  #TODO: what if multiple vectorfields?
    fieldlines = []
    for row in points:
        fieldlines.append(field.track(row, 
                                      args.vectorfield,
                                      args.stepsize,
                                      args.maxstep,
                                      args.direction,
                                      'midpoint'))

    # Save in the requested output format
    if args.outformat == 'vot':
        points2vot(args.output, fieldlines, args)
        
