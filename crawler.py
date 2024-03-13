from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
import datetime
import pandas as pd
import time 
import os
# import re
# import numpy as np

def text_to_df(text):
    # def change_type(li):
    #     re = []
    #     for ele in li:
    #         re.append(int(ele.replace(',', '')))
    #         if ele =='--':
    #             re.append(np.nan)
    #     return re
    air_text = text[text.find('航空公司') + len('航空公司'):text.find('直飛')].strip()
    air = [com for com in air_text.split('\n')]
    air_text1 = text[text.find('直飛') + len('直飛'):text.find('轉機 1次')].strip()
    air_price1 = [price for price in air_text1.split(' ')]
    #air_price1 = change_type(air_price1)
    air_text2 = text[text.find('轉機 1次') + len('轉機 1次'):text.find('轉機 2次以上')].strip()
    air_price2 = [price for price in air_text2.split(' ')]
    #air_price2 = change_type(air_price2)
    air_text3 = text[text.find('轉機 2次以上') + len('轉機 2次以上'):].strip()
    air_price3 = [price for price in air_text3.split(' ')]
    #air_price3 = change_type(air_price3)
    df = {'航空公司' : air, '直飛' : air_price1, '轉機 1次' : air_price2, '轉機 2次以上' : air_price3}
    return df
def crawler(day_inter, dept = '台北 TAIPEI(松山TSA/桃園TPE)-台灣', arriv = '大阪 OSAKA(OSA)-日本'):
    

    driver.get(url)

    #driver.implicitly_wait(4)  # 這裡的時間可以根據網頁加載速度進行調整

    element_single = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-wair"]/div[1]/label[2]/input')))
    element_single.click()

    element_from = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="wair-sp-dept"]')))
    element_from.send_keys(dept)
    element_from2 = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-wair-sp"]/div[1]/div[1]/div/span/ul/li/a')))
    element_from2.click()

    element_to = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="wair-sp-arrv"]')))
    element_to.send_keys(arriv)
    element_to2 = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-wair-sp"]/div[1]/div[2]/div/span/ul/li/a')))
    element_to2.click()

    goal_date = (datetime.datetime.today() + datetime.timedelta(days=day_inter)).strftime("%Y%m%d")
    element_date = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="wair-sp-sd"]')))
    element_date.send_keys(goal_date)

    element_search = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="wair-sp-search"]')))
    driver.execute_script("arguments[0].scrollIntoView();", element_search)
    driver.execute_script("arguments[0].click();", element_search)
    time.sleep(3)
    new_window = driver.window_handles[-1]
    driver.switch_to.window(new_window)


    data_list = []
    final_df = pd.DataFrame()
    try :
        """這邊是指每查詢一次所得到的那個可以點下一頁的table"""
        if WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[3]/div[1]/div[2]/div[1]/h4'))
        ) : 
            element_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]')))
            #print(element_table.text)
            data_list.append(text_to_df(element_table.text))
            if WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]/div/table/tfoot/tr/td/a'))) :  
                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]/div/table/tfoot/tr/td/a'))).click()
                time.sleep(0.5)
                element_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]')))
                #print(element_table.text)
                data_list.append(text_to_df(element_table.text))
                try : 
                    while WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]/div/table/tfoot/tr/td/a[2]'))):
                        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]/div/table/tfoot/tr/td/a[2]'))).click()
                        time.sleep(0.5)
                        element_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="home"]')))
                        #print(element_table.text)
                        data_list.append(text_to_df(element_table.text))
                        if TimeoutException:
                            break
                except: 
                    pass
    except :
        pass
    for data in data_list:
        df = pd.DataFrame(data)
        final_df = pd.concat([final_df, df])
    final_df.reset_index(drop=True, inplace=True)
    final_df['資料抓取日期'] = [today] * len(final_df)
    final_df['出發日(日期)'] = [goal_date] * len(final_df)
    final_df['出發日(禮拜)'] = [(datetime.datetime.today() + datetime.timedelta(days=day_inter)).weekday()+1] * len(final_df)
    final_df['出發地點'] = [dept.split('-')[-1] + dept.split(' ')[0]] * len(final_df)
    final_df['抵達地點'] = [arriv.split('-')[-1] + arriv.split(' ')[0]] * len(final_df)
    #print(final_df)
    return final_df
today = datetime.datetime.today().strftime("%Y%m%d")
start_time = time.time()
path = os.path.join('data', f'price_ticket_{today}.xlsx')
df_list = []
final_df = pd.DataFrame()

country_groups = [['台北 TAIPEI(松山TSA/桃園TPE)-台灣', '洛杉磯 LOS ANGELES(LAX)-美國'], 
             ['台北 TAIPEI(松山TSA/桃園TPE)-台灣', '東京 TOKYO(TYO)-日本'], 
             ['台北 TAIPEI(松山TSA/桃園TPE)-台灣', '曼谷 BANGKOK(BKK)-泰國'],
             #['新加坡 SINGAPORE(SIN)-新加坡', '吉隆坡 KUALA LUMPUR(KUL)-馬來西亞'], 
             ['紐約 NEW YORK(NYC)-美國', '倫敦 LONDON(LON)-英國']]

chrome_options = Options()
chrome_options.page_load_strategy = 'eager'
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--headless")  
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
#service = Service('chromedriver.exe')  
driver = webdriver.Chrome(options=chrome_options)

url = 'https://intl.ezfly.com/'

for day in range(1, 181):
    for countries in country_groups : 
        try :
            df_list.append(crawler(day, dept = countries[0], arriv = countries[1]))
        except Exception or WebDriverException as e: # 發生錯誤，當下馬上存檔，並繼續下一個國家的組合
            for data in df_list:
                df = pd.DataFrame(data)
                final_df = pd.concat([final_df, df])
            df_list = []
            final_df.reset_index(drop=True, inplace=True)
            final_df.to_excel(path)
            print(f'發生錯誤 :{e}, at {(datetime.datetime.strptime(today,  "%Y%m%d") + datetime.timedelta(days=day)).strftime("%Y%m%d")}, for countries group {countries}')
            continue

for data in df_list:
    df = pd.DataFrame(data)
    final_df = pd.concat([final_df, df])
final_df.reset_index(drop=True, inplace=True)
final_df.to_excel(path)

end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds for {180 * len(country_groups)}")