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
impex_cfg.read('fmi/code/fmi.cfg')  # Is there a way to don't parse the path this way?

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
            finalstring += key + ': ' + ','.join(query[key]) + ';\n '
        else:
            finalstring += key + ': ' + str(query[key]) + ';\n '
    
    finalstring += '}\n == Query executed on: ' + datetime.datetime.now().isoformat() + '==\n'
    return finalstring

def vot2points(filename):
    vot = votable.parse_single_table(filename, pedantic = False)
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

    # TODO, FIXME! This can be done in less lines!
    if points_d.has_key('line_00'):
        for key in sorted(points_d.keys()): # line_00, line_01, ...
            line = points_d[key]
            table = votable.tree.Table(vot)
            resource.tables.append(table)

            table.description = key  # line_00, ..

            var = sorted(line.keys())
            if time is None:
                var = var[-3:] + var[:-3]
            else:
                var = ['Time'] + var[-3:] + var[:-3]

            fields = [votable.tree.Field(votable, name=fields_props[v]['name'], datatype=fields_props[v]['type'], 
                                         arraysize=fields_props[v]['size'], unit=fields_props[v]['units'].to_string(), 
                                         ucd=fields_props[v]['ucd']) for v in var]
            table.fields.extend(fields)

            # points_d dict to array
            points_array = np.array([line[x] for x in var]).transpose()
            table.create_arrays(points_array.shape[0])
    
            if time is None:
                points_mask = np.ma.masked_array(points_array, mask = False)
                table.array = points_mask
            else:
                for i, line in enumerate(time):
                    table.array[i] = tuple(time[i]) + tuple(points_array[i, :])

    else:  # There are just the variables (not lines)
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

    # TODO, FIXME! This can be done in less lines!
    if points_d.has_key('line_00'):
        for key in sorted(points_d.keys()):  #line_00, line_01, ...
            dim = 'dim_' + key
            f.createDimension(dim, len(points_d[key]['x']))
            line = points_d[key]
            for coord in line.keys():  # x, y, z, ...
                key_n = f.createVariable(fields_props[coord]['name']+'_'+key, fields_props[coord]['type'],(dim,))
                key_n.units = fields_props[coord]['units'].to_string()
                key_n[:] = line[coord]
    else:
        dim = 'dim'
        f.createDimension(dim, len(points_d[points_d.keys()[0]]))
        for key in points_d.keys():
            key_n = f.createVariable(fields_props[key]['name'], fields_props[key]['type'],(dim,))
            key_n.units = fields_props[key]['units'].to_string()
            key_n[:] = points_d[key]
    f.close()

def _url2points(url):
    url_XYZ = url
    response = urllib2.urlopen(url_XYZ.replace('\\',''))
    votfile = StringIO.StringIO()
    votfile.write(response.read())
    return vot2points(votfile)

def _writeout(dict_input, values):
    # write in the fileformat requested
    write_file = {'votable': points2vot, 'netcdf': points2netcdf}
    # - Create file
    outfile = tempfile.NamedTemporaryFile(prefix = 'hwa_', dir = impex_cfg.get('fmi', 'diroutput'), suffix = '.'+dict_input['OutputFiletype'])
    outfile.close()
    write_file[dict_input['OutputFiletype']](outfile.name, values, dict_input)
    return outfile.name

def _table2dict(table):
    '''
    It reads an array of lines with space separated values
    into a dictionary of the header variables
    '''
    for line in table:
        if (line[0] == '%') or (line[0] == '#'):
            variables_list = line[1:].split()
            variables_out = {var: [] for var in variables_list}
        else:  
            values = line.split()
            for i, var in enumerate(variables_list):
                variables_out[var].append(float(values[i]))
    return variables_out

