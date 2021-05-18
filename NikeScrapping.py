from numpy.core.fromnumeric import size
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import bs4
import requests
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver import ActionChains
import re


class NikeShoesData():
    
    def __init__(self,link=None,category='General'):
        if(link is not None):
            
            self.df=pd.DataFrame(columns = ['Title', 'Style Code', 'Category', 'Size', 'Description', 'Colors', 'Status', 'Rating', 'Picture', 'Price','Link','Review Dates'])
            
            self.link=link
            self.categ=category
            
            # I used Firefox; you can use whichever browser you like.
            self.browser = webdriver.Chrome(executable_path="chromedriver.exe")

            # Ask Selenium to get the URL you're interested in.
            self.browser.get(self.link)
            
            # start scrapping process
            self.startLoading()
            self.Scrapping()
    
    def startLoading(self):
        '''
        This method will use to load all product by scrolling down to the page
        '''
        # Selenium script to scroll to the bottom, wait 3 seconds for the next batch of data to load, then continue scrolling.  It will continue to do this until the page stops loading new data.
        lenOfPage = self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        
        # this loop is to check end of loading more content or maybe popup shown 
        # so it will handle both condition
         
        while(match==False):
            time.sleep(2)
            lastCount = lenOfPage
            lenOfPage = self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount==lenOfPage:
                try:
                    print('---------PopUpcheck--------')
                    try:
                        WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close Menu"]'))).click()
                    except:
                        WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-var="CloseBtn"]'))).click()
                        
                    match=False
                    print('---------PopUp Closed--------')
                except:
                    match=True
                    print('---------PopUp Didn`t Found!!--------')
                    print('---------Laoding Products Completed!--------')
    
    def Scrapping(self):
        # Now that the page is fully scrolled, grab the source code.
        source_data = self.browser.page_source

        # Throw your source into BeautifulSoup and start parsing!
        soup = bs(source_data,features="html.parser")
        products= soup.find_all('div', class_ = 'product-card')
        print('Total Products Found=',len(products))
        
        i=0
        #iterate over all availavle products cards one by one 
        for p in products:
            prod_link=p.find('a' , attrs={'class': 'product-card__img-link-overlay', 'id':None, 'style':None})
            prod_link=prod_link['href']
            
            prod_status=p.find('div' , attrs={'class': 'product-card__messaging accent--color', 'id':None, 'style':None})
            try:
                prod_status=prod_status.text
            except:
                prod_status='Available'
                
            # print(prod_link)
            # print(prod_status)
            try:
                self.getProduct(prod_link,prod_status)
                self.saveDatacsv()
            except:
                print(f'**********************\nError!\nLink:{prod_link}\nStaus{prod_status}')

            # if(i>=2):
            #     break
            # else:
            #     i+=1
        
    def getProduct(self,link,prod_status):
        '''
        This method will get the link of product and status of product, then will open that link to get more details of it 
        '''
        print('*****************************')
        print('Link of Product:',link)
        print('Status:',prod_status)
        
        if(prod_status=='Coming Soon'):
            self.comingSoon(link)
        elif('SNKRS' in prod_status):
            self.SNKRS(link)
        else:
            
            self.Available(link,prod_status)
                   
    def comingSoon(self,link):
        # print('--------Coming Soon -----------')
        page=requests.get(link)
        content=page.content
        prod_soup=bs(content,'html.parser')
        
        title=prod_soup.find("h1",attrs={ "id" : "pdp_product_title" })
        title=title.text
        
        picture=prod_soup.find("img",attrs={ "data-fade-in" : "css-147n82m" })
        picture=picture['src']
        
        avail_size='N/A'
        status='Coming Soon'
        
        # getting description,price,styleCode,colors
        info_container=prod_soup.find("div",attrs={ "class" : "description-preview body-2 css-1pbvugb" })
        
        description=info_container.find("p").text
        
        colors=info_container.find("li",attrs={ "class" : "description-preview__color-description ncss-li" })
        colors=str(colors.text).split(sep=':')[1]
        
        style_code=info_container.find("li",attrs={ "class" : "description-preview__style-color ncss-li" })
        style_code=str(style_code.text).split(sep=':')[1]
        
        rating='N/A'
        
        price=prod_soup.find("div",attrs={ "class" : "product-price css-11s12ax is--current-price" })
        price=price.text
        
        # adding in dataframe
        row=[]
        row.append(title)
        row.append(style_code)
        row.append(self.categ)
        row.append(avail_size)
        row.append(description)
        row.append(colors)
        row.append(status)
        row.append(rating)
        row.append(picture)
        row.append(price)
        row.append(link)
        row.append('N/A')
        
        
        self.df.loc[len(self.df)] = row
        
        
        # print('------Title:',title)
        # print('------Picture:',picture)
        # print('------Available Size:',avail_size)
        # print('------Description:',description)
        # print('------Style Code:',style_code)
        # print('------Colors:',colors)
        # print('------Rating:',rating)
        # print('------Price:',price)
        # print('------Status:',status)
    
    def Available(self,link,status):
        
        # print(f'--------{status}-----------')
        page=requests.get(link)
        content=page.content
        prod_soup=bs(content,'html.parser')
        
        try:
            avail_size,review_dates=getSize(link)
        except:
            avail_size='N/A'
    
        title=prod_soup.find("h1",attrs={ "id" : "pdp_product_title" })
        title=title.text
        
        picture=prod_soup.find("img",attrs={ "data-fade-in" : "css-147n82m" })
        picture=picture['src']
        
        status=status
        
        # getting description,price,styleCode,colors
        info_container=prod_soup.find("div",attrs={ "class" : "description-preview body-2 css-1pbvugb" })
        
        description=info_container.find("p").text
        
        colors=info_container.find("li",attrs={ "class" : "description-preview__color-description ncss-li" })
        colors=str(colors.text).split(sep=':')[1]
        
        style_code=info_container.find("li",attrs={ "class" : "description-preview__style-color ncss-li" })
        style_code=str(style_code.text).split(sep=':')[1]
        
        try:
            rating_container=prod_soup.find("div",attrs={ "class" : "product-review mb10-sm" })
            rating=rating_container.find("p",attrs={ "class" : "d-sm-ib pl4-sm" }).text
        except:
            rating='N/A'
            
        try:
            price=prod_soup.find("div",attrs={ "class" : "product-price css-11s12ax is--current-price" })
            price=price.text
        except:
            price=prod_soup.find("div",attrs={ "class" : "product-price is--current-price css-s56yt7" })
            price=price.text
        
        
        # adding in dataframe
        row=[]
        row.append(title)
        row.append(style_code)
        row.append(self.categ)
        row.append(avail_size)
        row.append(description)
        row.append(colors)
        row.append(status)
        row.append(rating)
        row.append(picture)
        row.append(price)
        row.append(link)
        row.append(review_dates)
        
        self.df.loc[len(self.df)] = row
        
        # print('------Title:',title)
        # print('------Picture:',picture)
        # print('------Available Size:',avail_size)
        # print('------Description:',description)
        # print('------Style Code:',style_code)
        # print('------Colors:',colors)
        # print('------Rating:',rating)
        # print('------Price:',price)
        # print('------Status:',status)
    
    def SNKRS(self,link):
        # print('--------SNKRS-----------')
        page=requests.get(link)
        content=page.content
        prod_soup=bs(content,'html.parser')
        
        avail_size='N/A'
        
        # size_container=prod_soup.find("div",attrs={ "class" : "prod_soup" })
        # # .findAll("div",attrs={ "class" : "mt2-sm css-1j3x2vp" })  #mt2-sm css-1j3x2vp
        # print(size_container)
        # return

        contianer=prod_soup.find("div",attrs={ "class" : "product-info ncss-col-sm-12 full" })
        
        title=contianer.find("h5",attrs={ "class" : "headline-1 pb3-sm" })
        title=title.text
        
        price=contianer.find("div",attrs={ "class" : "headline-5 pb6-sm fs14-sm fs16-md" })
        price=price.text
       
        # # contianer=prod_soup.find("div",attrs={"class" : "full js-photo"})
        # picture=prod_soup.findAll("img")[2]
        # picture=picture['src']
        # print(picture)
        picture='N/A'
        
    
        status='SNKRS'
        
        # getting description,price,styleCode,colors
        info_container=prod_soup.find("div",attrs={ "class" : "description-text text-color-grey" })
        
        description=info_container.find("p").text
        
        colors='N/A'
        
        style_code='N/A'
        rating='N/A'
        
        
        
        # adding in dataframe
        row=[]
        row.append(title)
        row.append(style_code)
        row.append(self.categ)
        row.append(avail_size)
        row.append(description)
        row.append(colors)
        row.append(status)
        row.append(rating)
        row.append(picture)
        row.append(price)
        row.append(link)
        row.append('N/A')
        
        self.df.loc[len(self.df)] = row

        # print('------Title:',title)
        # print('------Picture:',picture)
        # print('------Available Size:',avail_size)
        # print('------Description:',description)
        # print('------Style Code:',style_code)
        # print('------Colors:',colors)
        # print('------Rating:',rating)
        # print('------Price:',price)
        # print('------Status:',status)
    
    
    def saveDatacsv(self):
        # Considering certain columns for dropping duplicates
        self.df.drop_duplicates(subset=['Link'])
        self.df.to_csv(self.categ+".csv")
        print('file Saved SuccessFully!!')


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
        print('Review Not Available')
        return 'N/A'
    
    check=0
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
               check+=1
               # button.location_once_scrolled_into_view
               # print("Couldn't Click on Any")
               print('Checking Again')
               if(check==3):
                   break
    
    
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


if __name__ == '__main__':
    # starting time
    start = time.time()
    # main link
    # NikeShoesData("https://www.nike.com/w/mens-shoes-nik1zy7ok",'Mens Shoes & Sneakers')
    
    # just for testing purpose
    NikeShoesData("https://www.nike.com/w/mens-skateboarding-shoes-8mfrfznik1zy7ok",'Mens Shoes & Sneakers')
    
    # end time
    end = time.time()

    t=float("{:.2f}".format((end - start)/60))
    # total time taken
    print(f"Time taken:{t} Minutes")