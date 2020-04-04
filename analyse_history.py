#!/usr/bin/env python
import argparse
import pandas as pd


latestDataFname = "latestData.xlsx"

authoritiesLst = [
    "Hartlepool",
    "Middlesbrough",
    "Redcar and Cleveland",
    "Stockton-on-Tees",
    "Darlington",
    "County Durham",
    #"Bournemouth, Christchurch and Poole"
]

def plotAuthorityData(df,authNames,chartFname="chart.png"):
    """ Plots a graph of the data in df for authority authName """
    print("plotAuthorityData(%s)" % authNames)
    ax = df.plot(y=authNames)
    ax.figure.savefig(chartFname)

def plotFit(df,authName, chartFname="chart2.png"):
    """ plots data for a single authority with a simple exponential fit for comparison"""
    print("plotFit - authName=%s" % authName)
    dfSlice = df[authName]
    print(dfSlice)

def loadFile(fname):
    """ Reads the dasboard excel file fname and convert it into a dataframe
    which is returned.
    """
    print("loadFile(%s)" % fname)
    df = pd.read_excel(fname, sheet_name='UTLAs', header=7)
    #latestDate=(df.iloc[-1][0]).date()
    df=df.drop(columns=["Area Code","NHS region", "Region (Governement) "])
    #print(df.head())
    #print(df.describe())
    colNames = list(df.iloc[:,0]) # Authority Names
    dft = df.transpose()
    dft.columns = colNames
    dft=dft.drop(index=["Area Name"]) # Drop the first row which is authority names
    #print(dft.head())
    #print(dft.describe())

    return dft

if (__name__ == "__main__"):
    print("main()")
    parser = argparse.ArgumentParser(description='analyse_history')
    parser.add_argument('--inFile', default=latestDataFname,
                        help='input filename')
    #parser.add_argument('--noMove', dest='noMove', action='store_true',
    #                    help="Do not move XY stage at all during measurement.")
    argsNamespace = parser.parse_args()
    args = vars(argsNamespace)
    print(args)
    inFname = args['inFile']

    print("inFname=%s" % inFname)

    df=loadFile(inFname)

    print(df)

    plotAuthorityData(df,authoritiesLst)
    plotFit(df,"Hartlepool")