def _writeout_ion(dict_input, resultfile):
    #read result file
    results = open(resultfile, 'r')     # TODO: If to do in a general way this should either get a stdout (eg., fieldline tracer)
    # Extracts {x:[...], y:[...], z:[...], pairID:[...]}
    variables = _table2dict(results.readlines())
    results.close()

    # number of ion paths
    # Each path has a number > 0.  So, we count these pairs > 0
    # (len(pairs) is always going to be larger than pairID)
    pairs = variables['parID']
    ind_paths = [l for l in range(1, len(pairs)) if pairs.count(l) > 0]
    ion_paths = len(ind_paths)# - ind_paths.count(0) (they are not already.)

    variables_lines = {'line_{:02d}'.format(x):{} for x in range(ion_paths)}
    line = 0
    for elem in ind_paths:
        if elem != 0: # It should never be == 0 after the condition added in ind_paths
            variables_lines['line_{:02d}'.format(line)]={l: [x for i,x in enumerate(variables[l]) if pairs[i] == elem] for l in ['x', 'y', 'z']}
            line += 1

    return _writeout(dict_input, variables_lines)
 

def iontracer_writecfg(dict_input, points):
    '''
    it writes the config file needed to run the iontracer routine with the 
    parameters set in the method. 
    points need to be a list of 3D points.
    NOTE: Defaults options are hardcoded, by now (though it should be easy to input)
    '''
    cfg = ''
    # HC file, relative mass, relative charge  
    #Note: iontracer allows more than one, for IMPEx we allow just one at a time.
    # check whether the mass and charge exists
    mass, charge = 1, 1
    if dict_input['properties'].has_key('mass'):
        mass = np.round(dict_input['properties'][0]['mass'])
    if dict_input['properties'].has_key('charge'):
        charge = np.round(dict_input['properties'][0]['charge'])

    cfg += "HCF {file} {mass:.0f} {charge:.0f}\n".format(file = dict_input['filename'].replace('\\',''),
                                                         mass = mass, 
                                                         charge = charge)  #FIXME!!!! it writes 0 and 0!!! for mass and charge

    cfg += 'FORMATS matlab\n' # This is a ASCII format which we know how to read...
    cfg += 'OUT_DIR /\n'     # This should create the file where the config file resides

    cfg += 'TRACEVARS parID\n'  # So we can tied each input point with it's number
    # Notice the pairs are numbered as: Odd for forward, Even for backwards, so if asks for just forward, then you would get for starting point A, B, C => 1, 3, 5 as IDs.

    cfg += 'BUNEMANVERSION U\n' # Default value when electron pressure is not included.
    # TODO: This could be define automatically if present on tree.xml file

    cfg += 'DIRECTION {direction}\n'.format(direction = dict_input['direction'].lower())
    
    if dict_input['maxsteps'] > 0:
        cfg += 'MAXSTEPS {steps:.0f}\n'.format(steps = dict_input['maxsteps'])
    
    if dict_input['stepsize'] > 0:
        cfg += 'STEPSIZE {stepsize:.3f}\n'.format(stepsize = dict_input['stepsize'])

    order = {'nearestgridpoint': 0, 'linear': 1}
    if dict_input['order'] != 'nearestgridpoint':
        dict_input['order'] = 'linear'
    cfg += 'INTPOLORDER {order:.0f}\n'.format(order = order[dict_input['order']])

    cfg += 'VERBOSE 0\n'
    
    cfg += 'OVERWRITE 1\n'

    cfg += 'ENDPOINTSONLY 0\n'

    cfg += 'PLANETARY_BOUNDARY {radius:.2f}\n'.format(radius = dict_input['stop_radius'])
    
    box_limits = [['XMIN', 0], ['YMIN', 2], ['ZMIN', 4], 
                  ['XMAX', 1], ['YMAX', 3], ['ZMAX', 5]]
    for elem in box_limits:
        cfg += '{label} {value:e}\n'.format(label = elem[0], value = float(dict_input['stop_box'][elem[1]])) 

    cfg += 'EOC\n'

    cfg += '########### INITIAL POINTS SECTION ###########\n'
    for stpoint in points:
        cfg += '{0[0]:e} {0[1]:e} {0[2]:e}\n'.format(stpoint)
        # TODO! initial v, mass and charge needs to be input
    
    # Create tempfile to write the configuration
    cfgfile = tempfile.NamedTemporaryFile(prefix = 'hwa_ion_', dir = impex_cfg.get('fmi', 'diroutput'), suffix = '.cfg', delete = False)
    cfgfile.write(cfg)
    cfgfile.close() # it does not delete the file because delete = False

    return cfgfile.name


