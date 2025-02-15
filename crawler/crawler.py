import requests as re
from bs4 import BeautifulSoup as bs
import pandas as pd 
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from time import sleep


class BaseCrawler(ABC):
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    @abstractmethod
    def start_browser(self):
        pass

    @abstractmethod
    def scrape_reviews(self):
        pass

    @abstractmethod
    def save_to_database(self):
        pass

class ThreeThreeCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.output_dir = os.path.join(output_dir, "threethree.json")
        self.data = []
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode (no UI)
        # options.add_argument("--disable-gpu")  # Recommended for some systems
        self.driver:webdriver.Chrome = webdriver.Chrome(options=options)
        self.url = f"https://33m2.co.kr/webpc/search/keyword?keyword=서대문구&start_date=2025-02-12&end_date=2025-02-18&week=1"

    def start_browser(self) -> None:
        '''start chrome browser'''
        driver:webdriver.Chrome = self.driver
        driver.maximize_window()
        driver.get(self.url)
        sleep(3)

    def scrape_reviews(self):
        """Scrape reviews from the specified URL."""
        self.start_browser()
        driver = self.driver
        url = self.url
        
        driver.get(url)
        sleep(3)
        
        # # 리뷰 더보기로 이동
        # more_btn=browser.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]')
        # more_btn.click()
        # sleep(3)
        
        # # div태그 스크롤 
        # js_scripts = '''
        # let aa = document.getElementsByClassName('section-scrollbox')[0];
        # aa.scrollBy(0,10000);
        # '''
        # browser.execute_script(js_scripts)
        # sleep(3) 
        
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
                    title_selector = 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong'
                    title = soup.select(title_selector)
                    if title:
                        room['title'] = title[0].text
                    else:
                        room['title'] = ""
                    
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
                
    def save_to_database(self) -> None:
        """Save reviews."""
        with open(self.output_dir, 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)