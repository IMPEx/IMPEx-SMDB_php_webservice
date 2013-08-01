__authors__ = ["David PS"]
__email__ = "dps.helio-?-gmail.com"

import argparse
import sys
import os
import subprocess
import numpy as np
import json
import astropy.io.votable as votable
import astropy.units as u
from  scipy.io import netcdf
from itertools import izip
import urllib2
import StringIO
import tempfile
import datetime
import ConfigParser

impex_cfg = ConfigParser.RawConfigParser()
impex_cfg.read('fmi.cfg')

# Definitions for fields #
fields_props = {'x':     {'name': 'posx', 'ucd': 'pos.cartesian.x', 'units': u.m, 'type': 'double', 'size': '1'},
                'y':     {'name': 'posy', 'ucd': 'pos.cartesian.y', 'units': u.m, 'type': 'double', 'size': '1'},
                'z':     {'name': 'posz', 'ucd': 'pos.cartesian.z', 'units': u.m, 'type': 'double', 'size': '1'},
                'rho':   {'name': 'rho', 'ucd': 'phys.density',    'units': u.kilogram / u.m ** 3, 'type': 'double', 'size': '1'},
                'n':     {'name': 'n', 'ucd': 'phys.density',    'units': u.m ** -3, 'type': 'double', 'size': '1'},
                'rhovx': {'name': 'rhovx', 'ucd': 'phys.density',    'units': u.kilogram / u.m ** 3, 'type': 'double', 'size': '1'},
                'rhovy': {'name': 'rhovy','ucd': 'phys.density',    'units': u.kilogram / u.m ** 3, 'type': 'double', 'size': '1'},
                'rhovz': {'name': 'rhovz','ucd': 'phys.density',    'units': u.kilogram / u.m ** 3, 'type': 'double', 'size': '1'},
                'vx' :   {'name': 'vx', 'ucd': 'phys.veloc',      'units': u.m / u.s, 'type': 'double', 'size': '1'},
                'vy' :   {'name': 'vy', 'ucd': 'phys.veloc',      'units': u.m / u.s, 'type': 'double', 'size': '1'},
                'vz' :   {'name': 'vz', 'ucd': 'phys.veloc',      'units': u.m / u.s, 'type': 'double', 'size': '1'},
                'vr' :   {'name': 'vr', 'ucd': 'phys.veloc',      'units': u.m / u.s, 'type': 'double', 'size': '1'},
                'v'  :   {'name': 'v', 'ucd': 'phys.veloc',      'units': u.m / u.s, 'type': 'double', 'size': '1'},
                'v2' :   {'name': 'v2', 'ucd': 'phys.veloc',      'units': u.m / u.s, 'type': 'double', 'size': '1'}, # What's this velocity?
                'U'  :   {'name': 'U','ucd': 'phys.energy.density', 'units': u.J / u.m ** 3, 'type': 'double', 'size': '1'},
                'U1' :   {'name': 'U1','ucd': 'phys.energy.density', 'units': u.J / u.m ** 3, 'type': 'double', 'size': '1'},
                'P'  :   {'name': 'P','ucd': 'phys.pressure', 'units': u.J / u.m ** 3, 'type': 'double', 'size': '1'},
                'T'  :   {'name': 'T','ucd': 'phys.temperature', 'units': u.K, 'type': 'double', 'size': '1'},
                'Bx' :   {'name': 'Bx','ucd': 'phys.magField', 'units': u.T, 'type': 'double', 'size': '1'},
                'By' :   {'name': 'By','ucd': 'phys.magField', 'units': u.T, 'type': 'double', 'size': '1'},
                'Bz' :   {'name': 'Bz','ucd': 'phys.magField', 'units': u.T, 'type': 'double', 'size': '1'},
                'B'  :   {'name': 'B','ucd': 'phys.magField', 'units': u.T, 'type': 'double', 'size': '1'},
                'Ex' :   {'name': 'Ex','ucd': 'phys.electField', 'units': u.V / u.m ** 2, 'type': 'double', 'size': '1'},
                'Ey' :   {'name': 'Ex','ucd': 'phys.electField', 'units': u.V / u.m ** 2, 'type': 'double', 'size': '1'},
                'Ez' :   {'name': 'Ex','ucd': 'phys.electField', 'units': u.V / u.m ** 2, 'type': 'double', 'size': '1'},
                'E'  :   {'name': 'E','ucd': 'phys.electField', 'units': u.V / u.m ** 2, 'type': 'double', 'size': '1'}, 
                'Time':  {'name': 'Date', 'ucd': 'TIME', 'unit': 'iso-8601', 'type': 'char', 'size': '*'}
}                            

