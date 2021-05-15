from selenium import webdriver
from bs4 import BeautifulSoup as bs
import bs4
import requests
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



def getSize(link):
    # I used Firefox; you can use whichever browser you like.
    browser = webdriver.Chrome(executable_path="H:\Scrapping\FlipKart_Scraping\chromedriver.exe")

    # Tell Selenium to get the URL you're interested in.
    browser.get(link)


    # Selenium script to scroll to the bottom, wait 3 seconds for the next batch of data to load, then continue scrolling.  It will continue to do this until the page stops loading new data.
    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            try:
                print('---------PopUpcheck--------')
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close Menu"]'))).click()
                match=False
                print('---------PopUp Closed--------')
            except:
                match=True
                print('---------PopUp Couldn`t Closed--------')
            
    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    soup = bs(source_data,features="html.parser")
    size= soup.find_all('label', class_ = 'css-xf3ahq')
    # print(size)
    sizes=[]
    for s in size:
        sizes.append(s.text)
    browser.close()
    return sizes
     
            
        
size=getSize('https://www.nike.com/t/zoomx-invincible-run-flyknit-mens-running-shoe-NgvDVX/CT2228-101')    
print(size)      


