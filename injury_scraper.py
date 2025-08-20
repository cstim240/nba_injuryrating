from seleniumbase import SB
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import random
import time

INITIAL_OFFSET = 3150 # used as part of the starting url, decremented each time we go back a page
CUTOFF_DATE = (2024, 9, 1) #YYYY, MM, DD
DB_PATH = 'records.db'

def removeBullet(name):
    return name.replace("• ", "")

def scrapePage(sb, offset, cutoff_date):
    inSeason = True
    pageCounter = 0
    while inSeason:
        # url where we begin our scrape- the most recent page, currently just one page from PST (this is from July 26, 2025)
        url = f"https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2024-09-01&EndDate=2025-08-19&ILChkBx=yes&InjuriesChkBx=yes&PersonalChkBx=yes&Submit=Search&start={offset}"

        print(f"Loading... page: {offset}")

        # tells browser to open url and try 4 times if there's a connection failure or bot challenge 
        sb.uc_open_with_reconnect(url, 4)
        sb.wait_for_element("tr")

        pst_html = sb.get_page_source()
        soup = BeautifulSoup(pst_html, 'html.parser')

        # get table, there's only one tbody element in the html
        pst_table = soup.tbody

        conn = sqlite3.connect('records.db')
        cursor = conn.cursor()

        # process scraped data and insert into DB
        row = pst_table.find_all("tr")
        found_old_date = False # to keep track if we're at the page where CUTOFF_DATE is located
        for row in row[1:]:  #skips the header row
            cells = list(row.stripped_strings)
            if len(cells) < 4:
                continue #skips an empty row, unfortunately these are present in PST
            date = cells[0]
            player_name = removeBullet(cells[2])
            notes = cells[3]

            current_date = datetime.strptime(date, "%Y-%m-%d").date()
            if current_date < cutoff_date:
                found_old_date = True
                continue # skips this row but keep processing the page

            print(f"Saving player: {player_name}, injury: {notes}")

            cursor.execute('''
                INSERT OR IGNORE INTO records
                (name, date, notes)
                VALUES (?, ?, ?)
            ''', (player_name, date, notes))

            # After processing the entire page, check if we should stop
            if found_old_date:
                inSeason = False
            # this fixes our input errors on the boundary which was skewing our results -- ie. Kristaps Porzingis was injured on 9-24
            # but because we start our scraping from the top of the page, we prematurely end processing when we encounter Jarrett Allen's row which has 4-30-2024, its way before the CUTOFF_DATE so we initially had a break there, meaning we didn't insert the porzingis injury --> resulting in the output in csv as total injury days = 9 days (if you we're watching the 2024-25 season you would know Porzingis was gone for half the season)

        conn.commit()
        conn.close()
        print(f"Loading..")

        pageCounter += 1
        offset -= 25 # move to the previous page

        if offset < 0:
            break

        sleepy_time = random.uniform(1, 2.5)
        time.sleep(sleepy_time)
        print(f"Sleeping for {sleepy_time} seconds! They won't know I'm a bot hehe!")
    
    print(f"Done! We scraped {pageCounter} pages!")

def createDB():
    # Create DB once prior to looping
    conn = sqlite3.connect(DB_PATH)
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

def main():
    cutoff_date = datetime(*CUTOFF_DATE).date() #yyyy, mm, dd of date we want to scrape to

    offset = INITIAL_OFFSET

    createDB()
    with SB(uc=True, headless=True) as sb:
        scrapePage(sb, offset, cutoff_date)

if __name__ == "__main__":
    main()



