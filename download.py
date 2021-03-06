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

def downloadLatestData3(
        urlStr = "https://coronavirus.data.gov.uk/downloads/csv", #'https://coronavirus.data.gov.uk/',
        dataDirStr = "data",
):
    deathsFname = "coronavirus-deaths_latest.csv"
    casesFname = "coronavirus-cases_latest.csv"
    #downloadPath = "~/Downloads"
    downloadPath = "."  # Headless chrome downloads to working directory

    # If the files already exist in the downloads folder, delete them
    casesPath = os.path.expanduser(os.path.join(downloadPath,casesFname))
    deathsPath = os.path.expanduser(os.path.join(downloadPath,deathsFname))
    if (os.path.exists(casesPath)):
        os.remove(casesPath)
    if (os.path.exists(deathsPath)):
        os.remove(deathsPath)
    

    # Create the output data directory if necessary
    dataDir = os.path.join(".",dataDirStr)
    if (not os.path.exists(dataDir)):
        print("Creating Data Directory %s" % dataDir)
        os.makedirs(dataDir)
    
    # Download Cases Data
    casesUrl = "%s/%s" % (urlStr,casesFname)
    fileData = requests.get(casesUrl)
    print("Saving data to %s" % casesPath)
    open(casesPath, 'w').write(fileData.content.decode())

    # Download Deaths Data
    deathsUrl = "%s/%s" % (urlStr,deathsFname)
    fileData = requests.get(deathsUrl)
    print("Saving data to %s" % deathsPath)
    open(deathsPath, 'w').write(fileData.content.decode())
    

    
    print("Waiting for %s to download..." % casesPath)
    while not os.path.exists(casesPath):
        time.sleep(0.2)
        sys.stderr.write(".")
    sys.stdout.write("\nDownload Complete\n")
    print("Waiting for %s to download..." % deathsPath)
    while not os.path.exists(deathsPath):
        time.sleep(0.2)
        sys.stderr.write(".")
    sys.stdout.write("\nDownload Complete\n")

    # Copy to data directory
    print()
    print("Copying files to data folder %s" % dataDir)
    shutil.copy(casesPath,os.path.join(dataDir,casesFname))
    shutil.copy(deathsPath,os.path.join(dataDir,deathsFname))

    casesDate = getLatestDate(os.path.join(dataDir,casesFname))
    deathsDate = getLatestDate(os.path.join(dataDir,deathsFname))

    casesDateFname = "%s_%s%s" % (os.path.splitext(casesFname)[0],
                         casesDate.isoformat(),
                         os.path.splitext(casesFname)[1])
    deathsDateFname = "%s_%s%s" % (os.path.splitext(deathsFname)[0],
                         deathsDate.isoformat(),
                         os.path.splitext(deathsFname)[1])
    print(casesDateFname, deathsDateFname)
    shutil.copy(casesPath,os.path.join(dataDir,casesDateFname))
    shutil.copy(deathsPath,os.path.join(dataDir,deathsDateFname))


def downloadLatestData2(
        urlStr = 'https://coronavirus.data.gov.uk/',
        dataDirStr = "data",
):
    deathsFname = "coronavirus-deaths_latest.csv"
    casesFname = "coronavirus-cases_latest.csv"
    #downloadPath = "~/Downloads"
    downloadPath = "."  # Headless chrome downloads to working directory

    # If the files already exist in the downloads folder, delete them
    casesPath = os.path.expanduser(os.path.join(downloadPath,casesFname))
    deathsPath = os.path.expanduser(os.path.join(downloadPath,deathsFname))
    if (os.path.exists(casesPath)):
        os.remove(casesPath)
    if (os.path.exists(deathsPath)):
        os.remove(deathsPath)
    
    # Use a web browser to render the page.
    chrome_options = webdriver.chrome.options.Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver",
                               chrome_options=chrome_options)
    browser.get(urlStr)
    # give the page chance to finish downloading ajax bits
    time.sleep(2)

    # Click on the two links to download the cases and deaths datasets
    print("Starting Cases Data Download")
    cases_link = browser.find_element_by_partial_link_text("Download cases data as CSV")
    cases_link.click()
    time.sleep(0.2)
    print("Starting Deaths Data Download")
    deaths_link = browser.find_element_by_partial_link_text("Download deaths data as CSV")
    deaths_link.click()

    # Create the output data directory if necessary
    dataDir = os.path.join(".",dataDirStr)
    if (not os.path.exists(dataDir)):
        print("Creating Data Directory %s" % dataDir)
        os.makedirs(dataDir)
    
    # Wait for the downloads to finish
    print("Waiting for %s to download..." % casesPath)
    while not os.path.exists(casesPath):
        time.sleep(0.2)
        sys.stderr.write(".")
    sys.stdout.write("\nDownload Complete\n")
    print("Waiting for %s to download..." % deathsPath)
    while not os.path.exists(deathsPath):
        time.sleep(0.2)
        sys.stderr.write(".")
    sys.stdout.write("\nDownload Complete\n")

    # Copy to data directory
    print()
    print("Copying files to data folder %s" % dataDir)
    shutil.copy(casesPath,os.path.join(dataDir,casesFname))
    shutil.copy(deathsPath,os.path.join(dataDir,deathsFname))

    casesDate = getLatestDate(os.path.join(dataDir,casesFname))
    deathsDate = getLatestDate(os.path.join(dataDir,deathsFname))

    casesDateFname = "%s_%s%s" % (os.path.splitext(casesFname)[0],
                         casesDate.isoformat(),
                         os.path.splitext(casesFname)[1])
    deathsDateFname = "%s_%s%s" % (os.path.splitext(deathsFname)[0],
                         deathsDate.isoformat(),
                         os.path.splitext(deathsFname)[1])
    print(casesDateFname, deathsDateFname)
    shutil.copy(casesPath,os.path.join(dataDir,casesDateFname))
    shutil.copy(deathsPath,os.path.join(dataDir,deathsDateFname))

    
        
def downloadLatestData(
        urlStr = 'https://fingertips.phe.org.uk/documents/Historic%20COVID-19%20Dashboard%20Data.xlsx',
        dataDirStr = "data",
        latestFileFname = "latestData.xlsx",
        symlinkFname = "latestData.xlsx"
        ):
    # Download the File
    dataDir = os.path.join(".",dataDirStr)
    if (not os.path.exists(dataDir)):
        print("Creating Data Directory %s" % dataDir)
        os.makedirs(dataDir)
    print("Downloading Data from %s" % urlStr)
    fileData = requests.get(urlStr)
    filePath = os.path.join(dataDir,latestFileFname)
    print("Saving data to %s" % filePath)
    open(filePath, 'wb').write(fileData.content)

    # Look in the file to get the last data data in the file.
    print("Extracting latest date from file")
    df = pd.read_excel(filePath, sheet_name='UK Cases')
    latestDate=(df.iloc[-1][0]).date()

    fname = "Dashboard_Data_%s.xlsx" % latestDate.isoformat()
    filePath = os.path.join(dataDir,fname)
    print("this file name is %s" % fname)
    if (not os.path.exists(filePath)):
        print("Saving file to %s" % filePath)
        open(filePath, 'wb').write(fileData.content)

        if (os.path.exists(symlinkFname)):
            print("removing pre-existing symlink to latest data")
            os.remove(symlinkFname)
        print("Creating symlink to latest data as %s" % symlinkFname)
        os.symlink(filePath, symlinkFname)
    else:
        print("File aleady exists, not doing anything.")
    print("done!")


if (__name__ == "__main__"):
    downloadLatestData3()
    #getLatestDate("data/coronavirus-cases.csv")
