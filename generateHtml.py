#!/usr/bin/env python

import os
import datetime
import argparse

import pandas as pd
import jinja2

import download
import analyse



if (__name__ == "__main__"):
    print("html.main()")
    parser = argparse.ArgumentParser(description='generateHtml')
    parser.add_argument('--inFile', default="latestData.xlsx",
                        help='input filename')
    parser.add_argument('--window', default="5d",
                        help='Window width for rolling average lines')
    parser.add_argument('--noDownload', dest='noDownload', action='store_true',
                        help="Do not download the latest data")
    parser.add_argument('--noUpload', dest='noUpload', action='store_true',
                        help="Do not Upload the generated html to web site")
    argsNamespace = parser.parse_args()
    args = vars(argsNamespace)
    print(args)
    inFname = args['inFile']
    windowStr = args['window']

    if (not args['noDownload']):
        print("Downloading Latest Data")
        download.downloadLatestData()
    else:
        print("Not downloading data - attempting to use local data instead")


    df=analyse.loadFile(inFname)
    dataDateStr=str((df.index[-1]).date())

    analyse.plotAuthorityData(df,analyse.authoritiesLst,
                              chartFname="www/chart1.png",
                              rolling_window = windowStr
    )
    analyse.plotNormalisedAuthorityData(df,analyse.authoritiesLst,
                                        chartFname="www/chart2.png",
                                        rolling_window = windowStr
    )
    #plotFit(df,"Hartlepool")


    # Get the most recent data, and filter it to only view the
    # corrected values for each authority.
    #dfCurrent = df.iloc[-1,:]
    #print(dfCurrent.sort_values().filter(like='_corr', axis=0))


    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__),'templates/')
        ))

    template = env.get_template('index.html.template')

    outfile = open(os.path.join(os.path.dirname(__file__),'www/index.html'),
                   'w')
    outfile.write(template.render(data={
        'pageDateStr' : datetime.datetime.now(),
        'dataDateStr' : dataDateStr
    }))
    outfile.close()
        
    if (not args['noUpload']):
        print("Uploading to web site")
        os.system(os.path.join(os.path.dirname(__file__),"upload.sh"))
    else:
        print("Not uploading files to web site")
        
