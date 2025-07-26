# creates a csv file from webpage
from seleniumbase import SB
from bs4 import BeautifulSoup
import sqlite3
import os

def removeBullet(name):
    return name.replace("• ", "")

with SB(uc=True) as sb:
    # url where we begin our scrape, currently just one page from PST
    url = "https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=&EndDate=&InjuriesChkBx=yes&Submit=Search&start=31850"

    # tells browser to open url and try 4 times if there's a connection failure or bot challenge 
    sb.uc_open_with_reconnect(url, 4)

    pst_html = sb.get_page_source()
    soup = BeautifulSoup(pst_html, 'html.parser')

    # get table, there's only one tbody element in the html
    pst_table = soup.tbody

    conn = sqlite3.connect('records.db')
    cursor = conn.cursor()

    # create the players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT,
            notes TEXT
        )
    ''')

    # process scraped data and insert into DB
    row = pst_table.find_all("tr")
    for row in row[1:]:  #skips the header row
        cells = list(row.stripped_strings)
        date = cells[0]
        player_name = removeBullet(cells[2])
        notes = cells[3]

        cursor.execute('''
            INSERT INTO records
            (name, date, notes)
            VALUES (?, ?, ?)
        ''', (player_name, date, notes))

    conn.commit()
    conn.close()
        




