import numpy as np
import subprocess
from itertools import izip

class HCpy(object):
    def __init__(self, filename):
        self.filename = filename
        self.header = self._read(filename)
        self.hcdict = self._parseheader(self.header)
        limits = ['xmin0','xmax0', 'xmin1', 'xmax1', 'xmin2', 'xmax2']
        self.box = np.array([float(self.hcdict[x]) for x in limits]). \
                   reshape(3,2)
        self.variables = self._extractvariables(filename)

    def _read(self, filename):
        hcfile = open(filename, 'r')
        header = []
        line = ''
        while line != 'eoh\n':
            line = hcfile.readline()
            header.append(line)
        hcfile.close()
        headernew = [line.rstrip('\n') for line in header]
        return headernew[:-1]

    def _parseheader(self, header):
        # remove comments
        header_nocomm = [elem for elem in header if elem[0] != '#']
        g = lambda line: line.replace(' ','').split('=')
        return {g(line)[0]: g(line)[1] for line in header_nocomm}
        
    def _extractvariables(self, filename):
        cmd = 'hcintpol ' + filename
        # Execute the hc command with just an empty string 
        hc_in = subprocess.Popen(cmd, shell=True, 
                                 stdout=subprocess.PIPE, 
                                 stdin=subprocess.PIPE)
        variables, error = hc_in.communicate('\n')
        try:
            variables_list = variables[1:].split()
        except:
            print('something went wrong calling hcintpol')
            raise
        return variables_list[3:]


    def hcintpol(self, x, y, z, variables=None, linear=True):
        '''
        x,y,z needs to be a list of numbers, not other type
        variables need to be a list too
        '''
        cmd = 'hcintpol ' #Note, hcintpol needs to be in the path!
        if linear:
            cmd += ' -z '
        if variables is not None:
            cmd += ' -v '+ ','.join(variables)
        cmd += ' ' + self.filename

        # Coordinates single or multiple values
        coordinates = ''
        # check whether a list as input
        try:
            for i,j,k in izip(x, y, z):
                coordinates += '{0:e} {1:e} {2:e}\n'.format(i, j, k)
        except TypeError:
            print('inputs x,y and z need to be a list\n')
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
                for i,var in enumerate(variables_list):
                    variables_out[var].append(float(values[i]))

        return variables_out

        pass