def query2string(query):
    finalstring = 'Result provided by impex-fp7 project with query {\n '
    # TODO!
    for key in query:
        if key == 'variables':
            finalstring += key + ': ' + ','.join(query[key]) + '\n '
        else:
            finalstring += key + ': ' + str(query[key]) + '\n '
    
    finalstring += '}\n == Query executed on: ' + datetime.datetime.now().isoformat() + '==\n'
    return finalstring

def vot2points(filename):
    vot = votable.parse_single_table(filename)
    types = ['x', 'y', 'z']
    points = np.empty((vot.nrows, 3))
    for column in vot.iter_fields_and_params():
        if column.name.lower() in types:
            ucd_name = 'pos.cartesian.' + column.name.lower()
            idx = types.index(column.name.lower())
            if (column.ucd == ucd_name) or (column.ucd == ucd_name.upper()):
                point_column = vot.array[column.ID].data * column.unit
                points[:, idx] = point_column.si.value
    return points

def points2vot(filename, points_d, query, time = None):
    #'''
    #filename where to write the votable
    #points_d points dictionary where the key is the variable and it contains a list of its values
    #query    the query made to get this votable
    #'''
    # as explained in
    # https://astropy.readthedocs.org/en/latest/io/votable/index.html#building-a-new-table-from-scratch

    vot = votable.tree.VOTableFile()

    resource = votable.tree.Resource()
    vot.resources.append(resource)

    # Query information
    # TODO: add information for the input (query)
    params = votable.tree.Param(vot, 'Query', arraysize = '*')
    resource.params.append(params)

    params.description = query2string(query)
    
    # Tabular information
    table = votable.tree.Table(vot)
    resource.tables.append(table)

    var = sorted(points_d.keys())
    if time is None:
        var = var[-3:] + var[:-3]
    else:
        var = ['Time'] + var[-3:] + var[:-3]

    fields = [votable.tree.Field(votable, name=fields_props[v]['name'], datatype=fields_props[v]['type'], 
                                 arraysize=fields_props[v]['size'], unit=fields_props[v]['units'].to_string(), 
                                 ucd=fields_props[v]['ucd']) for v in var]
    table.fields.extend(fields)

    # points_d dict to array
    points_array = np.array([points_d[x] for x in var]).transpose()
    table.create_arrays(points_array.shape[0])
        
    if time is None:
        points_mask = np.ma.masked_array(points_array, mask = False)
        table.array = points_mask
    else:
        for i, line in enumerate(time):
            table.array[i] = tuple(time[i]) + tuple(points_array[i, :])

    vot.to_xml(filename)

def points2netcdf(filename, points_d, query, time = None):
    f = netcdf.netcdf_file(filename, 'w')
    f.history = query2string(query)

    if time is not None:
        # convert time to seconds from first point
        iso8601_fmt = '%Y-%m-%dT%H:%M:%S.%f'
        f.createDimension('time', len(time))
        time_n = f.createVariable('time', 'd', ('time',))
        time_n.units = 'Seconds since ' + time[0]
        time = [datetime.datetime.strptime(x, iso8601_fmt) for x in time]
        time_n[:] = [(x-time[0]).total_seconds()  for x in time] 
    
    dim = 'dim'
    f.createDimension(dim, len(points_d[points_d.keys()[0]]))
    for key in points_d.keys():
        key_n = f.createVariable(fields_props[key]['name'], fields_props[key]['type'],(dim,))
        key_n.units = fields_props[key]['units'].to_string()
        key_n[:] = points_d[key]
    f.close()


