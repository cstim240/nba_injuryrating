# Project Overview 

### A descriptive data analysis project to demonstrate the data analysis process starting from data acquisition, exploration, preparation, to analysis of findings, and visualization. 

### Business question: "Which NBA players are the most injury-prone based on historical data?"

Quick link to the HTML page where my Worksheets are embedded!


Quick link to the data viz:
https://public.tableau.com/views/NBA2024-25PlayerInjuryData/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link

### Audience: Fantasy Basketball Players, Casual fans, etc.

## Setup and Usage 
- Big picture: Scrape data with SeleniumBase and BeautifulSoup4 -> Save to SQLite database -> Analyze with SQL / pandas -> Export query to CSV -> Get player data from Basketball Reference --> Import CSVs into Tableau
- Current objective: Embed tableau onto github pages with a simple html/css setup and write down some of the insights gained from the data we analyzed.

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

- `records.db` schema
  - `records(id, name, date, notes)`

- Approach
  - **Injury Duration Calculation**
    - For a given player, find a row where `notes` **does not** contain `'returned to lineup'`.
    - Then search **forward in time** for the **next** row where the same player's `notes` **does** contain `'returned to lineup'`
    - Subtract the two dates to calculate an **injury period**.
    - Repeat and **sum all injury periods** for each player to identify the most injury-prone.
    - Edge Cases:
      - For players still injured (i.e. no return found), use a **cutoff date** (i.e. end of season) to cap their injury duration.
      - For players coming back from an injury sustained in the previous season, we can just skip their first 'return to lineup' entry.
  
  - **Injury Frequency Ranking**
    - Look at all `notes` **not equal to** `'returned to lineup'`.
    - Group and count unique injury descriptions.
    - Rank by frequency.
  
  - **Average Recovery Time per Injury Type**
    - For each injury note (excluding 'returned to lineup'), track the **paired return date** and calculate recovery time.
    - group by injury type and average the durations.

- injury_analysis.py
  - Notes: Ran into an error with my getInjuryPeriods function where I pair up injury beginning and end rows -- my if statements forgot to account that the notes were turned to lowercase, this resulted in some notes being omitted as I initially had 'note != "activated from IL"' which was enough to disregard some of the player injury notes. 

- Relevant libraries/modules:
  - `sqlite3` - database access
  - `pandas` - data handling
  - `datetime` - time deltas

## Visualization and Presentation
- Tableau Public for our data visualization needs.
- Required Files:
  - aggregateInjuries.csv (from injury_analysis, exportToCSV, aggregateInjuryPeriods)
  - injuryTypes.csv (from injury_analysis, exportToCSV2, aggregateInjuryTypes)
  - player_data/2425_regszn.csv (from BR: https://www.basketball-reference.com/leagues/NBA_2025.html#all_per_game_team-opponent)
  
- Dashboard 1: Injured Days Vs. Injury Count and Injury Types Pie Chart
  - We utilize our aggregateInjuries csv file we generated with injury_analysis.py. We also join this source file with the player statistics csv file from Basketball reference to acquire a filter for player minutes, allowing us to highlight only the 'significant' players likely to be acquired during draft day.
  - I opted for a scatterplot to best show the outliers and reliable players with the x-axis being the injury count and injured days as the y-axis. I've also placed a minutes played (mp) filter to increase or decrease the number of players being shown on the graph. 
  - For the Injury Types Pie Chart, this required the injuryTypes csv which contained each injury (non-distinct) and the corresponding player. This was not in the aggregateInjuries csv file as the 'injuries sustained' column contained multiple values. It was much easier to create a separate csv file instead of parsing through this column.
  - The 'Other' category combines uncommon injuries ie. concussion, eye related injuries, etc.
- Dashboard 2: Per Player Breakdown
  - Again, we utilize the above sources to present a dot plot where each row is a player and each corresponding dot is a type of injury. Hovering on a dot will reveal the amount of times a player has sustained that injury and the full description of said injury. 
  - We implement something similar with the Missed Games per Player Bar Chart where the x-axis is the number of games missed. A color gradient has also been added to represent a larger injury count (note this is not equal to days spent recovering from an injury).
- Dashboard 3: Injury Breakdown
  - We use a horizontal stacked bar chart to represent players for each injury, with each player being a different color. Hovering on a section of a bar reveals the player name and the number of times they have sustained this specific injury. 

- Challenges for this process:
  - Figuring out how to merge different csv datasets to create combined sources for data visualization and graphs. 
  - Creating a phone layout as the default web layout will look very clunky on mobile view. 
  - Learning Tableau's features: table calculations (vs. calculating said attribute in previous phases), differentiating between dimension/attribute/measure of data points, adding enough visuals so that the user can form insights within seconds of viewing the worksheets, decluttering visuals as some of the labels can overlap with each other, adding filters, using different types of charts, combining worksheets into dashboards, etc.

- To preserve the interactibility of the Tableau Dashboards, I've decided to embed them onto a simple HTML file hosted on Github Pages. I'd also like to write down my insighs on here.
  - I've also included some meta tags for the purposes of search engine optimization and indexing. 
    - See: https://developers.google.com/search/docs/crawling-indexing/special-tags and https://gist.github.com/lancejpollard/1978404
    - *og is for sharing previews. og refers to Open Graph tags which controls how the page loks when shared on social media.