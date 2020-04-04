#!/usr/bin/env python

import requests
import os
import pandas as pd

urlStr = 'https://fingertips.phe.org.uk/documents/Historic%20COVID-19%20Dashboard%20Data.xlsx'
dataDirStr = "data"
latestFileFname = "latestData.xlsx"
symlinkFname = "latestData.xlsx"


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
print("Saving file to %s" % filePath)
open(filePath, 'wb').write(fileData.content)

if (os.path.exists(symlinkFname)):
    print("removing pre-existing symlink to latest data")
    os.remove(symlinkFname)
print("Creating symlink to latest data as %s" % symlinkFname)
os.symlink(filePath, symlinkFname)

print("done!")