def hcintpol(filename, x, y, z, variables=None, linear=True):
    '''
    x,y,z needs to be a list of numbers, not other type
    variables need to be a list too
    '''
    cmd = 'hcintpol ' #Note, hcintpol needs to be in the path!
    if linear:
        cmd += ' -z '
    if variables is not None:
        cmd += ' -v '+ ','.join(variables)
        cmd += ' ' + filename

    # Coordinates single or multiple values
    coordinates = ''
    # check whether a list as input
    try:
        for i,j,k in izip(x, y, z):
            coordinates += '{0:e} {1:e} {2:e}\n'.format(i, j, k)
    except TypeError:
        print('inputs x, y and z need to be a list\n')
    except:
        print('something went wrong\n')
        raise

    # Execute the command
    hc_in = subprocess.Popen(cmd, shell=True, 
                             stdout=subprocess.PIPE, 
                             stdin=subprocess.PIPE)
    interpolatedvalues, error = hc_in.communicate(coordinates)

    # Extract the values as a dictionary {var(x,y,z,rho): [values]}
    for line in interpolatedvalues.splitlines():
        if line[0] == '#':
            variables_list = line[1:].split()
            variables_out = {var: [] for var in variables_list}
        if line[0] != '#':
            values = line.split()
            for i, var in enumerate(variables_list):
                variables_out[var].append(float(values[i]))

    return variables_out

def getDataPointValue(dict_input):
    '''
    Executes the method with the same name.  The input has to be a dictionary
    with all the parameters needed, they are:
    -function: getDataPointValue
    -ResourceID: Number from IMPEx
    -variables: List of variables
    -url_XYZ: url address to the input data
    -IMFClockAngle: Not used here, yet.
    -InterpolationMethod: whether lineal or not
    -OutputFiletype: which kind (netcdf, votable, csv)
    '''
    outjson = {'out_url':'', 'error':'' }
    # TODO: read config file, paths...
    # Get filename - TODO: Check whether it's right/accessible
    filename = dict_input['filename']
    # Check variables is a proper list (Needed?)
    # Check Interpolation Method
    if (dict_input['order'] == 'nearestgridpoint'):
        linear = False
    else:
        linear = True
    
    # url_XYZ - Get the votable file, download it; process it to [x],[y],[z] ; TODO: Check whther it does not fail
    url_XYZ = dict_input['url_XYZ']
    response = urllib2.urlopen(url_XYZ.replace('\\',''))
    votfile = StringIO.StringIO()
    votfile.write(response.read())
    points = vot2points(votfile)
    x, y, z = points[:,0], points[:,1], points[:, 2]

    # Run hcintpol with the the file, coordinates, var and intpol method
    filename = str(dict_input['filename'])
    result = hcintpol(filename.replace('\\',''), 
                      x, y, z, 
                      variables=dict_input['variables'], 
                      linear=linear)

    # write in the fileformat requested
    write_file = {'votable': points2vot, 'netcdf': points2netcdf}
    # - Create file
    outfile = tempfile.NamedTemporaryFile(prefix = 'hwa_', dir = impex_cfg.get('fmi', 'diroutput'), suffix = '.'+dict_input['OutputFiletype'])
    outfile.close()
    write_file[dict_input['OutputFiletype']](outfile.name, result, dict_input)
    # outfile to URL
    outjson['out_url'] = impex_cfg.get('fmi', 'httpoutput') + os.path.basename(outfile.name)
    return outjson
def getFieldLine(dict_input):
    pass
def getDataPointValue_spacecraft(dict_input):
    pass
def getDataPointSpectra(dict_input):
    pass
def getSurface(dict_input):
    pass
def getFileURL(dict_input):
    pass
def getDataPointSpectra_spacecraft(dict_input):
    pass
def getParticleTrajectory(dict_input):
    pass

if __name__ == '__main__':# Load the data that PHP sent us

    try:
        data = json.loads(sys.argv[1])
    except:
        print('ERROR: not appropriate json input.')
        sys.exit(1)

    # dict of which functions call what
    functions = {'getDataPointValue': getDataPointValue,
                 'getFieldLine': getFieldLine,
                 'getDataPointValue_spacecraft': getDataPointValue_spacecraft,
                 'getDataPointSpectra': getDataPointSpectra,
                 'getSurface': getSurface,
                 'getFileURL': getFileURL,
                 'getDataPointSpectra_spacecraft': getDataPointSpectra_spacecraft,
                 'getParticleTrajectory': getParticleTrajectory}

    # parse the data object to the right function
    try:
        fileout = functions[data['function']](data)
    except:
        print('ERROR: Function not recognized')
        sys.exit(1)
    
    # Generate some data to send to PHP
    #result = {'fileout': fileout}

    # Send it to stdout (to PHP)
    print json.dumps(fileout)

