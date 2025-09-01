# Project Overview

A descriptive data analysis project demonstrating the end-to-end process: **data acquisition**, **exploration**, **preparation**, **analysis**, and **visualization**.

**Business Question:**  
*Which NBA players are the most injury-prone based on historical data?*

- [View the interactive dashboards (HTML)](https://cstim240.github.io/nba_injuryrating/)
- [Direct link to Tableau visualization](https://public.tableau.com/views/NBA2024-25PlayerInjuryData/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

**Audience:** Fantasy basketball players, analysts, and NBA fans.

---

# Setup and Usage

## Project Workflow (TL;DR)

1. **Scrape injury data** from Pro Sports Transactions using **SeleniumBase** + **BeautifulSoup** (`injury_scraper.py`).
2. **Store raw entries** in a local **SQLite** database.
3. **Aggregate & clean** injury data with **pandas** (`injury_analysis.py`).
4. **Export CSVs** for further analysis and Tableau.
5. **Join with player stats** (from Basketball Reference) in Tableau to build visualizations.
6. *(Optional)* Embed Tableau dashboards in a simple HTML page.

---

## Requirements

- **Python 3.11+** (3.12 recommended)
- **Google Chrome** (SeleniumBase manages the driver)
- **Git**

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/cstim240/nba_injuryrating.git
cd nba_injuryrating

# (Optional) One-liner: create and activate a virtual environment, install dependencies, and run both scripts
python3 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip && pip install -r requirements.txt && python injury_scraper.py && python injury_analysis.py

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate
# On Windows (PowerShell): .\.venv\Scripts\Activate.ps1

# 3. Install dependencies
python -m pip install -U pip
pip install -r requirements.txt
```

---

## Usage Notes

- To scrape and analyze a different season (other than 2024-25), update a few constants in `injury_scraper.py`:
  - `INITIAL_OFFSET` (URL parameter)
  - `CUTOFF_DATE`
  - The base URL itself

- Run the scraper:
  ```bash
  python3 injury_scraper.py
  ```
  This generates a local SQLite database (`records.db`) containing all raw injury entries.

- Process and analyze the data:
  - Update constants in `injury_analysis.py` (`CUTOFF_YEAR`, `CUTOFF_MONTH`, `CUTOFF_DAY`) as needed.
  - Run:
    ```bash
    python3 injury_analysis.py
    ```
  This produces two CSV files in the `generatedCSVs` directory:
  - `aggregateInjuries.csv`: One row per player, with injury count, total days missed, and injuries sustained.
  - `injuryTypes.csv`: Expanded list of injuries by player (multiple rows per player).

- Download player stats from [Basketball Reference](https://www.basketball-reference.com/leagues/NBA_2025.html#all_per_game_team-opponent) and join with the above CSVs in Tableau for visualization.

---

These files are sufficient for merging datasets and creating interactive dashboards in Tableau.  
For more details, see the in-depth notes below.

---

## Dataset and Data Collection Notes

- Since injury data will keep growing and changing over time, we have decided to only acquire data from the indicated season (2024-25 via modifiable cutoff_date) using a one-time snapshot with `injury_scraper.py` vs. a live-automated data scraping program which is likely to get detected as a bot by the website.
  
- **Future ideas:** 
  - Season Range Scraping (let users enter the season year they want to look into)!

- **Data sources:** Pro Sports Transaction (PST) for the most recent injury data (free!), and Basketball Reference for player minutes and other relevant performance statistics.
  
- **Notes:** 
  - **injury_scraper.py:**
    - We can bypass the Cloudflare Turnstile protection service on PST's web page using SeleniumBase UC mode, undetected-chromedriver, and a randomized execution suspension between page scraping through `time.sleep` and `random.uniform(start, end)`. 
    - This experience has led me through a rabbit-hole of how protection against bots is implemented, from early captchas to modern-day security services like Cloudflare. This [video by Michael Mintz](https://www.youtube.com/watch?v=5dMFI3e85ig) was quite insightful.
    - Some notable security measures over time: Google reCAPTCHA → Cloudflare Turnstile CAPTCHA-replacement, which runs a series of small non-interactive JS challenges gathering signals about the visitor (solved by undetected-chromedriver which helped selenium get past Turnstile).
      - [Cloudflare Turnstile docs](https://developers.cloudflare.com/turnstile/)
      - [undetected-chromedriver GitHub](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
    - We use SeleniumBase UC Mode, a modified fork of undetected-chromedriver with bug fixes and additional features like multithreading support. 
      - We import the `SB` class from the seleniumbase library; `SB` is a simplified Selenium wrapper that manages setup/teardown of the browser automatically—no need to call `quit()` after completing all tasks!
    - BeautifulSoup from the `bs4` library is used to parse PST's HTML, which contains a table of player information.
      ```python
      print(f"here's the html: {soup.prettify()}")
      # prints a formatted representation of the html structure of website
      ```
      - The website uses JS to dynamically load and insert real content into the DOM; we're only seeing the initial HTML with prettify. Using browser devtools gives us the rendered DOM.
      - The important bits: `html > body > div.container > table.datatable.center > tbody > tr align="left"`
      - These table rows are the key components which contain player information.
      - Attempt #1 at exposing the table's children:
        ```python
        for row in pst_table.children:
            for cell in row.stripped_strings:
                print(f"\t{cell} ", end='')
        ```
      - Unfortunately, `.children` will include whitespace and newline nodes, and the dreaded NavigableString objects. We use `find_all("tr")` instead.
    - We use the `sqlite3` module as it's part of Python's standard library, lightweight, and perfect for our limited operations—an intermediate storage prior to analysis.
      - We replace the existing records table if it exists to avoid duplicate entries, outdated rows, schema conflicts.
      - `sqlite3.connect` will connect to the existing `records.db` if it exists or create it if not.
      - The `AUTOINCREMENT` for the id field means it is filled automatically with an unused integer every time we create an entry.
      - PST's format looks like this and it's how we acquire the information: `['2025-05-01', 'Rockets', '• Jock Landale', 'knee injury (out for season)']`
      - We use the `UNIQUE` constraint on the combination of name and date to prevent insertion of similar rows. We leave out id as it's autoincremented and always unique.
    - **Pagination process:** We use PST's URL! For every page, the end of the link ends with an offset value that increments/decrements by 25 whenever you move to the previous/next page. We can use a boolean variable like `inSeason` to keep track of whether the row in question is less than the cutoff. 
    - We use the `datetime` module to set the cutoff for data acquisition. Since we don't know the exact date the season starts, we use this as an estimate: https://www.tickpick.com/blog/how-long-is-nba-basketball-season/
      - Note that we use the unpack operator `*CUTOFF_DATE` to unpack the tuple in our declared constant. This is a Python feature, not dereferencing a pointer.

- **Relevant libraries/modules:**
  - `seleniumbase` – browser automation for scraping
  - `bs4` – HTML parsing with BeautifulSoup
  - `sqlite3` – database access
  - `datetime` – date/time operations
  - `random` – generating delays to simulate human behavior
  - `time` – sleep functions and timestamps

---

## Data Exploration and Preparation

- Fortunately, our work with `injury_scraper.py` has removed empty rows found in PST. 
- However, there are still invalid rows that may have been inputted incorrectly, such as these two found from the scraped 2024-25 season:
  ![alt text](<Screenshot 2025-07-26 at 9.44.33 PM.png>)
  - **Solution:** We can filter these out with our sqlite queries in the data analysis stage!

---

## Data Analysis

- **Questions we will try to answer:**
  - Who are the most injury-prone players? 
  - Which injuries occur most often?

- **`records.db` schema:**
  - `records(id, name, date, notes)`

- **Approach:**
  - **Injury Duration Calculation**
    - For a given player, find a row where `notes` **does not** contain `'returned to lineup'`.
    - Then search **forward in time** for the **next** row where the same player's `notes` **does** contain `'returned to lineup'`.
    - Subtract the two dates to calculate an **injury period**.
    - Repeat and **sum all injury periods** for each player to identify the most injury-prone.
    - **Edge Cases:**
      - For players still injured (i.e. no return found), use a **cutoff date** (i.e. end of season) to cap their injury duration.
      - For players coming back from an injury sustained in the previous season, we can just skip their first 'return to lineup' entry.
  - **Injury Frequency Ranking**
    - Look at all `notes` **not equal to** `'returned to lineup'`.
    - Group and count unique injury descriptions.
    - Rank by frequency.
  - **Average Recovery Time per Injury Type**
    - For each injury note (excluding 'returned to lineup'), track the **paired return date** and calculate recovery time.
    - Group by injury type and average the durations.

- **injury_analysis.py**
  - Notes: Ran into an error with my `getInjuryPeriods` function where I pair up injury beginning and end rows—my if statements forgot to account that the notes were turned to lowercase, which resulted in some notes being omitted as I initially had `note != "activated from IL"` which was enough to disregard some of the player injury notes. 

- **Relevant libraries/modules:**
  - `sqlite3` – database access
  - `pandas` – data handling
  - `datetime` – time deltas

---

## Visualization and Presentation

- **Tableau Public** for our data visualization needs.
- **Required Files:**
  - `aggregateInjuries.csv` (from injury_analysis, exportToCSV, aggregateInjuryPeriods)
  - `injuryTypes.csv` (from injury_analysis, exportToCSV2, aggregateInjuryTypes)
  - `player_data/2425_regszn.csv` (from BR: https://www.basketball-reference.com/leagues/NBA_2025.html#all_per_game_team-opponent)
  
- **Dashboard 1: Injured Days Vs. Injury Count and Injury Types Pie Chart**
  - We utilize our `aggregateInjuries.csv` file generated with `injury_analysis.py`. We also join this source file with the player statistics CSV file from Basketball Reference to acquire a filter for player minutes, allowing us to highlight only the 'significant' players likely to be acquired during draft day.
  - I opted for a scatterplot to best show the outliers and reliable players, with the x-axis being the injury count and injured days as the y-axis. I've also placed a minutes played (mp) filter to increase or decrease the number of players being shown on the graph. 
  - For the Injury Types Pie Chart, this required the `injuryTypes.csv` which contained each injury (non-distinct) and the corresponding player. This was not in the `aggregateInjuries.csv` file as the 'injuries sustained' column contained multiple values. It was much easier to create a separate CSV file instead of parsing through this column.
  - The 'Other' category combines uncommon injuries (e.g., concussion, eye-related injuries, etc.).
- **Dashboard 2: Per Player Breakdown**
  - Again, we utilize the above sources to present a dot plot where each row is a player and each corresponding dot is a type of injury. Hovering on a dot will reveal the amount of times a player has sustained that injury and the full description of said injury. 
  - We implement something similar with the Missed Games per Player Bar Chart where the x-axis is the number of games missed. A color gradient has also been added to represent a larger injury count (note this is not equal to days spent recovering from an injury).
- **Dashboard 3: Injury Breakdown**
  - We use a horizontal stacked bar chart to represent players for each injury, with each player being a different color. Hovering on a section of a bar reveals the player name and the number of times they have sustained this specific injury. 

- **Challenges for this process:**
  - Figuring out how to merge different CSV datasets to create combined sources for data visualization and graphs. 
  - Creating a phone layout as the default web layout will look very clunky on mobile view. 
  - Learning Tableau's features: table calculations (vs. calculating said attribute in previous phases), differentiating between dimension/attribute/measure of data points, adding enough visuals so that the user can form insights within seconds of viewing the worksheets, decluttering visuals as some of the labels can overlap with each other, adding filters, using different types of charts, combining worksheets into dashboards, etc.

- To preserve the interactivity of the Tableau Dashboards, I've decided to embed them onto a simple HTML file hosted on Github Pages. I'd also like to write down my insights on here.
  - I've also included some meta tags for the purposes of search engine optimization and indexing. 
    - See: https://developers.google.com/search/docs/crawling-indexing/special-tags and https://gist.github.com/lancejpollard/1978404
    - *og is for sharing previews. og refers to Open Graph tags which control how the page looks when shared on social media.