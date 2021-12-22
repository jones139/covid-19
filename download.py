#!/usr/bin/env python

import os
import sys
import time
import shutil
import requests
import pandas as pd
import selenium
from selenium import webdriver

def getLatestDate(fname):
    # Look in the file to get the last data data in the file.
    print("Extracting latest date from file %s" % fname)
    df = pd.read_csv(fname)
    print(df.columns)
    if ('Specimen date' in df.columns):
        df['Specimen date'] = pd.to_datetime(df['Specimen date'])
        maxDate=max(df['Specimen date']).date()
    elif ('Reporting date' in df.columns):
        df['Reporting date'] = pd.to_datetime(df['Reporting date'])
        maxDate=max(df['Reporting date']).date()
    else:
        print("ERRROR - Can't find date column!!! - using todays date.")
        maxDate = pd.to_datetime('today')

    print("maxDate=%s" % maxDate.isoformat())

    return maxDate


def downloadLatestData(dataDirStr = "data"):
    """ Uses the API to download, utla, ltla and nation data, then merge them so it is similar to the
    data in coronavirus-cases_latest.csv, which no longer contans UTLA data (28apr2021).
    """

    urlStr = "https://api.coronavirus.data.gov.uk/v2/data?areaType=%s&metric=newCasesBySpecimenDate&metric=cumCasesBySpecimenDate&metric=cumDeaths28DaysByDeathDateRate&metric=newAdmissions&metric=newDeaths28DaysByDeathDate&format=csv"
    #urlStr = "https://api.coronavirus.data.gov.uk/v2/data?areaType=%s&metric=newCasesBySpecimenDate&format=csv"
    print("downloading %s...." % (urlStr % "ltla"))
    dfLtla = pd.read_csv(urlStr % "ltla")
    dfUtla = pd.read_csv(urlStr % "utla")
    dfRegion = pd.read_csv(urlStr % "region")
    dfNation = pd.read_csv(urlStr % "nation")
    df = pd.concat([dfNation, dfRegion, dfUtla, dfLtla], axis=0, ignore_index=True)
    df.rename(columns={
        'date':'Specimen date',
        'newCasesBySpecimenDate':'Daily lab-confirmed cases',
        'cumCasesBySpecimenDate':'Cumulative lab-confirmed cases',
        'areaType':'Area type',
        'areaName':'Area name',
        'areaCode':'Area code',
    },inplace=True)
    print(df)

    casesFname = "coronavirus-cases_latest.csv"

    # Create the output data directory if necessary
    dataDir = os.path.join(".",dataDirStr)
    if (not os.path.exists(dataDir)):
        print("Creating Data Directory %s" % dataDir)
        os.makedirs(dataDir)
    
    df.to_csv(os.path.join(".",casesFname), index=False)
    df.to_csv(os.path.join(dataDir,casesFname), index=False)

    casesDate = getLatestDate(os.path.join(dataDir,casesFname))
    casesDateFname = "%s_%s%s" % (os.path.splitext(casesFname)[0],
                         casesDate.isoformat(),
                         os.path.splitext(casesFname)[1])

    df.to_csv(os.path.join(dataDir,casesDateFname), index=False)
            
 

if (__name__ == "__main__"):
    downloadLatestData()
    #downloadLatestData3()
    #getLatestDate("data/coronavirus-cases.csv")
