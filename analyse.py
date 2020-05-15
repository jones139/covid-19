#!/usr/bin/env python
import argparse
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

latestDataFname = "latestData.xlsx"

authoritiesLst = [
    "E06000001", #"Hartlepool",
    "E06000002", #"Middlesbrough",
    "E06000003", #"Redcar and Cleveland",
    "E06000004", #"Stockton-on-Tees",
    "E06000005", #"Darlington",
    "E06000047", #"County Durham",
    "E08000024", # Sunderland
    #"E09000022", # Lambeth (for comparison)
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
    dfRoll = df.rolling(rolling_window).mean()
    #print(df.filter(authLst).tail(),dfRoll.filter(authLst).tail())
    dfDiff = df.diff(axis=0)
    dfDiffRoll = dfDiff.rolling(rolling_window).mean()

    fig, axes = plt.subplots(nrows=3, ncols=1,figsize=(7,12))
    df.plot(ax=axes[0],
            y=authLst,
            grid=True,
            title="Confirmed Cases\nRaw Data")

    dfDiff.plot(y=authLst,
                grid=True,
                ax=axes[1],
                title="Confirmed Cases Per Day\nRaw Data"

    )    

    dfDiffRoll.plot(ax=axes[2], y=authLst, grid=True,
                    title="%s Rolling Average Confirmed Cases Per Day\nRaw Data" % rolling_window
)
    axes[2].set_prop_cycle(None)
    #dfDiff.plot(y=authLst,
    #            grid=True,
    #            ax=axes[2],
    #            marker="+",
    #            style=".",
    #)
    legendLst = getLegendLst(authLst)
    axes[0].legend(legendLst)
    axes[0].set_ylabel("Cumulative Cases")
    axes[1].legend(legendLst)
    axes[1].set_ylabel("Cases per Day")
    axes[2].legend(legendLst)
    axes[2].set_ylabel("Cases per Day")
    plt.tight_layout()
    fig.savefig(chartFname)


def plotNormalisedAuthorityData(df, authLst, chartFname="chart2.png",
                                rolling_window='5d'):
    seriesLst = []
    dfPop = loadPopulationData()
    for auth in authLst:
        seriesLst.append("%s_corr" % auth)
    # Add normalised data for England for comparison.
    seriesLst.append("%s_corr" % "E92000001")
    print(seriesLst)

    dfRoll = df.rolling(rolling_window).mean()
    dfDiff = df.diff(axis=0)
    dfDiffRoll = dfDiff.rolling(rolling_window).mean()

    fig, axes = plt.subplots(nrows=3, ncols=1,figsize=(7,12))
    df.plot(ax=axes[0],
            y=seriesLst,
            grid=True,
            title="Confirmed Cases\nNormalised Data (cases per 100k population)")

    dfDiff.plot(y=seriesLst,
                grid=True,
                ax=axes[1],
                title="Confirmed Cases Per Day\nNormalised Data (cases per 100k population)"
    )    

    dfDiffRoll.plot(ax=axes[2], y=seriesLst, grid=True,
                        title="%s Rolling Average Confirmed Cases Per Day\nNormalised Data (cases per 100k population)" % rolling_window
)
    # Highlight the first series
    axes[2].set_prop_cycle(None)
    dfDiffRoll.plot(ax=axes[2], y=seriesLst[0], linewidth=4, grid=True)
    #dfDiff.plot(y=seriesLst, grid=True, ax=axes[2], marker="+", style=".")

    authLstExtended = authLst.append("E92000001")
    legendLst = getLegendLst(authLst)
    axes[0].legend(legendLst)
    axes[0].set_ylabel("Cumulative Cases")
    axes[1].legend(legendLst)
    axes[1].set_ylabel("Cases per Day")
    axes[2].legend(legendLst)
    axes[2].set_ylabel("Cases per Day")
    plt.tight_layout()
    fig.savefig(chartFname)


def plotFit(df,authName, chartFname="chart3.png"):
    """ plots data for a single authority with a simple exponential fit for comparison"""
    print("plotFit - authName=%s" % authName)
    dfSlice = df[authName]
    print(dfSlice)


def loadFile2(fname):
    """ Reads a new style (16apr2020) coronavirus-cases.csv file
    which is a long list of data, and converts it into a dataframe
    with each date as a row, and columns for each authority/region in
    the file.
    """
    print("loadFile2(%s)" % fname)
    dflist = pd.read_csv(fname)
    areaTypes = ['Upper tier local authority', 'Region', 'Nation']
    dflist = dflist.loc[dflist['Area type'].isin(areaTypes)]
    df = dflist.pivot(index="Specimen date",
                      columns = "Area code",
                      values = "Cumulative lab-confirmed cases")

    # Convert index from object to datetime
    df.index = pd.to_datetime(df.index)
    #print(df.index)

    # Fill the missing data with the previous day's number
    #print(df[authoritiesLst[0]])
    df = df.fillna(method='ffill', axis=0)
    #print(df[authoritiesLst[0]])

    dfPop = loadPopulationData()
    for auth in df.columns:
        pop = dfPop.query('Code=="%s"' % auth)['All ages']
        corr = float(100000./pop)
        df['%s_corr' % auth] = df[auth]*corr #.multiply(corr)



    return df
    
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

    
