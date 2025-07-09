#creates a csv file from webpage
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome() #start session
url = "https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=&EndDate=&InjuriesChkBx=yes&Submit=Search&start=31850"

driver.get(url) #take action on browser

title = driver.title #request browser info

#we want to make sure element is on page before attempting to locate it, implicit wait is used here
driver.implicitly_wait(2.0)

print(f"the website's title is {title}\n")

driver.quit()
