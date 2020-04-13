#!/usr/bin/env python
import argparse
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

latestDataFname = "latestData.xlsx"

authoritiesLst = [
    "E06000001", #"Hartlepool",
    "E06000002", #"Middlesbrough",
    "E06000003", #"Redcar and Cleveland",
    "E06000004", #"Stockton-on-Tees",
    "E06000005", #"Darlington",
    "E06000047", #"County Durham",
    "E08000024", # Sunderland
    "E09000022", # Lambeth (for comparison)
    #"Bournemouth, Christchurch and Poole"
]

def getLegendLst(authLst):
    legendLst = []
    dfPop = loadPopulationData()
    for auth in authLst:
        authName = str(dfPop.query('Code=="%s"' % auth)['Name'].values[0])
        legendLst.append(authName)
    return legendLst

def plotAuthorityData(df,authLst,chartFname="chart1.png",
                      rolling_window='5d'):
    """ Plots a graph of the data in df for authority authName 
    Plots a rolling average of the actual data as a line.  Default width
       of rolling average window is 1 day, which amounts to the raw data."""
    fig, axes = plt.subplots(nrows=2, ncols=1,figsize=(5,8))
    dfRoll = df.rolling(rolling_window).mean()
    print(df.filter(authLst).tail(),dfRoll.filter(authLst).tail())
    df.plot(ax=axes[0],
            #style=".",        
            y=authLst,
            #marker="+",
            grid=True,
            title="Confirmed Cases\nRaw Data")
    #dfRoll.plot(ax=axes[0], y=authLst)
    dfDiff = df.diff(axis=0)
    dfDiffRoll = dfDiff.rolling(rolling_window).mean()
    dfDiff.plot(y=authLst,
                grid=True,
                ax=axes[1],
                marker="+",
                style="."
    )
    axes[1].set_prop_cycle(None)
    dfDiffRoll.plot(ax=axes[1], y=authLst)
    legendLst = getLegendLst(authLst)
    axes[0].legend(legendLst)
    axes[0].set_ylabel("Cumulative Cases")
    axes[1].legend(legendLst)
    axes[1].set_ylabel("Cases per Day\n(with %s rolling average)" % rolling_window)
    plt.tight_layout()
    fig.savefig(chartFname)


def plotNormalisedAuthorityData(df, authLst, chartFname="chart2.png",
                                rolling_window='5d'):
    seriesLst = []
    dfPop = loadPopulationData()
    for auth in authLst:
        seriesLst.append("%s_corr" % auth)
    dfRoll = df.rolling(rolling_window).mean()
    fig, axes = plt.subplots(nrows=2, ncols=1,figsize=(5,8))

    df.plot(ax=axes[0],
            y=seriesLst,
            grid=True,
            title="Confirmed Cases\nCorrected Data (cases per 100k population)")
    dfDiff = df.diff(axis=0)
    dfDiffRoll = dfDiff.rolling(rolling_window).mean()
    dfDiff.plot(y=seriesLst, grid=True, ax=axes[1], marker="+", style=".")
    axes[1].set_prop_cycle(None)
    dfDiffRoll.plot(ax=axes[1], y=seriesLst)

    legendLst = getLegendLst(authLst)
    axes[0].legend(legendLst)
    axes[0].set_ylabel("Cumulative Cases")
    axes[1].legend(legendLst)
    axes[1].set_ylabel("Cases per Day\n(with %s rolling average)" % rolling_window)
    plt.tight_layout()
    fig.savefig(chartFname)


def plotFit(df,authName, chartFname="chart3.png"):
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
    df=df.drop(columns=["Area Name",
    #                    "NHS region",
    #                    "Region (Government) "
    ])
    colNames = list(df.iloc[:,0]) # Authority Codes
    dft = df.transpose()
    dft.columns = colNames
    dft=dft.drop(index=["Area Code"]) # Drop the first row which is authority names
    dft=dft.drop(columns=["Unconfirmed"])

    dfPop = loadPopulationData()
    # Convert datatypes from 'object' to numeric values.
    for auth in dft.columns:
        pop = dfPop.query('Code=="%s"' % auth)['All ages']
        corr = float(100000./pop)
        dft['%s_corr' % auth] = dft[auth]*corr #.multiply(corr)

    # Convert index from object to datetime
    dft.index = pd.to_datetime(dft.index)
    return dft

def loadPopulationData():
    df = pd.read_excel("populations.xlsx", sheet_name='MYE2-All', header=4)
    return df[['Code','Name','All ages']]
    

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

    plotAuthorityData(df,authoritiesLst)
    plotNormalisedAuthorityData(df,authoritiesLst)
    #plotFit(df,"Hartlepool")


    # Get the most recent data, and filter it to only view the
    # corrected values for each authority.
    dfCurrent = df.iloc[-1,:]
    print(dfCurrent.sort_values().filter(like='_corr', axis=0))

    
