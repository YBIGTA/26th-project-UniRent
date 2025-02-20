import requests as re
from bs4 import BeautifulSoup as bs
import pandas as pd 
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from time import sleep


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
        super().__init__(output_dir)
        self.output_dir = os.path.join(output_dir, "threethree")
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = []
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode (no UI)
        # options.add_argument("--disable-gpu")  # Recommended for some systems
        self.driver:webdriver.Chrome = webdriver.Chrome(options=options)
        self.url = f"https://33m2.co.kr/webpc/guest/main"
        self.place = place

    def scrape_reviews(self):
        """Scrape reviews from the specified URL."""
        self.start_browser()
        driver = self.driver
        url = self.url
        place = self.place
        
        driver.get(url)
        sleep(3)
        
        driver.find_element(By.XPATH, '//*[@id="btn_hide_notice_today"]').click()
        sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="txt_search_keyword"]').send_keys(place)
        sleep(3)
        driver.find_element(By.XPATH, '//*[@id="btn_search"]').click()
        sleep(3)
        
        data = []
        page = 1
        flag = True
        while flag:

            for i in range(1, 16):
                try:
                    driver.find_element(By.XPATH, f'//*[@id="div_search_result_inner"]/div[2]/a[{i}]').click()
                    sleep(5)
                    windows = driver.window_handles
                    if len(windows) > 1:
                        driver.switch_to.window(windows[1])

                    soup = bs(driver.page_source, 'html.parser')

                    room = {} 

                    # title
                    img_dir = None
                    title_selector = 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong'
                    title = soup.select(title_selector)
                    if title:
                        room['title'] = title[0].text
                        img_dir = os.path.join(self.output_dir, room['title'])
                        os.makedirs(img_dir, exist_ok=True)
                    else:
                        room['title'] = ""
                    
                    # images
                    if img_dir:
                        parent_div = driver.find_element(By.CLASS_NAME, 'swiper-wrapper')
                        images = parent_div.find_elements(By.TAG_NAME, "img")
                        for index, img in enumerate(images):
                            img_url = img.get_attribute("src")
                            print(img_url)
                            if img_url:
                                img_data = re.get(img_url).content
                                sleep(4)
                                with open(f"{img_dir}/{index}.jpg", "wb") as file:
                                    file.write(img_data)
                    
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
                    next = 10
                else:
                    next = (page + 1) % 10
                page = (page + 1) % 10
                driver.find_element(By.XPATH, f'//*[@id="div_search_result_inner"]/div[3]/a[{next}]').click()
                sleep(2)
            except Exception as e:
                print(e)
                flag = False
                
        self.data = data
                
class YanoljaCrawler(BaseCrawler):
    def __init__(self, output_dir: str, place="서대문구"):
        '''Constructor for JSCrawler'''
        super().__init__(output_dir)
        self.output_dir = os.path.join(output_dir, "yanolja.json")
        self.data = []
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode (no UI)
        options.add_argument("--disable-gpu")  # Recommended for some systems
        self.driver:webdriver.Chrome = webdriver.Chrome(options=options)
        self.url = f"https://www.yanolja.com/motel/r-900400?pageKey=1739609488992"
        
    def scrape_urls(self) -> list:
        """Scrape reviews from the specified URL."""
        self.start_browser()
        driver = self.driver
        url = self.url
        
        driver.get(url)
        sleep(3)
        
        # div태그 스크롤 
        # for i in range(20):
        #     driver.execute_script("window.scrollBy(0, 100);")
        #     sleep(0.1)

        urls = []
        soup = bs(driver.page_source, 'html.parser')
        i = 2
        while True:
            try:
                a_selector = f'#__next > div > main > section > div.PlaceListBody_listContainer__2qFG1 > div:nth-child({i}) > a'
                a = soup.select(a_selector)[0]
                motel_url = f'https://www.yanolja.com{a.get("href")}'
                urls.append(motel_url)
                i += 1
            except:
                break
        
        driver.quit()
        
        return urls

    def scrape_reviews(self):
        urls = self.scrape_urls()
        
        data = []
        for url in urls:
            options = Options()
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            sleep(4)

            soup = bs(driver.page_source, 'html.parser')
            room = {}

            title_selector = '#__next > div > div > main > article > div.css-1cc3d9 > div > div.css-nmmkf9 > div.css-11vo59c > h1'
            title = soup.select(title_selector)
            if title:
                room['title'] = title[0].text
            else:
                room['title'] = ''
                
            addr_selector = '#__next > div > div > main > article > div.css-c45a2y > div > div:nth-child(3) > section > div > div > div.css-cxbger > div.address.css-3ih6hc > span'
            addr = soup.select(addr_selector)
            if addr:
                room['addr'] = addr[0].text
            else:
                room['addr'] = ''
            
            price = {}
            day_selector = '#__next > div > div > main > article > div.css-c45a2y > div > div:nth-child(2) > div > div.css-1cvl589 > div:nth-child(1) > div > div > section.room-rate-plan-container.css-15qkreq > div:nth-child(1) > a > div.css-19f5u8z > div.css-f586hh > div.rack_price'
            day = soup.select(day_selector)
            if day:
                price['숙박'] = day[0].text
            else:
                price['숙박'] = ''
            hour_selector = '#__next > div > div > main > article > div.css-c45a2y > div > div:nth-child(2) > div > div.css-1cvl589 > div:nth-child(1) > div > div > section.room-rate-plan-container.css-15qkreq > div:nth-child(2) > a > div.css-1q7riaf > div.css-1axapta > div > span.price'
            hour = soup.select(hour_selector)
            if hour:
                price['대실'] = hour[0].text
            else:
                price['대실'] = ''
            room['price_table'] = price

            options = []
            service_selector = '#__next > div > div > main > article > div.css-c45a2y > div > div:nth-child(6) > div > div > div.css-19tl48v > div:nth-child(2)'
            service = soup.select(service_selector)
            if service:
                i = 1
                for opt in service[0].find_all('div', recursive=False):
                    opt_selector = f'#__next > div > div > main > article > div.css-c45a2y > div > div:nth-child(6) > div > div > div.css-19tl48v > div:nth-child(2) > div:nth-child({i}) > span:nth-child(2)'
                    opt = soup.select(opt_selector)
                    if opt:
                        options.append(opt[0].text)
                    i += 1
            
            service_selector = '#__next > div > div > main > article > div.css-c45a2y > div > div:nth-child(6) > div > div > div.css-19tl48v > div:nth-child(4)'
            service = soup.select(service_selector)
            if service:
                i = 1
                for opt in service[0].find_all('div', recursive=False):
                    opt_selector = f'#__next > div > div > main > article > div.css-c45a2y > div > div:nth-child(6) > div > div > div.css-19tl48v > div:nth-child(4) > div:nth-child({i}) > span'
                    opt = soup.select(opt_selector)
                    if opt:
                        options.append(opt[0].text)
                    i += 1
            room['options'] = options
            data.append(room)
            driver.quit()
        
        self.data = data

class HowBoutHereCrawler(BaseCrawler):
    def __init__(self, output_dir: str, place="서대문구"):
        '''Constructor for JSCrawler'''
        super().__init__(output_dir)
        self.output_dir = os.path.join(output_dir, "howbouthere.json")
        self.data = []
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode (no UI)
        options.add_argument("--disable-gpu")  # Recommended for some systems
        self.driver:webdriver.Chrome = webdriver.Chrome(options=options)
        self.url = "https://www.yeogi.com"
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
                
                if title:
                    room['title'] = title[0].text
                else:
                    room['title'] = ''
                    
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
    