import sqlite3
import datetime

def getInjuryPeriods(rows):
    # source is a list containing all the rows in the form: [ (name, date, record), ... ,(name, date, record)], we want to turn this into the injury_periods list where the components are separated into a dictionary object, easier to analyze!

    injury_periods = []
    # note there will be duplicates in terms of player name, the same player can get injured multiple times

    #dict/hashmap to help us keep track of unpaired injury_period object
    currently_injured = {} # key = player name, value = (injury_date, injury_note)

    for row in rows:
        name = row[0]
        date = row[1]
        note = row[2].strip().lower()

        #case 1: player sustains injury from this season
        if note != "returned to lineup" and name not in currently_injured:
            currently_injured[name] = (date, note)

        #case 2: player returns from injury from this season
        elif note == "returned to lineup" and name in currently_injured:
            injury_date, injury_note = currently_injured.pop(name)
            injury_periods.append({
                "name": name, 
                "injury_date": injury_date,
                "return_date": date,
                "injury_note": injury_note,
            })

        #case 3: player returns from injury from past season
        elif note == "returned to lineup" and name not in currently_injured:
            continue #skip
    
    #case 4: players who got injured and never returned this season?
    cutoff_date = datetime.date(2025, 7, 26) #YYYY, MM, DD

    for name, (injury_date, injury_note) in currently_injured.items():
        injury_periods.append({
            "name": name, 
            "injury_date": injury_date,
            "return_date": date,
            "injury_note": injury_note,
        })
    #we give them the arbitrary return date in form of cutoff

    return injury_periods

def fetchRows(): 
    conn = sqlite3.connect('records.db')
    cur = conn.cursor()

    cur.execute('''
        SELECT name, date, notes
        FROM records
        WHERE name <> "illness (DTD)" AND name <> "sore lower back (DTD)"
        ORDER BY name, date
    ''')

    rows = cur.fetchall()

    conn.close()

    return rows

def main():
    rows = fetchRows()
    periods = getInjuryPeriods(rows)
    # sum the injury duration from each player's periods combined

if __name__ == "__main__":
    main()