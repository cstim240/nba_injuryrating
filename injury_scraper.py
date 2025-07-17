# creates a csv file from webpage
from seleniumbase import SB
# import the SB class from the library, SB is a simplified Selenium wrapper that manages setup/teardown of the browser automatically -- no need to call quit() after completing all tasks!
from bs4 import BeautifulSoup

def removeBullet(name):
    return name.replace("• ", "")

# launch chrome browser in stealthmode using undetected-chromedriver (bypasses Cloudflare protections)
with SB(uc=True) as sb:
    # sb is the browser instance object, we can interact with the page using this

    # this url is what we scrape info from, currently just one page from PST
    url = "https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=&EndDate=&InjuriesChkBx=yes&Submit=Search&start=31850"

    # tells browser to open url and try 4 times if there's a connection failure or bot challenge 
    sb.uc_open_with_reconnect(url, 4)

    #print("Page title", sb.get_title())

    pst_html = sb.get_page_source()
    soup = BeautifulSoup(pst_html, 'html.parser')
    # print(f"here's the html: {soup.prettify()}") #prints a formatted representation of the html structure of website

    # we see that the website uses JS to dynamically load and insert real content into the DOM, we're only seeing the initial HTML with prettify --> using my browser's devtools gives use the rendered DOM
    # the important bits we wanted to see: html > body > div.container > table.datatable.center > tbody > tr align="left"
    # these table rows are the key components which contain player information

    # let's print ALL the players names for each row, if the td's in the row isn't empty let's print them!
    # first let's grab the table, there's only one tbody element in the entire html
    pst_table = soup.tbody

    """ for row in pst_table.children: #<tbody> <tr> 
        for cell in row.stripped_strings:
            print(f"\t{cell} ", end='')
        
        print("\n") """
    
    #notes: each player name has a bullet point before it
    #each row has (in-order): date, team, (acquired OR relinquished) and notes cell
    #the cells acquired and relinquished may be empty, at least one will have content

    #let's try printing just the player names, and without the bullet point
    # note: .children will include whitespace and newline nodes, and the dreaded NavigableString objects
    # alternative: using find_all("tr")
    row = pst_table.find_all("tr")
    for row in row[1:]:  
        cells = list(row.stripped_strings)
        if len(cells) >= 3:
            player_name = removeBullet(cells[2])
            print(player_name)