def hcintpol(filename, x, y, z, variables=None, linear=True):
    '''
    x,y,z needs to be a list of numbers, not other type
    variables need to be a list too
    '''
    cmd = os.path.join(impex_cfg.get('fmi','bindir'),'hcintpol') 
    if not linear:
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
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    interpolatedvalues, error = hc_in.communicate(coordinates) 

    # Extract the values as a dictionary {var(x,y,z,rho): [values]}
    variables_out = _table2dict(interpolatedvalues.splitlines())
    return variables_out, error

def hcfieldline(filename, x, y, z, variables = None, radius = 0,
                stop_box = None, max_step = None, step_size = 1, 
                direction = 'Forward', linear=True):
    '''
    wrapper to call the ft function from hctools.
    x,y,z:
    variables: 
    '''

    cmd = os.path.join(impex_cfg.get('fmi', 'bindir'), 'ft')

    if not linear:
        cmd += ' -z '

    if direction.lower() == 'backward':
        cmd += ' -b '

    if radius != 0:
        cmd += ' -r {:f} '.format(radius)

    if (stop_box is not None):
        if (len(stop_box) == 6):
            cmd += ' -l ' + ','.join(str(x) for x in stop_box)
        else: 
            raise Exception('stop_box can just work with 6 values')
    
    if (max_step is not None):
        cmd += ' -ms {:d} '.format(max_step)

    if (step_size != 1):
        cmd += ' -ss {:f} '.format(step_size)

    cmd += variables # FixMe! This assumes a single variable!
    
    cmd += ' {0:f},{1:f},{2:f} '.format(x, y, z) # FixMe! This assumes a single starting point!
    
    cmd += ' ' + filename

    ft_in = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    fieldline, error = ft_in.communicate() 
             
    # Extract the 6 columns (coordinates and fields - x,y,z) into a dict
    variables_out = _table2dict(fieldline.splitlines())
    return variables_out, error


