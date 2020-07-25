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
    parser.add_argument('--inFile', default="data/coronavirus-cases_latest.csv",
                        help='input filename')
    parser.add_argument('--window', default="7d",
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
        download.downloadLatestData3()
    else:
        print("Not downloading data - attempting to use local data instead")

    ca = analyse.CovidAnalysis(inFname, dropDays=3)
    df = ca.getRawData()
    dataDateStr = str((df.index[-1]).date())

    summary = ca.getRankedData(normalised=True, rolling_window='7d', lag=0)
    top10List = summary[0:10]['code'].tolist()
    print("Top 10=", summary)

    top10Summary = []
    for i in range(0, 10):
        top10Summary.append({
            'Authority': summary.index[i],
            'Rate': summary.iloc[i, 0]
            })

    print(top10Summary)

    ca.plotAuthorityData(top10List,
                         cumulative=False,
                         normalised=True,
                         rollingWindow='7d',
                         chartFname="www/chart3_c.png")
    
    ca.plotAuthorityData(analyse.authoritiesLst,
                         cumulative=True,
                         normalised=False,
                         rollingWindow=None,
                         chartFname="www/chart1_a.png")
    ca.plotAuthorityData(analyse.authoritiesLst,
                         cumulative=False,
                         normalised=False,
                         rollingWindow=None,
                         chartFname="www/chart1_b.png")
    ca.plotAuthorityData(analyse.authoritiesLst,
                         cumulative=False,
                         normalised=False,
                         rollingWindow='7d',
                         chartFname="www/chart1_c.png")
    ca.plotAuthorityData(analyse.authoritiesLst,
                         cumulative=True,
                         normalised=True,
                         rollingWindow=None,
                         chartFname="www/chart2_a.png")
    ca.plotAuthorityData(analyse.authoritiesLst,
                         cumulative=False,
                         normalised=True,
                         rollingWindow=None,
                         chartFname="www/chart2_b.png")
    ca.plotAuthorityData(analyse.authoritiesLst,
                         cumulative=False,
                         normalised=True,
                         rollingWindow='7d',
                         chartFname="www/chart2_c.png")


    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), 'templates/')
        ))

    template = env.get_template('index.html.template')

    outfile = open(os.path.join(os.path.dirname(__file__),
                                'www/index.html'), 'w')
    outfile.write(template.render(data={
        'top10': top10Summary,
        'pageDateStr': (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),
        'dataDateStr': dataDateStr
    }))
    outfile.close()
        
    if (not args['noUpload']):
        print("Uploading to web site")
        os.system(os.path.join(os.path.dirname(__file__), "upload.sh"))
    else:
        print("Not uploading files to web site")
        
