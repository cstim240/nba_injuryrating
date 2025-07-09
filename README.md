# Project Overview 

### A descriptive data analysis project to demonstrate the data analysis process starting from data acquisition, exploration, preparation, to analysis of findings, and visualization. 

### Business question: "Which NBA players are the most injury-prone based on historical data?"

### Audience: Fantasy Basketball Players, Casual fans, etc.

## Setup and Usage 

## Dataset and Data Collection Notes
- Since injury data will keep growing and changing over time, we have decided whether we should do a one-time snapshot of current data VS. an automated data scraping program for up-to-date injury reports. As of now, we are opting for the one-time snapshot -- we are also getting blocked with our simple GET requests and even Selenium's webdriver due to the site's anti-scraping measures. 
- Future ideas: 
  - Automate web scraping capabilities with Selenium + an undetected chromedriver or some kind of way to bypass cloudflare bot detection
  - Create a requirements.txt to list out installed libraries
  - Look into virtual environments
- Data source: Pro Sports Transaction (PST) which has the most recent injury data and its free!
- Method: ~~We will create a Python script to fetch the webpage from PST, downloading all its table contents into a csv file. This script's initialversion can only download a page at a time.~~ MANUAL process - I plan on creating a text file which I will paste the HTML code of the PST page I want stats from --> use a python script to input processed player injury --> place data into a SQLite database file. 
- Relevant libraries: 'Selenium - webdriver', 

## Data Exploration and Preparation

## Data Analysis

## Visualization and Presentation

