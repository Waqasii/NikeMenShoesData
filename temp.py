from selenium import webdriver
from bs4 import BeautifulSoup as bs
import bs4
import requests
import time
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import re

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
        # time.sleep(3)
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:  
            
            try:
                print('---------PopUpcheck--------')
                WebDriverWait(browser, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close Menu"]'))).click()
                match=False
                print('---------PopUp Closed--------')
            except:
                match=True
                print('---------PopUp Couldn`t Closed--------')
        
            
            
        
    
    
    
    review_dates=getReviewsDate(browser)
    
           
    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    soup = bs(source_data,features="html.parser")
    size= soup.find_all('label', class_ = 'css-xf3ahq')
    # print(size)
    sizes=[]
    for s in size:
        sizes.append(s.text)
    
    print('Sizes:',sizes) 
    browser.close()
    
    
    return sizes,review_dates



def getReviewsDate(browser):
    
    # check if reviews availavle or not
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    soup = bs(source_data,features="html.parser")
    rev_heading= soup.find('summary',attrs={ "class" : "css-ov1ktg" })
    rev_number=rev_heading.find('h3',attrs={ "class" : "css-xd87ek" })
    number=rev_number.find('span').text
    
    # print(number)
    number=(re.findall(r"\(\s*\+?(-?\d+)\s*\)", number)[0])
    
    if(int(number)<=0):
        return 'N/A'
        
    
    

    
    while(True):
       try:
        #    button = browser.find_element_by_xpath("//button[@class='ncss-btn-primary-light mod-u-underline css-1nglku6']")
           
           more_review_container = browser.find_element_by_xpath("//p[@class='mt10-sm mb10-sm']")
           browser.execute_script("arguments[0].scrollIntoView()", more_review_container)
           
           
           more_review_button = browser.find_element_by_xpath("//button[@data-test='more-reviews']")
           browser.implicitly_wait(5)
           ActionChains(browser).move_to_element(more_review_button).click(more_review_button).perform()
           
           print('More Reviews Button  Clicked')
           if(browser.find_element_by_xpath("//div[@id= 'TT3rShowMore']")):
               break
           
       except:
           button = browser.find_element_by_xpath("//div[@class= 'css-1n9iiad']")
           browser.execute_script("arguments[0].scrollIntoView()", button)
           # print('Not Clicked')
           try:
               browser.implicitly_wait(10)
               ActionChains(browser).move_to_element(button).click(button).perform()
               print('clicked on Review Button')
           except:
               # button.location_once_scrolled_into_view
               # print("Couldn't Click on Any")
               print('Checking Again')
    
    
    # Load More Reviews
    while(True):
        try:
            load_more = browser.find_element_by_xpath("//div[@id= 'TT3rShowMore']")
            browser.execute_script("arguments[0].scrollIntoView()", load_more)
            time.sleep(5)
            # browser.implicitly_wait(10)
            ActionChains(browser).move_to_element(load_more).click(load_more).perform()
            print('Click on Load  More Review Button')
            # browser.implicitly_wait(40)
            
        except:
            print('Reviews Loading Complete!')
            break
            
        
    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    soup = bs(source_data,features="html.parser")
    dates_container= soup.find_all('div',attrs={ "itemprop" : "dateCreated" })
    print('Total Reviews:',len(dates_container))
    
    dates=[]
    for date in dates_container:
        dates.append(date.text)
        print(date.text)
        
     
    return dates    

getSize('https://www.nike.com/t/sb-blazer-low-gt-skate-shoe-yKeNdm/704939-005')