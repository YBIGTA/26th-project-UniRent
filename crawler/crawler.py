import requests as re
from bs4 import BeautifulSoup as bs
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from abc import ABC, abstractmethod
from time import sleep
import boto3


class BaseCrawler(ABC):
    def __init__(self, output_dir: str, place=""):
        self.output_dir = output_dir
        self.url = ""
        self.driver = None

    def start_browser(self) -> None:
        '''start chrome browser'''
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(self.url)
        sleep(3)
        self.driver = driver

    @abstractmethod
    def scrape_reviews(self):
        pass

    def save_to_database(self) -> None:
        """Save reviews."""
        with open(os.path.join(self.output_dir, "data.json"), 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

class ThreeThreeCrawler(BaseCrawler):
    def __init__(self, output_dir, place="서대문구"):
        self.output_dir = os.path.join(output_dir, "threethree")
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = []
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode (no UI)
        # options.add_argument("--disable-gpu")  # Recommended for some systems
        self.driver:webdriver.Chrome = webdriver.Chrome(options=options)
        self.url = 'https://33m2.co.kr/webpc/search/keyword?keyword=서대문구&start_date=&end_date=&week='
        self.place = place

    def scrape_reviews(self):
        """Scrape reviews from the specified URL."""
        self.start_browser()
        driver = self.driver
        url = self.url
        place = self.place
        
        driver.get(url)
        sleep(3)
       
        s3 = boto3.client('s3')
        bucket_name = "uni-rent-bucket"
        data = []
        page = 1
        flag = True
        while flag:

            for i in range(1, 16): # to (1, 16)
                try:
                    driver.find_element(By.XPATH, f'//*[@id="div_search_result_inner"]/div[2]/a[{i}]').click()
                    sleep(5)
                    windows = driver.window_handles
                    if len(windows) > 1:
                        driver.switch_to.window(windows[1])

                    soup = bs(driver.page_source, 'html.parser')

                    room = {} 
                    # title
                    img_name = None
                    title_selector = 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong'
                    title = soup.select(title_selector)
                    if title:
                        room['title'] = title[0].text
                    else:
                        room['title'] = ""
                    
                    # images
                    if img_name:
                        parent_div = driver.find_element(By.CLASS_NAME, 'swiper-wrapper')
                        images = parent_div.find_elements(By.TAG_NAME, "img")
                        for index, img in enumerate(images):
                            img_url = img.get_attribute("src")
                            if img_url:
                                img_data = re.get(img_url).content
                                sleep(2)
                                s3.upload_fileobj(img_data, bucket_name, f'{img_name}/{index}.jpg')
                    
                    # addr
                    addr_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(1) > p'
                    addr = soup.select(addr_selector)
                    if addr:
                        room['addr'] = addr[0].text
                    else:
                        room['addr'] = ""
                    

                    # price
                    price_table = {}
                    price_selector = 'body > div.wrap > section > div > div.room_sticky > div.room_pay > p > strong'
                    price = soup.select(price_selector)
                    if price:
                        price_table['1week'] = price[0].text
                    else:
                        price_table['1week'] = ""
                    
                    room['price_table'] = price_table
                        
                    # options
                    options = []
                    option_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(5) > ul'
                    option = soup.select(option_selector)
                    if option:
                        for p in option[0].find_all('p', recursive=True):
                            options.append(p.text)

                    option_etc_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(6) > ul'
                    option_etc = soup.select(option_etc_selector)
                    if option_etc:
                        for p in option_etc[0].find_all('p', recursive=True):
                            options.append(p.text)
                    room['options'] = options
                    
                    data.append(room)
                    # Get window handles
                    windows = driver.window_handles
                    if len(windows) > 1:
                        driver.switch_to.window(windows[1])
                        driver.close()
                        driver.switch_to.window(windows[0])
                        sleep(2)
                    
                except Exception as e:
                    flag = False
                    print(e)
                    break

            try:
                next = 0
                if page == 1:
                    next = 1
                elif page % 10 == 0:
                    next = 11
                else:
                    next = page % 10 + 1
                page += 1
                driver.find_element(By.XPATH, f'//*[@id="div_search_result_inner"]/div[3]/a[{next}]').click()
                sleep(2)
            except Exception as e:
                print(page)
                print(e)
                flag = False
                
        self.data = data
                
class HowBoutHereCrawler(BaseCrawler):
    def __init__(self, output_dir: str, place="서대문구"):
        '''Constructor for JSCrawler'''
        self.output_dir = os.path.join(output_dir, "howbouthere")
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = []
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode (no UI)
        options.add_argument("--disable-gpu")  # Recommended for some systems
        self.driver:webdriver.Chrome = webdriver.Chrome(options=options)
        self.url = "https://www.yeogi.com/domestic-accommodations?keyword=%EC%84%9C%EC%9A%B8+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC&autoKeyword=%EC%84%9C%EC%9A%B8+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC&checkIn=2025-02-22&checkOut=2025-02-23&personal=2&freeForm=false"
        self.place = place
    
    def scrape_reviews(self):
        driver = self.driver
        url = self.url
        driver.get(url)
        place = self.place
        
        data = []
        i = 1
        while True:
            try:
                driver.find_element(By.XPATH, f'//*[@id="__next"]/div/main/section/div[2]/a[{i}]').click()
                sleep(2)
                windows = driver.window_handles
                if len(windows) > 1:
                    driver.switch_to.window(windows[1])
                soup = bs(driver.page_source, 'html.parser')
                room = {}
                
                title_selector = '#overview > div.css-3fvoms > div.css-mn17j9 > div.css-hn31yc > div.css-1tn66r8 > h1'
                title = soup.select(title_selector)
                
                img_dir = None
                if title:
                    room['title'] = title[0].text
                    img_dir = os.path.join(self.output_dir, room['title'])
                    os.makedirs(img_dir, exist_ok=True)
                else:
                    room['title'] = ''

                # image
                if img_dir:
                    parent_div = driver.find_element(By.XPATH, '//*[@id="overview"]/article/div[1]/ul')
                    images = parent_div.find_elements(By.TAG_NAME, "img")
                    for index, img in enumerate(images):
                        img_url = img.get_attribute("src")
                        print(img_url)
                        if img_url:
                            img_data = re.get(img_url).content
                            sleep(4)
                            with open(f"{img_dir}/{index}.jpg", "wb") as file:
                                file.write(img_data)
                    
                addr_selector = '#overview > div.css-3fvoms > div.css-y3ur5y > div.css-1insk2s > a > p'
                addr = soup.select(addr_selector)
                if addr:
                    room['addr'] = addr[0].text
                else:
                    room['addr'] = ''
                j = 1
                price_table = {}
                while True:
                    try:
                        price_selector = f'#room > div.css-g6g7mu > div:nth-child({j}) > div.css-gp2jfw > div.css-hn31yc > div.css-1a09zno > div:nth-child(2) > div.css-1rw2dq2 > div.css-zpds22 > div > div > div.css-1l31u4y > div > div > div.css-a34t1s'
                        price = soup.select(price_selector)[0].text
                        key_selector = f'#room > div.css-g6g7mu > div:nth-child({j}) > div.css-gp2jfw > div.css-zjkjbb > div.css-1ywt6mt > div'
                        key = soup.select(key_selector)[0].text
                        price_table[key] = price
                        j += 1

                    except:
                        break
                room['price_table'] = price_table
                
                j = 1
                options = []
                while True:
                    try:
                        option_selector = f'#__next > div > main > section.css-g9w49m > div.css-2nct5r > div.css-1nuurnu > div.css-1kglajm > div:nth-child({j}) > div > span'
                        option = soup.select(option_selector)[0].text
                        options.append(option)
                        j += 1
                    except:
                        break
                
                room['options'] = options
                data.append(room)

                # Get window handles
                windows = driver.window_handles
                if len(windows) > 1:
                    driver.switch_to.window(windows[1])
                    driver.close()
                    driver.switch_to.window(windows[0])
                    sleep(2)
                
                i += 1
            
            except:
                break
        
        self.data = data
    