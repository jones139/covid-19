#!/usr/bin/env python
import argparse
import pandas as pd


latestDataFname = "latestData.xlsx"

authoritiesLst = [
    "E06000001", #"Hartlepool",
    "E06000002", #"Middlesbrough",
    "E06000003", #"Redcar and Cleveland",
    "E06000004", #"Stockton-on-Tees",
    "E06000005", #"Darlington",
    "E06000047", #"County Durham",
    #"Bournemouth, Christchurch and Poole"
]

def getLegendLst(authLst):
    legendLst = []
    dfPop = loadPopulationData()
    for auth in authLst:
        authName = str(dfPop.query('Code=="%s"' % auth)['Name'].values[0])
        legendLst.append(authName)
    return legendLst

def plotAuthorityData(df,authLst,chartFname="chart.png"):
    """ Plots a graph of the data in df for authority authName """
    #print("plotAuthorityData(%s)" % authLst)
    ax = df.plot(y=authLst, grid=True, title="Confirmed Cases - Raw Data")
    legendLst = getLegendLst(authLst)
    ax.legend(legendLst)
    ax.figure.savefig(chartFname)

def plotNormalisedAuthorityData(df, authLst, chartFname="chart2.png"):
    #print(df.describe(),df.dtypes,df.head())
    seriesLst = []
    legendLst = []
    dfPop = loadPopulationData()
    #print(dfPop.head())
    for auth in authLst:
        seriesLst.append("%s_corr" % auth)

    ax = df.plot(y=seriesLst, grid=True, title="Confirmed Cases - Corrected Data (cases per 100k population)")
    legendLst = getLegendLst(authLst)
    ax.legend(legendLst)
    ax.figure.savefig(chartFname)


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
    #latestDate=(df.iloc[-1][0]).date()
    df=df.drop(columns=["Area Name","NHS region", "Region (Governement) "])
    colNames = list(df.iloc[:,0]) # Authority Codes
    dft = df.transpose()
    dft.columns = colNames
    dft=dft.drop(index=["Area Code"]) # Drop the first row which is authority names
    dft=dft.drop(columns=["Unconfirmed"])

    dfPop = loadPopulationData()
    # Convert datatypes from 'object' to numeric values.
    for auth in dft.columns:
        #dft[auth] = pd.to_numeric(dft[auth])
        pop = dfPop.query('Code=="%s"' % auth)['All ages']
        #print("Auth=%s, pop=%.0f," % (auth,pop))
        corr = float(100000./pop)
        #print("Auth=%s, pop=%.0f, corr=%f" % (auth,pop,corr))
        #print(df[auth])
        dft['%s_corr' % auth] = dft[auth]*corr #.multiply(corr)
    
    #print(dft.head())
    #print(dft.describe())

    


    return dft

def loadPopulationData():
    df = pd.read_excel("populations.xlsx", sheet_name='MYE2-All', header=4)
    #latestDate=(df.iloc[-1][0]).date()
    #df=df.drop(columns=["Code"])
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

    #print(df)

    plotAuthorityData(df,authoritiesLst)
    plotNormalisedAuthorityData(df,authoritiesLst)
    #plotFit(df,"Hartlepool")
