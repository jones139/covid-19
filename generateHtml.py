#!/usr/bin/env python

import os
import datetime
import argparse
import shutil

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

    # Today's ranked list
    summary = ca.getRankedData(normalised=True, rolling_window='7d', lag=0)
    # Last week's ranked list.
    summary_prev = ca.getRankedData(normalised=True, rolling_window='7d', lag=7)
    top10List = summary[0:10]['code'].tolist()
    print("Top 10=", summary)

    #summary_prev.sort_index(inplace=True)
    #print("summary_prev")
    #print(summary_prev)
    #print(summary_prev['code']==summary['code'])

    top10Summary = []
    for i in range(0, len(summary.index)):
        curPos = int(summary.iloc[i]['rank'])
        prevPos = int(summary_prev.loc[summary_prev['code']==summary.iloc[i]['code']]['rank'].iloc[0])
        iconName = "RightArrow.png"
        if (curPos<prevPos):
            iconName = "UpArrow.png"
        if (curPos>prevPos):
            iconName = "DownArrow.png"
        
        top10Summary.append({
            'Position': curPos,
            'Position_prev': prevPos,
            'Icon_name': iconName,
            'Authority': summary.index[i],
            'Rate': summary.iloc[i, 0],
            'Rate_weekly': summary.iloc[i, 0] * 7
            })

    print(top10Summary)

    ca.plotAuthorityData(top10List,
                         cumulative=False,
                         normalised=True,
                         rollingWindow='7d',
                         periodStr=None,
                         chartFname="www/chart3_c.png")
    ca.plotAuthorityData(top10List,
                         cumulative=False,
                         normalised=True,
                         rollingWindow='7d',
                         periodStr='12w',
                         chartFname="www/chart3_d.png")

    
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

    ca.plotAuthorityData(analyse.authoritiesLst,
                         cumulative=False,
                         normalised=True,
                         rollingWindow='7d',
                         periodStr='12w',
                         chartFname="www/chart2_d.png")

    
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), 'templates/')
        ))

    # Render main page
    template = env.get_template('index.html.template')
    outfile = open(os.path.join(os.path.dirname(__file__),
                                'www/index.html'), 'w')
    outfile.write(template.render(data={
        'top10': top10Summary,
        'pageDateStr': (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),
        'dataDateStr': dataDateStr
    }))
    outfile.close()

    # Render All Authorities table
    template = env.get_template('all_authorities_table.html.template')
    outfile = open(os.path.join(os.path.dirname(__file__),
                                'www/all_authorities_table.html'), 'w')
    outfile.write(template.render(data={
        'top10': top10Summary,
        'pageDateStr': (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),
        'dataDateStr': dataDateStr
    }))
    outfile.close()


    for iconFname in ['UpArrow.png', 'DownArrow.png', 'RightArrow.png']:
        print(iconFname)
        shutil.copyfile(os.path.join(os.path.dirname(__file__),
                                     'templates',iconFname),
                        os.path.join(os.path.dirname(__file__),
                                     'www',iconFname))
        
    if (not args['noUpload']):
        print("Uploading to web site")
        os.system(os.path.join(os.path.dirname(__file__), "upload.sh"))
    else:
        print("Not uploading files to web site")
        
