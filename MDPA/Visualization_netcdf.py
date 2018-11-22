#!/usr/local/Cellar/python@2/2.7.14_3/bin/python2.7

# Input is filename followed by names of axes (i.e. q frequency Sqw-total) from netcdf file

import matplotlib.pyplot as plt
from matplotlib import cm
import os.path as pth
from Scientific.IO.NetCDF import *
import numpy as np

def read_netcdf(fname):
    file = NetCDFFile(fname)
    var_dict = {var:file.variables[var] for var in file.variables}

    return var_dict

def genplot(params,color=[0,0,0]):
#Change to try except
    if len(params) == 2:
        plot2d(params,color)
    elif len(params) == 3:
        plot3d(params)
    else:
        print ("Number of parameters must be two or three")
        raise IndexError

def plot3d(params, save=None):

    """
    save - string specifying a filename
    """

    from mpl_toolkits.mplot3d import axes3d

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = expand("x",params[0],len(params[1]))
    y = expand("y",params[1],len(params[0]))
    z = np.array(params[2])

    #ax.set_zlim3d(0,1e-3)

    # Coloured wireframe using surface
    #colours = cm.coolwarm(z)
    #rcount, ccount, _ = colours.shape
    #surf_plot = ax.plot_surface(x, y, z, rcount=rcount, ccount=ccount, facecolors=colours, shade=False)
    #surf_plot.set_facecolor((0,0,0,0))

    ax.plot_wireframe(x,y,z)

    # label axes
    if __name__ == "__main__":
        ax.set_xlabel(sys.argv[2])
        ax.set_ylabel(sys.argv[3])
        ax.set_zlabel(sys.argv[4])

    if save:
        plt.savefig(save, format='png')

def plot2d(params,color):
    plt.plot(params[0],params[1],c=color)

    # plt.legend()
    # plt.xlabel("r (A)")
    # plt.ylabel("Total DISF (arb)")
    # plt.axis([0,10,0,3])
    # plt.minorticks_on()
    # plt.rc('legend',fontsize=16)

def expand(xy,var,length):
    if xy == "x":
        x = np.array([[i]*length for i in var])
        x.shape = (len(var),length)
        return x
    elif xy == "y":
        y = np.array([var] * length)
        y.shape = (length,len(var))
        return y

def main(filename,params):
    var_dict = read_netcdf(filename)
    genplot([var_dict.get(param)[:] for param in params])
    plt.show()

if __name__ == "__main__":
    import sys
    main(sys.argv[1],sys.argv[2:])
