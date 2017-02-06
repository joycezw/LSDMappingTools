# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 20:53:58 2017

Example of how to use the Swath profile plotter
to plot longitudinal swaths along channels 
from LSDSwathTools.

@author: dav
"""

import matplotlib.pyplot as plt
from LSDPlottingTools.LSDMap_BasicPlotting \
        import MultiLongitudinalSwathAnalysisPlot, init_plotting_DV

init_plotting_DV()

data_dir = "/mnt/SCRATCH/Analyses/HydrogeomorphPaper/SwathProfile/Swath_secondVisit/Ryedale/"
file_single = "RyedaleElevDiff_GRIDDED_TLIM_long_profile.txt"
file_wildcard = "*ElevDiff_*_TLIM_long_profile.txt"

#plot_swath_profile(file_single + data_dir)
plt.rcParams['lines.linewidth'] = 1.5

MultiLongitudinalSwathAnalysisPlot(data_dir, file_wildcard)