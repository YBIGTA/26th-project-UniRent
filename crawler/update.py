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


def threethree(prevList):
    data = {"new": [],
            "delete": []}
    currList = []

    s3 = boto3.client('s3')
    bucket_name = "uni-rent-bucket"
    
    url = 'https://33m2.co.kr/webpc/search/keyword?keyword=서대문구&start_date=&end_date=&week='
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    sleep(3)

    page = 1
    flag = True
    while flag:
        for i in range(1, 16):
            try:
                soup = bs(driver.page_source, 'html.parser')
                title_selector = f'#div_search_result_inner > div.result_room > a:nth-child({i}) > dl > dd.room_name'
                title = soup.select(title_selector)[0].text
                currList.append(title)

                if title in prevList:
                    continue
                print(title)

                driver.find_element(By.XPATH, f'//*[@id="div_search_result_inner"]/div[2]/a[{i}]').click()
                sleep(3)

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
                            sleep(4)
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
                
                data['new'].append(room)
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
            print(e)
            flag = False
        
    # Find eliminated elements
    eliminated = list(set(prevList) - set(currList))

    # Store in data dictionary
    data["delete"] = eliminated
    return data
    

def howbouthere(prevList):
    data = {"new": {},
            "delete": []}
    
    url = 'https://www.yeogi.com/domestic-accommodations?keyword=%EC%84%9C%EC%9A%B8+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC&autoKeyword=%EC%84%9C%EC%9A%B8+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC&checkIn=2025-02-22&checkOut=2025-02-23&personal=2&freeForm=false'
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    sleep(3)

    
    return data

def update(prevList, site):
    fMap= {"howbouthere": howbouthere,
           "threethree": threethree}
    updater = fMap[site]

    data = updater(prevList)
    return data