def getDataPointValue(dict_input):
    '''
    Executes the method with the same name.  The input has to be a dictionary
    with all the parameters needed, they are:
    -function: getDataPointValue
    -filename: filename (with path) to the requested ResourceID
    -variables: List of variables
    -url_XYZ: url address to the input data
    -IMFClockAngle: Not used here, yet.
    -InterpolationMethod: whether lineal or not
    -OutputFiletype: which kind (netcdf, votable)
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
    points = _url2points(dict_input['url_XYZ'])
    x, y, z = points[:,0], points[:,1], points[:, 2]

    # Run hcintpol with the the file, coordinates, var and intpol method
    filename = str(dict_input['filename'])
    result, hcerror = hcintpol(filename.replace('\\',''), 
                      x, y, z, 
                      variables=dict_input['variables'], 
                      linear=linear)
    if (len(result.keys()) < 4):
        outjson['error'] = 'ERROR: Unrecognized variable names \n hcintpol message:\n' + hcerror
        return outjson

    # parse hcerror/warnings to the savefile
    if (hcerror != ''):
        dict_input['hc_warnings'] = hcerror

    outname = _writeout(dict_input, result)
    # outfile to URL
    outjson['out_url'] = impex_cfg.get('fmi', 'httpoutput') + os.path.basename(outname)
    return outjson

def getFieldLine(dict_input):
    '''
    Executes the method with such name. The input needs to be a dictionary with 
    the following parameters:
    -function: getFieldLine
    -filename: filename (with path) to the requested ResourceID
    -variables: Variable desired to follow the fieldline #todo: what if more than one?
    -direction: Direction on how to follow the fieldline (forward or backward)
    -stepsize: Size of the step in m.
    -maxsteps: Maximum number of steps to follow the field.
    -stop_radius: Lower limit as radius in m on the simulation box.
    -stop_box: Edge limits as box coordinates in m: [x0, x1, y0, y1, z0, z1]
    -url_XYZ: url address to the input data
    -OutputFiletype: which kind (netcdf, votable)

    Attention, at the moment this works just for one variable and one initial point. 
    So, it returns just one fieldline.

    Attention, Default is linear interpolation.  If zeroth order required, then need to be implemented in the Method's input (php) and then here!
    '''

    #TODO: accept zeroth order interpolation?
    
    outjson = {'out_url':'', 'error':''}

    points = _url2points(dict_input['url_XYZ'])
    # Read starting point(s) #TODO: What happens when we get multiple starting points?
    x, y, z = points[:,0], points[:,1], points[:, 2]

    if (len(x) > 1):
        x, y, z = x[0], y[0], z[0] # fixme: we should be able to run multiple initial cond.

    # Run fieldline tracer with the the file, coordinates, var and intpol method
    filename = str(dict_input['filename'])
    result, hcerror = hcfieldline(filename.replace('\\',''),  #TODO: FIXME, check parms!
                                  x, y, z, 
                                  variables=dict_input['variables'], # fixme: what if we have mult vars?
                                  radius = dict_input['stop_radius'],
                                  stop_box = dict_input['stop_box'],
                                  max_step = dict_input['maxsteps'],
                                  step_size = dict_input['stepsize'],
                                  direction = dict_input['direction'],
                                  linear = True)
    # TODO! Any error message to stop execution? => outjson['error']

    # any other warnings:
    if (hcerror != ''):
        dict_input['hc_warnings'] = hcerror
        
    outname = _writeout(dict_input, result) #Fixme: if we want to provide multiple input points or variables this needs also to apply.
    outjson['out_url'] = impex_cfg.get('fmi', 'httpoutput') + os.path.basename(outname)

    return outjson

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
    '''
    Gets the particle trajectory for the properties set in the input dictionary.
    The following parameters are needed:
    -function: getParticleTrajectory
    -filename: filename (path included) to the requested ResourceID
    -direction: Direction on how to follow the particle trajectory (forward or backward)
    -stepsize: Size of steps in metres
    -maxsteps: Maximum number of steps to follow the particle
    -stop_radius: Lower limit as "planet boundary" in metres.
    -stop_box: Edge limits as box coordinates in m: [x0, x1, y0, y1, z0, z1]
    -order: whether linear or not (nearestgridpoint)
    -OutputFiletype: which kind (netcdf, votable)
    -url_XYZ: url address to the input data

    Attention, at the moment this is plan as single particle.
    '''

    outjson = {'out_url':'', 'error':''}

    # Get the points from votable
    points = _url2points(dict_input['url_XYZ'])

    # Write config file in a tmp file
    ## Define the outdir 
    cfgfilename = iontracer_writecfg(dict_input, points)

    # Execute program
    cmd = os.path.join(impex_cfg.get('fmi','bindir'),'iontracer')
    cmd += ' ' + cfgfilename
    iontracer = subprocess.Popen(cmd, shell=True,
                                 stderr=subprocess.PIPE)
    ion_ex, ion_error = iontracer.communicate()
    # What are the execution/error messages to check here?
    if (ion_error != ''):
        dict_input['ion_warnings'] = ion_error
    #FIXME!! Check whether the file was craeted and if it works;
    #FIXME!! iontracer does not return anything if points out of boundaries
    # "'Error: Some points go outside of the simulation box.\nCheck points in the point data or config file\n'"
    # Convert the output file to the required format
    outname = _writeout_ion(dict_input, cfgfilename + '_trace_0.m')
    outjson['out_url'] = impex_cfg.get('fmi', 'httpoutput') + os.path.basename(outname)
    return outjson

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

