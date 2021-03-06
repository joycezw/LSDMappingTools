#=============================================================================
# Runs visulisation on each sensitivity test for the MLE collinearity analysis.
#
# Authors:
#     Fiona J. Clubb
#=============================================================================
#=============================================================================
# IMPORT MODULES
#=============================================================================
# set backend to run on server
import matplotlib
matplotlib.use('Agg')

#from __future__ import print_function
import sys
import os
from LSDPlottingTools import LSDMap_MOverNPlotting as MN
from LSDMapFigure import PlottingHelpers as Helper
from LSDPlottingTools import LSDMap_SAPlotting as SA

#=============================================================================
# This is just a welcome screen that is displayed if no arguments are provided.
#=============================================================================
def print_welcome():

    print("\n\n=======================================================================")
    print("Hello! I'm going to plot the MLE sensitivity results for you.")
    print("You will need to tell me which directory to look in.")
    print("Use the -dir flag to define the working directory.")
    print("If you don't do this I will assume the data is in the same directory as this script.")
    print("For help type:")
    print("   python MLESensitivity.py -h\n")
    print("=======================================================================\n\n ")

#=============================================================================
# This is the main function that runs the whole thing
#=============================================================================
def main(argv):

    # If there are no arguments, send to the welcome screen
    if not len(sys.argv) > 1:
        full_paramfile = print_welcome()
        sys.exit()

    # Get the arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--base_directory", type=str, help="The base directory with the MLE analyses. If this isn't defined I'll assume it's the same as the current directory.")
    parser.add_argument("-fname", "--fname_prefix", type=str, help="The prefix of your DEM WITHOUT EXTENSION!!! This must be supplied or you will get an error.")
    # What sort of analyses you want
    parser.add_argument("-PR", "--plot_rasters", type=bool, default=False, help="If this is true, I'll make raster plots of the m/n value and basin keys")
    parser.add_argument("-chi", "--plot_basic_chi", type=bool, default=False, help="If this is true I'll make basin chi plots for each basin coloured by elevation.")
    parser.add_argument("-PC", "--plot_chi_profiles", type=bool, default=False, help="If this is true, I'll make chi-elevation plots for each basin coloured by the MLE")
    parser.add_argument("-K", "--plot_chi_by_K", type=bool, default=False, help="If this is true, I'll make chi-elevation plots for each basin coloured by K. NOTE - you MUST have a column in your chi csv with the K value or this will break!")
    parser.add_argument("-pcbl", "--plot_chi_by_lith", type=bool, default=False, help="If this is true, I'll make chi-elevation plots for each basin coloured by litho. NOTE - you MUST have a column in your chi csv with the K value or this will break!")
    parser.add_argument("-PO", "--plot_outliers", type=bool, default=False, help="If this is true, I'll make chi-elevation plots with the outliers removed")
    parser.add_argument("-MLE", "--plot_MLE_movern", type=bool, default=False, help="If this is true, I'll make a plot of the MLE values for each m/n showing how the MLE values change as you remove the tributaries")
    parser.add_argument("-SA", "--plot_SA_data", type=bool, default=False, help="If this is true, I'll make a plot of the MLE values for each m/n showing how the MLE values change as you remove the tributaries")
    parser.add_argument("-MCMC", "--plot_MCMC", type=bool, default=False, help="If this is true, I'll make a plot of the MCMC analysis. Specify which basins you want with the -basin_keys flag.")
    parser.add_argument("-pts", "--point_uncertainty", type=bool, default=False, help="If this is true, I'll make a plot of the range in m/n from the MC points analysis")
    parser.add_argument("-hist", "--plot_histogram", type=bool, default=False, help="If this is true, I'll make plots of the pdfs of m/n values for each method.")
    # parser.add_argument("-basin_joyplot", "--basin_joyplot", type=bool, default=False, help="If this is true, I'll make a joyplot showing m/n for each basin from the chi points")
    parser.add_argument("-SUM", "--plot_summary", type=bool, default=False, help="If this is true, I'll make the summary CSV file and plot of the best fit m/n from each of the methods.")
    parser.add_argument("-ALL", "--all_movern_estimates", type=bool, default=False, help="If this is true, I'll make all the plots")

    # Plotting options
    parser.add_argument("-points", "--point_analysis", type=bool, default=False, help="If this is true then I'll assume that you're running the MLE analysis using the point method. Default = False")
    parser.add_argument("-show_SA_raw", "--show_SA_raw", type=bool, default=True, help="Show the raw S-A data in background of SA plot. Default = True")
    parser.add_argument("-show_SA_segments", "--show_SA_segments", type=bool, default=False, help="Show the segmented S-A data in SA plot. Default = False")
    parser.add_argument("-test_SA_regression", "--test_SA_regression", type=bool, default=False, help="If this is true I'll print the regression stats for the slope area plots.")
    parser.add_argument("-show_legend", "--show_legend", type=bool, default=True, help="If this is true, I'll display the legend for the SA plots.")

    parser.add_argument("-basin_keys", "--basin_keys",type=str,default = "", help = "This is a comma delimited string that gets the list of basins you want for the plotting. Default = no basins")

    # These control the format of your figures
    parser.add_argument("-fmt", "--FigFormat", type=str, default='png', help="Set the figure format for the plots. Default is png")
    parser.add_argument("-size", "--size_format", type=str, default='ESURF', help="Set the size format for the figure. Can be 'big' (16 inches wide), 'geomorphology' (6.25 inches wide), or 'ESURF' (4.92 inches wide) (defualt esurf).")
    parser.add_argument("-animate", "--animate", type=bool, default=True, help="If this is true I will create an animation of the chi plots. Must be used with the -PC flag set to True.")
    parser.add_argument("-keep_pngs", "--keep_pngs", type=bool, default=False, help="If this is true I will delete the png files when I animate the figures. Must be used with the -animate flag set to True.")
    args = parser.parse_args()

    if not args.fname_prefix:
        print("WARNING! You haven't supplied your DEM name. Please specify this with the flag '-fname'")
        sys.exit()

    # get the base directory
    if args.base_directory:
        Directory = args.base_directory
    else:
        Directory = os.getcwd()

    # check the basins
    print("You told me that the basin keys are: ")
    print(args.basin_keys)

    if len(args.basin_keys) == 0:
        print("No basins found, I will plot all of them")
        these_basin_keys = []
    else:
        these_basin_keys = [int(item) for item in args.basin_keys.split(',')]
        print("The basins I will plot are:")
        print(these_basin_keys)

    # get the range of moverns, needed for plotting
    BasinDF = Helper.ReadBasinStatsCSV(Directory+"/sigma_10/", args.fname_prefix)
    # we need the column headers
    columns = BasinDF.columns[BasinDF.columns.str.contains('m_over_n')].tolist()
    moverns = [float(x.split("=")[-1]) for x in columns]
    start_movern = moverns[0]
    n_movern = len(moverns)
    d_movern = (moverns[-1] - moverns[0])/(n_movern-1)

    # loop through each sub-directory with the sensitivity results
    MLE_str = "sigma_"
    for subdir, dirs, files in os.walk(Directory):
        for dir in dirs:
            if MLE_str in dir:
                this_dir = Directory+"/"+dir+'/'
                # make the plots depending on your choices
                # make the plots depending on your choices
                if args.plot_rasters:
                    MN.MakeRasterPlotsBasins(this_dir, args.fname_prefix, args.size_format, simple_format)
                    MN.MakeRasterPlotsMOverN(this_dir, args.fname_prefix, start_movern, n_movern, d_movern, size_format=args.size_format, FigFormat=simple_format)
                    MN.MakeRasterPlotsMOverN(this_dir, args.fname_prefix, start_movern, n_movern, d_movern, movern_method="Chi_points", size_format=args.size_format, FigFormat=simple_format)
                    MN.MakeRasterPlotsMOverN(this_dir, args.fname_prefix, start_movern, n_movern, d_movern, movern_method="SA", size_format=args.size_format, FigFormat=simple_format)
                if args.plot_basic_chi:
                    MN.MakePlotsWithMLEStats(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern)
                if args.plot_chi_profiles:
                    MN.MakeChiPlotsMLE(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, size_format=args.size_format, FigFormat = simple_format, animate=args.animate, keep_pngs=args.keep_pngs)
                if args.plot_chi_by_K:
                    MN.MakeChiPlotsColouredByK(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, size_format=args.size_format, FigFormat=simple_format, animate=args.animate, keep_pngs=args.keep_pngs)
                if args.plot_chi_by_lith:
                    MN.MakeChiPlotsColouredByLith(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, size_format=args.size_format, FigFormat=simple_format, animate=args.animate, keep_pngs=args.keep_pngs)
                if args.plot_outliers:
                    MN.PlotProfilesRemovingOutliers(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern)
                if args.plot_MLE_movern:
                    MN.PlotMLEWithMOverN(this_dir, args.fname_prefix,basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, size_format=args.size_format, FigFormat =simple_format)
                if args.plot_SA_data:
                    SA.SAPlotDriver(this_dir, args.fname_prefix, FigFormat = simple_format,size_format=args.size_format,
                                    show_raw = args.show_SA_raw, show_segments = args.show_SA_segments,basin_keys = these_basin_keys)
                if args.test_SA_regression:
                    #SA.TestSARegression(this_dir, args.fname_prefix)
                    SA.LinearRegressionRawDataByChannel(this_dir,args.fname_prefix, basin_list=these_basin_keys)
                    #SA.LinearRegressionSegmentedData(this_dir, args.fname_prefix, basin_list=these_basin_keys)
                if args.plot_MCMC:
                    MN.plot_MCMC_analysis(this_dir, args.fname_prefix,basin_list=these_basin_keys, FigFormat= simple_format, size_format=args.size_format)
                if args.point_uncertainty:
                    MN.PlotMCPointsUncertainty(this_dir, args.fname_prefix,basin_list=these_basin_keys, FigFormat=simple_format, size_format=args.size_format,start_movern=start_movern, d_movern=d_movern, n_movern=n_movern)
                if args.plot_histogram:
                    MN.MakeMOverNSummaryHistogram(this_dir, args.fname_prefix,basin_list=these_basin_keys,start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, FigFormat=simple_format, size_format=args.size_format, show_legend=args.show_legend)
                if args.plot_summary:
                    MN.CompareMOverNEstimatesAllMethods(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern)
                    MN.MakeMOverNSummaryPlot(this_dir, args.fname_prefix, basin_list=these_basin_keys,start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, FigFormat = simple_format,size_format=args.size_format, show_legend=args.show_legend)
                    MN.MakeMOverNPlotOneMethod(this_dir,args.fname_prefix,basin_list=these_basin_keys,start_movern=start_movern,d_movern=d_movern,n_movern=n_movern,FigFormat=args.FigFormat,size_format=args.size_format)
                # if args.basin_joyplot:
                #     MN.CompareMOverNEstimatesAllMethods(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern)
                #     MN.MakeBasinJoyplot(this_dir, args.fname_prefix, basin_list=these_basin_keys, FigFormat=simple_format, size_format=args.size_format)
                if args.all_movern_estimates:
                    # plot the rasters
                    MN.MakeRasterPlotsBasins(this_dir, args.fname_prefix, args.size_format, args.FigFormat)
                    MN.MakeRasterPlotsMOverN(this_dir, args.fname_prefix, start_movern, n_movern, d_movern, movern_method="Chi_full", size_format=args.size_format, FigFormat=args.FigFormat)
                    MN.MakeRasterPlotsMOverN(this_dir, args.fname_prefix, start_movern, n_movern, d_movern, movern_method="Chi_points", size_format=args.size_format, FigFormat=args.FigFormat)
                    MN.MakeRasterPlotsMOverN(this_dir, args.fname_prefix, start_movern, n_movern, d_movern, movern_method="SA", size_format=args.size_format, FigFormat=args.FigFormat)

                    # make the chi plots
                    MN.MakeChiPlotsMLE(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, size_format=args.size_format, FigFormat = args.FigFormat, animate=True, keep_pngs=True)

                    # make the SA plots
                    SA.SAPlotDriver(this_dir, args.fname_prefix, FigFormat = args.FigFormat,size_format=args.size_format,
                                    show_raw = args.show_SA_raw, show_segments = True, basin_keys = these_basin_keys)
                    SA.SAPlotDriver(this_dir, args.fname_prefix, FigFormat = args.FigFormat,size_format=args.size_format,
                                    show_raw = args.show_SA_raw, show_segments = False, basin_keys = these_basin_keys)

                    #summary plots
                    MN.CompareMOverNEstimatesAllMethods(this_dir, args.fname_prefix, basin_list=these_basin_keys, start_movern=start_movern, d_movern=d_movern, n_movern=n_movern)
                    MN.MakeMOverNSummaryPlot(this_dir, args.fname_prefix, basin_list=these_basin_keys,start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, FigFormat = args.FigFormat,size_format=args.size_format, show_legend=args.show_legend)
                    #joyplot
                    MN.MakeMOverNPlotOneMethod(this_dir,args.fname_prefix,basin_list=these_basin_keys,start_movern=start_movern,d_movern=d_movern,n_movern=n_movern,FigFormat=args.FigFormat,size_format=args.size_format)
                    MN.MakeMOverNSummaryHistogram(this_dir, args.fname_prefix,basin_list=these_basin_keys,start_movern=start_movern, d_movern=d_movern, n_movern=n_movern, FigFormat=args.FigFormat, size_format=args.size_format, show_legend=args.show_legend)

    # collate all the results to get the final figure
    MN.PlotSensitivityResultsSigma(Directory, args.fname_prefix,FigFormat=args.FigFormat,size_format=args.size_format,movern_method='points')

#=============================================================================
if __name__ == "__main__":
    main(sys.argv[1:])
