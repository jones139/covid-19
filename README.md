COVID-19 TRACKER
================

This repository contains tools to download and analyse the COVID-19 cases
data available from public health england.

It currently focuses on doing analysis for a limited number of local
authority areas that I am most interested in (Teesside area), but it could
analyse others very easily.

Current functionality is:
  * Generate graphs of cumulative cases v time for local authority areas.
  * Generate above graphs normalised for population to give cases per 100k population.
  * (working on) adding lines exrapolating based on different doubling times
       to help interpret if the trend is slowing or not.
  * cleverer analysis to follow......
  
  
Any comments please email grahamjones139@gmail.com


Dependencies
------------
The following python libraries are used:
  * pandas for data analysis
  * jinja2 to generate html from templates
  * requests to download data
