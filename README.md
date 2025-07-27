# Project Overview 

### A descriptive data analysis project to demonstrate the data analysis process starting from data acquisition, exploration, preparation, to analysis of findings, and visualization. 

### Business question: "Which NBA players are the most injury-prone based on historical data?"

### Audience: Fantasy Basketball Players, Casual fans, Stephen A. Smith etc.

## Setup and Usage 
- Big picture: Scrape data with SeleniumBase and BeautifulSoup4 -> Save to SQLite database -> Analyze with SQL / pandas -> Export query to CSV -> Import CSV into Tableau
- Current objective: Analyze acquired data from records.db

## Dataset and Data Collection Notes
- Since injury data will keep growing and changing over time, we have decided to only acquire data from the indicated season (2024-25 via modifiable cutoff_date) using a one-time snapshot with injury_scraper VS. a live-automated data scraping program which is likely to get detected as a bot by the website.
  
- Future ideas: 
  - Season Range Scraping (let users enter the season year they want to look into)!
  - Create a requirements.txt to list out installed libraries
  - Look into virtual environments
- Data source: Pro Sports Transaction (PST) which has the most recent injury data and its free!
  

- Notes: 
  - injury_scraper.py:
    - We can bypass the Cloudflare Turnstile protection service on PST's web page using SeleniumBase UC mode, undetected-chromedriver, and a randomized execution suspension between page scraping through ```time.sleep``` and ```random.uniform(start, end)```. 
    - This experience has led me through a rabbit-hole of how protection against bots are implemented throughout time, from early captchas to modern-day security services from companies like Cloudflare - these services will likely impede web-scraping scripts. This video by Michael Mintz was quite insightful on this: https://www.youtube.com/watch?v=5dMFI3e85ig.
    - Some of the notable security measures over time: Google reCAPTCHA -> Cloudflare Turnstile CAPTCHA-replacement which ran a series of small non-interactive JS challenges gathering signals about the visitor [solved by undetected-chromedriver which helped selenium get past Turnstile].
      - https://developers.cloudflare.com/turnstile/
      - https://github.com/ultrafunkamsterdam/undetected-chromedriver
    - As mentioned, we use SeleniumBase UC Mode which is a modified fork of undetected-chromedriver which has bug fixes, additional features like multithreading support. 
      - We import the SB class from the selenium base library, SB is a simplified Selenium wrapper that manages setup/teardown of the browser automatically -- no need to call quit() after completing all tasks!
    
    - BeautifulSoup from the bs4 library will be used to parse through PST's html which contains a table of player information.
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
    
    - We use the sqlite3 module as its part of Python's standard library, I'm not interested in running a server process, and its lightweight which is perfect for the limited amount of operations we plan to use it for -- an intermediate storage prior to analysis.
      - It's inefficient but we replace the existing records table if it exists, otherwise the old data from previous runs stay - we want to avoid duplicate entries, outdated rows, schema conflicts.
      - sqlite3.connect will connect to the existing records.db if it exists or create it if not
      - the AUTOINCREMENT for the id field means it is filled automatically with an unused integer everytime we create an entry
      - PST's format looks like this and it's how we acquire the information: ['2025-05-01', 'Rockets', '• Jock Landale', 'knee injury (out for season)']
      - We use the UNIQUE constraint on the combination of name, date to prevent insertion of a similar rows. We do leave out id as its autoincremented and always unique, which means its inclusion will not prevent duplicate records. 
    
    - Pagination process: we use PST's url! For every page, the end of the link ends with an offset value that decrements/increments by 25 whenever you move to the previous/next page. We can use a boolean variable like ```inSeason``` to keep track of whether the row in question is less than the cutoff. 
    - We use the datetime module of Python's standard lib to set the cutoff for data acquisition. Since we don't know the exact date the season starts, we use this as an estimate: https://www.tickpick.com/blog/how-long-is-nba-basketball-season/
      - Note that we use the unpack operator ```*CUTOFF_DATE``` to unpack the tuple in our declared constant. This is a Python feature, we're not dereferencing a pointer.

- Relevant libraries/modules:
  - `seleniumbase` – browser automation for scraping
  - `bs4` – HTML parsing with BeautifulSoup
  - `sqlite3` – database access
  - `datetime` – date/time operations
  - `random` – generating delays to simulate human behavior
  - `time` – sleep functions and timestamps

## Data Exploration and Preparation
- Fortunately, our work with injury_scraper.py has removed empty rows found in PST. 
- However, there are still invalid rows that may have been inputted incorrectly, such as these two found from the scraped 2024-25 season:
  ![alt text](<Screenshot 2025-07-26 at 9.44.33 PM.png>)
  - Solution: We can filter these out with our sqlite queries in the data analysis stage!

## Data Analysis
- Questions we will try to answer:
  - Who are the most injury-prone players? 
  - Which injuries occur most often?
  - Average recovery time per injury?

- `records.db` schema
  - `records(id, name, date, notes)`

- Approach
  - **Injury Duration Calculation**
    - For a given player, find a row where `notes` **does not** contain `'returned to lineup'`.
    - Then search **forward in time** for the **next** row where the same player's `notes` **does** contain `'returned to lineup'`
    - Subtract the two dates to calculate an **injury period**.
    - Repeat and **sum all injury periods** for each player to identify the most injury-prone.
    - For players still injured (i.e. no return found), use a **cutoff date** (i.e. end of season) to cap their injury duration.
  
  - **Injury Frequency Ranking**
    - Look at all `notes` **not equal to** `'returned to lineup'`.
    - Group and count unique injury descriptions.
    - Rank by frequency.
  
  - **Average Recovery Time per Injury Type**
    - For each injury note (excluding 'returned to lineup'), track the **paired return date** and calculate recovery time.
    - group by injury type and average the durations.

- injury_analysis.py
  - Notes:

- Relevant libraries/modules:
  - `sqlite3` - database access
  - `pandas` - data handling
  - `datetime` - time deltas

## Visualization and Presentation

