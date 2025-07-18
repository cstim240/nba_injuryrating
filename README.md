# Project Overview 

### A descriptive data analysis project to demonstrate the data analysis process starting from data acquisition, exploration, preparation, to analysis of findings, and visualization. 

### Business question: "Which NBA players are the most injury-prone based on historical data?"

### Audience: Fantasy Basketball Players, Casual fans, etc.

## Setup and Usage 

## Dataset and Data Collection Notes
- Big picture: Scrape data with SeleniumBase and BeautifulSoup4 -> Save to SQLite -> Analyze with SQL / pandas -> Export query to CSV -> Import CSV into Tableau

- Since injury data will keep growing and changing over time, we have decided whether we should do a one-time snapshot of current data VS. an automated data scraping program for up-to-date injury reports. As of now, we are opting for the one-time snapshot, we will focus on the 2024-2025 NBA season data ~~,we are also getting blocked with our simple GET requests and even Selenium's webdriver due to the site's anti-scraping measures~~ . 
- Future ideas: 
  - ~~Automate web scraping capabilities with Selenium + an undetected chromedriver or some kind of way to bypass cloudflare bot detection~~
  - Create a requirements.txt to list out installed libraries
  - Look into virtual environments
- Data source: Pro Sports Transaction (PST) which has the most recent injury data and its free!
- Method: I have decided to try again on bypassing the Cloudflare Turnstile protection service on PST's web page using SeleniumBase UC mode and undetected-chromedriver. 
  - This experience has led me through a rabbit-hole of how protection against bots are implemented throughout time, from early captchas to modern-day security services from companies like Cloudflare - these services will likely impede web-scraping scripts. This video by Michael Mintz was quite insightful on this: https://www.youtube.com/watch?v=5dMFI3e85ig.
  - Some of the notable security measures over time: Google reCAPTCHA -> Cloudflare Turnstile CAPTCHA-replacement which ran a series of small non-interactive JS challenges gathering signals about the visitor [solved by undetected-chromedriver which helped selenium get past Turnstile].
    - https://developers.cloudflare.com/turnstile/
    - https://github.com/ultrafunkamsterdam/undetected-chromedriver
  
  - Undetected-chromedriver has to adapt to changes caused by new versions of Chrome, Selenium, Cloudflare.
  - We also need SeliniumBase UC Mode which is a modified fork of undetected-chromedrier which has bug fixes, additional features like multithreading support. 
    - UC mode is one of many SeleniumBase modes...
  
  - We use sqlite3 as its part of Python's standard library, I'm not interested in running a server process, and its lightweight which is perfect for the limited amount of operations we plan to use it for -- an intermediate storage prior to analysis.
- Relevant libraries: 'seleniumbase', 'BeautifulSoup4', 'sqlite3'

## Data Exploration and Preparation

## Data Analysis

## Visualization and Presentation

