from seleniumbase import SB
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import random
import time

cutoff = datetime(2024, 9, 1).date() #yyyy, mm, dd of date we want to scrape to
currentDate = datetime.today()
print(f"Today's date: {currentDate}")

inSeason = True
pageCounter = 0

def removeBullet(name):
    return name.replace("• ", "")

with SB(uc=True, headless=True) as sb:
    offset = 31850 #used as part of the url, decremented each time we go back a page

    # Create DB once prior to looping
    conn = sqlite3.connect('records.db')
    cursor = conn.cursor()

    cursor.execute(''' DROP TABLE IF EXISTS records ''')

    # create the players table
    cursor.execute('''
        CREATE TABLE records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT,
            notes TEXT,
            UNIQUE(name, date)
        )
    ''')

    conn.commit()
    conn.close()

    while inSeason:
        # url where we begin our scrape- the most recent page, currently just one page from PST (this is from July 26, 2025)
        url = f"https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=&EndDate=&InjuriesChkBx=yes&Submit=Search&start={offset}"

        print(f"Loading... page: {offset}")

        # tells browser to open url and try 4 times if there's a connection failure or bot challenge 
        sb.uc_open_with_reconnect(url, 4)

        pst_html = sb.get_page_source()
        soup = BeautifulSoup(pst_html, 'html.parser')

        # get table, there's only one tbody element in the html
        pst_table = soup.tbody

        conn = sqlite3.connect('records.db')
        cursor = conn.cursor()

        # process scraped data and insert into DB
        row = pst_table.find_all("tr")
        for row in row[1:]:  #skips the header row
            cells = list(row.stripped_strings)
            if len(cells) < 4:
                continue #skips an empty row, unfortunately these are present in PST
            date = cells[0]
            player_name = removeBullet(cells[2])
            notes = cells[3]

            currentDate = datetime.strptime(date, "%Y-%m-%d").date()
            if currentDate < cutoff:
                inSeason = False
                break # stop processing rest of page

            cursor.execute('''
                INSERT INTO records
                (name, date, notes)
                VALUES (?, ?, ?)
            ''', (player_name, date, notes))

        conn.commit()
        conn.close()
        print(f"Loading..")

        pageCounter += 1
        offset -= 25 # move to the previous page

        sleepy_time = random.uniform(1, 2.5)
        time.sleep(sleepy_time)
        print(f"Sleeping for {sleepy_time} seconds! They won't know I'm a bot hehe!")
    
    print(f"Done! We scraped {pageCounter} pages!")

            




