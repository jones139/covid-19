#!/usr/bin/env python
import argparse
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

latestDataFname = "coronavirus-cases_latest.csv"

authoritiesLst = [
    "E06000001", #"Hartlepool",
    "E06000002", #"Middlesbrough",
    "E06000003", #"Redcar and Cleveland",
    "E06000004", #"Stockton-on-Tees",
    "E06000005", #"Darlington",
    "E06000047", #"County Durham",
    "E08000024", # Sunderland,
#    "E06000016", # Leicester,
#    "E08000032", # Bradford,
#    "E08000005", # Rochdale,
#    "E06000009", # Blackpool,
#    "E08000018", # Rotherham
    #"E09000022", # Lambeth (for comparison)
    #"Bournemouth, Christchurch and Poole"
]


class PopData():
    dfPop = None
    def __init__(self):
        df = pd.read_excel("populations.xlsx",
                           sheet_name='MYE2-All', header=4)
        self.dfPop =  df[['Code','Name','All ages']]

    def code2authName(self, authCode):
        authName = str(
            self.dfPop.query('Code=="%s"' % authCode)['Name'].values[0])
        return(authName)

    def getPop(self, authCode):
        pop = self.dfPop.query('Code=="%s"' % authCode)['All ages']
        return(pop)


class CovidAnalysis():
    popData = None
    dfRaw = None
    dfNorm = None

    def __init__(self, inFname, dropDays=2):
        #Fix problem with some axes labels being cut off the plots.
        matplotlib.rcParams.update({'figure.autolayout': True})
        self.popData = PopData()
        self.loadCsvFile(inFname, dropDays)
        print("CovidAnalysis.__init__ complete.")


    def loadCsvFile(self,fname, dropDays=2):
        """ Reads a new style (16apr2020) coronavirus-cases.csv file
        which is a long list of data, and converts it into a dataframe
        with each date as a row, and columns for each authority/region in
        the file.
        """
        print("loadCsvFile(%s)" % fname)

        # First process cases data using cumulative cases
        dflist = pd.read_csv(fname)
        areaTypes = ['ltla', 'region', 'nation']
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

        #Drop last 'dropDays' days of data, because they tend to be incomplete so are misleading
        df.drop(df.tail(dropDays).index, inplace=True)
        
        self.dfRaw = df.copy()

        # Normalise the data by population
        for auth in df.columns:
            pop = self.popData.getPop(auth)
            corr = float(100000./pop)
            df[auth] = df[auth]*corr
        self.dfNorm = df.copy()


        # Now process daily cases and daily deaths data - using only national
        # statistics so they are comparable.
        dflist = pd.read_csv(fname)
        areaTypes = ['nation']
        dflist = dflist.loc[dflist['Area type'].isin(areaTypes)]
        dfDailyCases = dflist.pivot(index="Specimen date",
                          columns = "Area code",
                          values = "Daily lab-confirmed cases")
        dfDailyDeaths = dflist.pivot(index="Specimen date",
                          columns = "Area code",
                          values = "newDeaths28DaysByDeathDate")

        # Convert index from object to datetime
        dfDailyCases.index = pd.to_datetime(dfDailyCases.index)
        dfDailyDeaths.index = pd.to_datetime(dfDailyDeaths.index)

        # Fill the missing data with the previous day's number
        dfDailyCases = dfDailyCases.fillna(method='ffill', axis=0)
        dfDailyDeaths = dfDailyDeaths.fillna(method='ffill', axis=0)

        #Drop last 'dropDays' days of data, because they tend to be incomplete so are misleading
        dfDailyCases.drop(dfDailyCases.tail(dropDays).index, inplace=True)
        dfDailyDeaths.drop(dfDailyDeaths.tail(dropDays).index, inplace=True)
        
        self.dfDailyCasesRaw = dfDailyCases.copy()
        self.dfDailyDeathsRaw = dfDailyDeaths.copy()

        # Normalise the data by population
        for auth in self.dfDailyCasesRaw.columns:
            pop = self.popData.getPop(auth)
            corr = float(100000./pop)
            dfDailyCases[auth] = dfDailyCases[auth]*corr
        self.dfDailyCasesNorm = dfDailyCases.copy()
        for auth in dfDailyDeaths.columns:
            pop = self.popData.getPop(auth)
            corr = float(100000./pop)
            dfDailyDeaths[auth] = dfDailyDeaths[auth]*corr
        self.dfDailyDeathsNorm = dfDailyDeaths.copy()

        self.dfDailyDeathsRaw = self.dfDailyDeathsRaw.join(self.dfDailyCasesRaw, lsuffix="_deaths", rsuffix="_cases")
        self.dfDailyDeathsNorm = self.dfDailyDeathsNorm.join(self.dfDailyCasesNorm, lsuffix="_deaths", rsuffix="_cases")


    def getRawDeathsData(self):
        return(self.dfDailyDeathsRaw)
    def getNormDeathsData(self):
        return(self.dfDailyDeathsNorm)
        
    def getRawData(self):
        return self.dfRaw

    def getNormData(self):
        return self.dfNorm

    def getLegendLst(self, authLst):
        legendLst = []
        for auth in authLst:
            authName = self.popData.code2authName(auth)
            legendLst.append(authName)
        return legendLst


    def getRankedData(self,normalised = True, rolling_window='5d',lag=3):
        """Return a list of tuples of authority, normalised cases and 
        normalised rate.   returns the data for curent date -lag days 
        (because the most recent data is incompletes so should not be used).
        """
        if (normalised):
            df = self.dfNorm
        else:
            df = self.dfRaw
            
        dfRoll = df.rolling(rolling_window).mean()
        dfDiff = df.diff(axis=0)
        dfDiffRoll = dfDiff.rolling(rolling_window).mean()

        dfCurrDiff = dfDiffRoll.iloc[-1*(lag+1)].sort_values(ascending=False).to_frame()

        authCodes = dfCurrDiff.index
        authNames = self.getLegendLst(authCodes)
        dfCurrDiff.index = authNames
        dfCurrDiff['rank'] = dfCurrDiff.rank(ascending=False)
        dfCurrDiff['code'] = authCodes
        return(dfCurrDiff)

    def plotAuthorityData(self, authLst,
                          cumulative=False,
                          normalised=False,
                          rollingWindow=None,
                          periodStr=None,
                          chartFname="chart2.png"):
        seriesLst = authLst.copy()

        # Either present raw cases or normalised cases per 100k population.
        if normalised:
            df = self.dfNorm
            normStr = "per 100k population"
            # Add normalised data for England for comparison.
            seriesLst.append("E92000001")
        else:
            df = self.dfRaw
            normStr = ""

        # If we do not want cumulative data, calculate daily changes.
        if not cumulative:
            cumStr = "Cases Per Day"
            df = df.diff(axis=0)
        else:
            cumStr = "Total Cases"
            
        # If we hae specified a rollingWindow value ('7d' etc)
        # then calculate a rolling average over that window.
        if rollingWindow is not None:
            df = df.rolling(rollingWindow).mean()
            rollStr = "%s rolling average" % rollingWindow
        else:
            rollStr = ""

        # Select only the requested data timeframe
        if periodStr is not None:
            df = df.last(periodStr)

            
        # Assemble the title, Y axis label and legend.
        titleStr = "Confirmed Covid-19 Cases %s\n%s %s" % (normStr, cumStr,rollStr)
        yAxisStr = "%s, %s" % (cumStr, normStr)
        legendLst = self.getLegendLst(seriesLst)

        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(7,6))
        h1 = df.plot(ax=axes,
                y=seriesLst,
                grid=True,
                title=titleStr)
        # Highlight the first series
        axes.set_prop_cycle(None)
        df.plot(ax=axes, y=seriesLst[0], linewidth=4, grid=True)

        axes.legend(legendLst)
        axes.set_ylabel(yAxisStr)
        fig.savefig(chartFname)
        plt.close(fig)
        print("plot complete")

        
    def plotNationalDeathsData(self,
                               caseOffsetDays=7,
                               normalised=False,
                               rollingWindow=None,
                               periodStr=None,
                               chartFname="chart2.png"):
        '''
        Plot graphs of rate of national covid related deaths vs case rate (offset by a given number of days.
        '''
        seriesLst = [
            "E92000001",  # England
            "S92000003",  # Scotland
            "W92000004",  # Wales
            "N92000002",  # Northern Ireland
        ]

        # Create lists of the series names in the dataframe
        casesSeriesLst = []
        deathsSeriesLst = []
        for auth in seriesLst:
            casesSeriesLst.append("%s_cases" % auth)
            deathsSeriesLst.append("%s_deaths" % auth)
            
        
        # Either present raw cases or normalised cases per 100k population.
        if normalised:
            df = self.dfDailyDeathsNorm
            normStr = "per 100k population"
        else:
            df = self.dfDailyDeathsRaw
            normStr = ""


        # If we hae specified a rollingWindow value ('7d' etc)
        # then calculate a rolling average over that window.
        if rollingWindow is not None:
            df = df.rolling(rollingWindow).mean()
            rollStr = "%s rolling average" % rollingWindow
        else:
            rollStr = ""

        # Select only the requested data timeframe
        if periodStr is not None:
            df = df.last(periodStr)

            
        # Assemble the title, Y axis label and legend.
        titleStr = "Confirmed Covid-19 Cases %s\n%s %s" % (normStr, "Cases per Day",rollStr)
        yAxisStr = "%s, %s" % ("Cases per Day", normStr)
        legendLst = self.getLegendLst(seriesLst)

        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(7,6))
        h1 = df.plot(ax=axes,
                     y=casesSeriesLst,
                     grid=True,
                     title=titleStr)

        axes.legend(legendLst)
        axes.set_ylabel(yAxisStr)
        fig.savefig("%s_cases.png" % chartFname)
        plt.close(fig)

        # Assemble the title, Y axis label and legend for deaths chart.
        titleStr = "Covid-19 Related Deaths %s\n%s %s" % (normStr, "Deaths Per Day",rollStr)
        yAxisStr = "%s, %s" % ("Deaths (within 28 days of +ve test) per day", normStr)
        legendLst = self.getLegendLst(seriesLst)
        print("Plotting deaths data: ",deathsSeriesLst)
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(7,6))
        h1 = df.plot(ax=axes,
                     y=deathsSeriesLst,
                     grid=True,
                     title=titleStr)

        axes.legend(legendLst)
        axes.set_ylabel(yAxisStr)
        fig.savefig("%s_deaths.png" % chartFname)
        plt.close(fig)

        # Now Plot Deaths per Case (with time shift of cases)
        dfOffset = df.shift(periods=caseOffsetDays)
        #print(df,dfOffset)
        dfRatio = pd.DataFrame()
        for n in range(0,len(deathsSeriesLst)):
            auth = seriesLst[n]
            print(n,auth)
            dfRatio[auth] = df["%s_deaths" % auth] / dfOffset["%s_cases" % auth]
        print(dfRatio)
        # Assemble the title, Y axis label and legend for deaths chart.
        titleStr = "Covid-19 Related Deaths per Case %s\n%s %s" % (normStr, "Deaths Per Day",rollStr)
        yAxisStr = "%s, %s" % ("Deaths (within 28 days of +ve test) per case per day", normStr)
        legendLst = self.getLegendLst(seriesLst)
        print("Plotting deaths ratio data: ",deathsSeriesLst)
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(7,6))
        h1 = dfRatio.plot(ax=axes,
                     y=seriesLst,
                     grid=True,
                     title=titleStr)

        axes.legend(legendLst)
        axes.set_ylabel(yAxisStr)
        fig.savefig("%s_ratio.png" % chartFname)
        plt.close(fig)


        print("plot complete")



        
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

    ca = CovidAnalysis(inFname)
    
    print(ca.getRankedData(normalised=True, rolling_window='7d', lag=64))

    ca.plotAuthorityData(authoritiesLst, cumulative=False, normalised=True, chartFname="tst.png")
    print("__main__ complete")
