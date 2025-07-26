# Project Overview 

### A descriptive data analysis project to demonstrate the data analysis process starting from data acquisition, exploration, preparation, to analysis of findings, and visualization. 

### Business question: "Which NBA players are the most injury-prone based on historical data?"

### Audience: Fantasy Basketball Players, Casual fans, etc.

## Setup and Usage 

## Dataset and Data Collection Notes
- Big picture: Scrape data with SeleniumBase and BeautifulSoup4 -> Save to SQLite -> Analyze with SQL / pandas -> Export query to CSV -> Import CSV into Tableau

- Since injury data will keep growing and changing over time, we have decided to only acquire data from the indicated season (2024-25) using a one-time snapshot with injury_scraper VS. a live-automated data scraping program which is likely to get detected as a bot by the website.
  
- Future ideas: 
  - Create a requirements.txt to list out installed libraries
  - Look into virtual environments
- Data source: Pro Sports Transaction (PST) which has the most recent injury data and its free!
  

- Method: I have decided to try again on bypassing the Cloudflare Turnstile protection service on PST's web page using SeleniumBase UC mode and undetected-chromedriver. 
  - This experience has led me through a rabbit-hole of how protection against bots are implemented throughout time, from early captchas to modern-day security services from companies like Cloudflare - these services will likely impede web-scraping scripts. This video by Michael Mintz was quite insightful on this: https://www.youtube.com/watch?v=5dMFI3e85ig.
  - Some of the notable security measures over time: Google reCAPTCHA -> Cloudflare Turnstile CAPTCHA-replacement which ran a series of small non-interactive JS challenges gathering signals about the visitor [solved by undetected-chromedriver which helped selenium get past Turnstile].
    - https://developers.cloudflare.com/turnstile/
    - https://github.com/ultrafunkamsterdam/undetected-chromedriver

  - As mentioned, we use SeleniumBase UC Mode which is a modified fork of undetected-chromedrier which has bug fixes, additional features like multithreading support. 
    - We import the SB class from the library, SB is a simplified Selenium wrapper that manages setup/teardown of the browser automatically -- no need to call quit() after completing all tasks!
  
  - BeautifulSoup will be used to parse through PST's html which contains a table of player information.
     ```python 
     print(f"here's the html: {soup.prettify()}") 
    # prints a formatted representation of the html structure of website
     ```
    - We see that the website uses JS to dynamically load and insert real content into the DOM, we're only seeing the initial HTML with prettify --> using my browser's devtools gives use the rendered DOM.
    - The important bits we wanted to see: html > body > div.container > table.datatable.center > tbody > tr align="left"
    - These table rows are the key components which contain player information
    - Attempt #1 at exposing the table's children: 
      ```python
      for row in pst_table.children:
        for cell in row.stripped_strings:
            print(f"\t{cell} ", end='')
      ```
    - Unfortunately, .children will include whitespace and newline nodes, and the dreaded NavigableString objects. We use find_all("tr") instead
  
  - We use sqlite3 as its part of Python's standard library, I'm not interested in running a server process, and its lightweight which is perfect for the limited amount of operations we plan to use it for -- an intermediate storage prior to analysis.
    - sqlite3.connect will connect to the existing records.db if it exists or create it if not
    - the AUTOINCREMENT for the id field means it is filled automatically with an unused integer everytime we create an entry
    - PST's format looks like this and it's how we acquire the information: ['2025-05-01', 'Rockets', '• Jock Landale', 'knee injury (out for season)']

- Relevant libraries: 'seleniumbase', 'BeautifulSoup4', 'sqlite3'

## Data Exploration and Preparation

## Data Analysis

## Visualization and Presentation

