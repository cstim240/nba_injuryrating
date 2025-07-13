#creates a csv file from webpage
from seleniumbase import SB
#import the SB class from the library, SB is a simplified Selenium wrapper that manages setup/teardown of the browser automatically -- no need to call quit() after completing all tasks!

#launch chrome browser in stealthmode using undetected-chromedriver (bypasses Cloudflare protections)
with SB(uc=True) as sb:
    #sb is the browser instance object, we can interact with the page using this

    #this url is what we scrape info from, currently just one page from PST
    url = "https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=&EndDate=&InjuriesChkBx=yes&Submit=Search&start=31850"

    # tells browser to open url and try 4 times if there's a connection failure or bot challenge 
    sb.uc_open_with_reconnect(url, 4)

    print("Page title", sb.get_title())


