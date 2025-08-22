import sqlite3
from datetime import datetime, date 
import pandas as pd

CUTOFF_YEAR = 2025
CUTOFF_DAY = 19
CUTOFF_MONTH = 8 
CUTOFF_DATE = date(CUTOFF_YEAR, CUTOFF_MONTH, CUTOFF_DAY)

def exportToCSV(hashmap):
    # with our hashmap input, pandas treats the out keys (player names) as columns, not rows
    # so we have to transpose to get the correct orientation
    df = pd.DataFrame(hashmap).transpose()
    df.to_csv("aggregateInjuries.csv")

# returns a hashmap of players with their combined injured days, injuries sustained
def aggregateInjuryPeriods(periods):
    aggregateInjuryPer = {} # key = name, value = the other stuff

    for period in periods:
        name = period["name"]
        
        if name in aggregateInjuryPer:
            # update existing entry
            aggregateInjuryPer[name]["injury_count"] += 1
            aggregateInjuryPer[name]["injured_days"] += period["recovery_days"]
            aggregateInjuryPer[name]["injuries_sustained"].append(period["injury_note"])
        else:
            # create new entry in hashmap
            aggregateInjuryPer[name] = {
                "injury_count" : 1,
                "injured_days" : period["recovery_days"],
                "injuries_sustained" : [period["injury_note"]]
            }
    
    print(f"aggregation done!")
    return aggregateInjuryPer

# returns a list of injury periods, along with player name, injury date, return date, recovery date, type of injury
def getInjuryPeriods(rows):
    # source is a list containing all the rows in the form: [ (name, date, record), ... ,(name, date, record)], we want to turn this into the injury_periods list where the components are separated into a dictionary object, easier to analyze!

    injury_periods = []
    # note there will be duplicates in terms of player name, the same player can get injured multiple times

    #dict/hashmap to help us keep track of unpaired injury_period object
    currently_injured = {} # key = player name, value = (injury_date, injury_note)

    for row in rows:
        name = row[0]
        current_date = datetime.strptime(row[1], "%Y-%m-%d").date() # from str to datetime obj
        note = row[2].strip().lower()

        #case 1: player sustains injury from this season
        if note != "returned to lineup" and note != "activated from il" and name not in currently_injured:
            currently_injured[name] = (current_date, note)
            print(f"Case 1: Adding {name} to the injured list with injury: {note}!")

        #case 2: player returns from injury from this season
        elif (note == "returned to lineup" or note == "activated from il") and name in currently_injured:
            injury_date, injury_note = currently_injured.pop(name)
            injury_periods.append({
                "name": name, 
                "injury_date": injury_date,
                "return_date": current_date,
                "injury_note": injury_note,
                "recovery_days": (current_date - injury_date).days
            })
            print(f"Case 2: Adding {injury_note} to {name}'s file")

        #case 3: player returns from injury from past season
        elif (note == "returned to lineup" or note == "activated from il") and name not in currently_injured:
            print(f"Ignored case for {name}, no matching injury entry, note: {note}")
            continue #skip
    
    #case 4: players who got injured and never returned this season?
    # we use our CUTOFF_DATE constant

    for name, (injury_date, injury_note) in currently_injured.items():
        # create an injury period object
        injury_periods.append({
            "name": name, 
            "injury_date": injury_date,
            "return_date": current_date,
            "injury_note": injury_note,
            "recovery_days": (CUTOFF_DATE - injury_date).days
        })
        # print(f"For player {name}, adding injury note: {injury_note}")
    #we give them the arbitrary return date in form of cutoff

    return injury_periods

def fetchRows(): 
    conn = sqlite3.connect('records.db')
    cur = conn.cursor()

    # we manually exclude a few erroneuous values placed by PST in the WHERE clause
    cur.execute('''
        SELECT name, date, notes
        FROM records
        WHERE name <> "illness (DTD)" OR name <> "sore lower back (DTD)" OR name <> "fractured rib (out indefinitely)" OR name <> "torn ACL in left knee (out for season)"
        ORDER BY name, date
    ''')

    rows = cur.fetchall()

    conn.close()

    # print(f"rows: {rows}")

    return rows

def main():
    rows = fetchRows()
    periods = getInjuryPeriods(rows) # pair injury date and return to lineup into a 'single injury period' -- raw unmanipulated data
    # print(f"Periods: {periods}")
    # sum the injury duration/s from each player's injury period(s)
    sumAg = aggregateInjuryPeriods(periods) 
    exportToCSV(sumAg)


if __name__ == "__main__":
    main()