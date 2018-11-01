# A module for reading, parsing and plotting LAMMPS fix ave/time and log file
# output

import matplotlib.pyplot as plt
import numpy as np

def open_file(file_name):

    """
    Opens LAMMPS fix ave/time or log file

    Arguments:
    file_name - string specifying path and filename

    Returns:
    file
    """

    return open(file_name, 'r')


def parse(file, log=True, equilibration=True):

    """
    Parses LAMMPS fix ave/time and log files

    Arguments:
    file - an open file

    Returns:
    dictionary of string:NumPy array pairs where string specifies the variable
    name and the array contains its values
    """

    if log:
        ln = ''
        while 'Per MPI rank memory allocation' not in ln:
            ln = file.readline()

        if equilibration:
            ln = ''
            while 'Per MPI rank memory allocation' not in ln:
                ln = file.readline()

    else:
        # Dispose of meaningless first header
        file.readline()

    header = file.readline().split()
    return parse_data(file, header, log)


def parse_data(file, header, log=True):

    if log:
        data = []
        while True:
            ln = file.readline()
            if 'Loop time of' in ln:
                break
            data.append(ln.split())
    else:
        data = [ln.split() for ln in file.readlines()]

    data = np.transpose(np.array(data).astype(np.float))

    data_dict = {}
    if log:
        start_i = sub = 0
    else:
        start_i = sub = 1

    for i in range(start_i, len(header)):
        data_dict[header[i]] = data[i-sub]

    return data_dict


def read(file_name, log=True, equilibration=True):

    """
    Convenience function which performs both open and parse

    Arguments:
    file_name - string specifying path and filename

    Returns:
    dictionary of string:NumPy array pairs where string specifies the variable
    name and the array contains its values
    """

    file = open_file(file_name)
    data = parse(file, log, equilibration)
    file.close()
    return data


def plot(x, y):

    """
    Uses matplotlib to produce a plot of the ave/time data

    Arguments:
    x - an array of independent variables
    y - an array of dependent variables

    """

    plt.plot(x,y)
    plt.show()


def setup_argparser():

    """
    Creates the argument parser for command line aerguments
    """

    import argparse

    argparser = argparse.ArgumentParser(description='Reads LAMMPS log and'
                                        ' ave/time output, calculates mean and'
                                        ' standard deviation for variables and'
                                        ' writes them to a file. VISUAL'
                                        ' INSPECTION OF THE GRAPHS IS ALWAYS'
                                        ' RECOMMENDED.')

    argparser.add_argument('-i', '--in', type=str, nargs='?',
                           default='log.lammps', help='the path and filename of'
                           ' the input file')
    argparser.add_argument('-a', '--ave_time', action='store_false',
                           default=True, help='Defines if input is log file or'
                           ' ave/time files')
    argparser.add_argument('-o', '--out', type=str, nargs='?',
                           default='var_stats.out', help='the path and filename'
                           ' of the output file, excluding the extention. THIS'
                           'WRITES OVER EXISTING FILES WITH THIS NAME AND .val'
                           'EXTENSION')
    argparser.add_argument('-x', '--exclude', type=str, nargs='*', help='a list'
                           ' of strings specifying any variables to be excluded'
                           ' from calculations and output, e.g. Steps')
    argparser.add_argument('-p', '--plots', action='store_true',
                           default=False, help='outputs a plot of mean'
                           ' and standard deviation for each variable')

    return argparser


def main(opts):


    """
    Arguments:
    opts - A dictionary of options
    """
    from block_analysis import blockAverage



    if not opts['plots']:
        plotFileName = None

    log = read(opts['in'], log=opts['ave_time'])

    # Empty file if it exists
    outFileName = opts['out']+'.val'
    with open(outFileName, 'w') as file:
        file.close()

    # Sort the keys alphabetically
    for k in sorted(log.keys(), key=str.lower):
        if k not in opts['exclude']:
            if opts['plots']:
                plotFileName = k
            value_err = blockAverage(log[k],
                                     showPlot=False,
                                     plotFileName=plotFileName,
                                     varName = k,
                                     returnSimple=True)
            with open(outFileName, 'a') as file:
                file.write(value_err + '\n')



if __name__ == '__main__':

    """
    Command line arguments are shown with a -h flag
    """

    argparser = setup_argparser()
    args = vars(argparser.parse_args())
    main(args)
