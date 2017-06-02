"""
This is a script to make slope-area plots of channels using the data
from the chi mapping tool.

It creates a separate plot for each basin, and the points are coloured by the
source node.

At the moment it uses the raw data - will also work on scripts for the binned data.

FJC
02/06/16
"""

import numpy as np
import LSDPlottingTools as LSDP
import matplotlib.pyplot as plt

def MakeRawSlopeAreaPlot(DataDirectory, DEM_prefix, FigFormat = 'show',
                         size_format = 'ESURF'):
    """
    This function makes a slope-area plot based on the raw data, using the
    channel file generated from the chi mapping tool (ends in the extension
    "_SAvertical.csv".)  It has a separate plot for each basin and colour codes
    the points by source node so different tributaries can be identified.

    Args:
        DataDirectory (str): the path to the directory with the csv file
        DEM_prefix (str): name of your DEM without extension
        FigFormat (str): The format of the figure. Usually 'png' or 'pdf'. If "show" then it calls the matplotlib show() command.
        size_format (str): Can be "big" (16 inches wide), "geomorphology" (6.25 inches wide), or "ESURF" (4.92 inches wide) (defualt esurf).

    Returns:
        Slope-area plot for each basin

    Author: FJC
    """
    from LSDPlottingTools import LSDMap_PointTools as PointTools

    # read in the csv file
    chi_csv_fname = DataDirectory+DEM_prefix+'_SAvertical.csv'
    print("I'm reading in the csv file "+chi_csv_fname)

    # get the point data object
    thisPointData = PointTools.LSDMap_PointData(chi_csv_fname)

    # get the basin keys
    basin = thisPointData.QueryData('basin_key')
    basin = [int(x) for x in basin]
    Basin = np.asarray(basin)
    basin_keys = np.unique(Basin)
    print('There are %s basins') %(len(basin_keys))

    for basin_key in basin_keys:
        FileName = DEM_prefix+'_SA_plot_basin%s.%s' %(str(basin_key),FigFormat)
        LSDP.LSDMap_ChiPlotting.SlopeAreaPlot(thisPointData, DataDirectory, FigFileName=FileName, FigFormat=FigFormat, size_format=size_format, basin_key=basin_key)

if __name__ == "__main__":
    MakeRawSlopeAreaPlot(DataDirectory='/home/s0923330/DEMs_for_analysis/mid_bailey_run_10m/', DEM_prefix='bailey_dem_10m', FigFormat='png')
