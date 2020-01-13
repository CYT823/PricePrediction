from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import pandas as pd 


class Crawler():
    def __init__(self, sYear, sMonth, sDay, eYear, eMonth, eDay, market, product):
        # 變數
        self.web = 'https://amis.afa.gov.tw/fruit/FruitProdDayTransInfo.aspx'
        self.sYear = sYear
        self.sMonth = str(sMonth)
        self.sDay = str(sDay)
        self.eYear = eYear
        self.eMonth = str(eMonth)
        self.eDay = str(eDay)
        if market == '台北一':
            self.market = '109'
        if product == '香蕉':
            self.product = 'A1'
        elif product == '檸檬':
            self.product = 'F1'
        elif product == '馬鈴薯':
            self.product = 'SC1'
            self.web = 'https://amis.afa.gov.tw/veg/VegProdDayTransInfo.aspx'
        elif product == '花椰菜':
            self.product = 'FB1'
            self.web = 'https://amis.afa.gov.tw/veg/VegProdDayTransInfo.aspx'
        elif product == '小番茄':
            self.product = '71'
        elif product == '椰子':
            self.product = '11'
        
        # 呼叫底下方法
        self.__func()
    def __func(self):
        #使用chrome的webdriver
        browser = webdriver.Chrome()
        browser.get(self.web)
        
        # 選擇範圍
        browser.find_element_by_xpath('//*[@id="ctl00_contentPlaceHolder_ucDateScope_rblDateScope_1"]').click()
        
        # 輸入開始日期
        browser.find_element_by_xpath('//*[@id="ctl00_contentPlaceHolder_txtSTransDate"]').click()
        year = Select(browser.find_element_by_xpath('//*[@id="sYear_amis"]'))
        year.select_by_value(str(self.sYear - 1911))
        month = Select(browser.find_element_by_xpath('//*[@id="sMonth_amis"]'))
        month.select_by_value(self.sMonth)
        fontTag = browser.find_elements_by_tag_name("font")
        for item in fontTag:
            if item.text == self.sDay:
                item.click()
        
        # 輸入結束日期
        browser.find_element_by_xpath('//*[@id="ctl00_contentPlaceHolder_txtETransDate"]').click()
        year = Select(browser.find_element_by_xpath('//*[@id="sYear_amis"]'))
        year.select_by_value(str(self.eYear - 1911))
        month = Select(browser.find_element_by_xpath('//*[@id="sMonth_amis"]'))
        month.select_by_value(self.eMonth)
        fontTag = browser.find_elements_by_tag_name("font")
        for item in fontTag:
            if item.text == str(self.eDay):
                item.click()
        
        # 挑選市場 - 台北一
        browser.find_element_by_xpath('//*[@id="ctl00_contentPlaceHolder_txtMarket"]').click()
        browser.switch_to.frame(0)
        menu = Select(browser.find_element_by_xpath('//*[@id="lstMarket"]'))
        menu.select_by_value(self.market)
        browser.find_element_by_xpath('//*[@id="btnConfirm"]').click()
         
        # 挑選產品 - 牛奶鳳梨B7
        browser.find_element_by_xpath('//*[@id="ctl00_contentPlaceHolder_txtProduct"]').click()
        browser.switch_to.frame(0)
        menu = Select(browser.find_element_by_xpath('//*[@id="lstProduct"]'))
        menu.select_by_value(self.product)
        browser.find_element_by_xpath('//*[@id="btnConfirm"]').click()
         
        # 查詢
        browser.find_element_by_xpath('//*[@id="ctl00_contentPlaceHolder_btnQuery"]').click()
         
        # 取得table資料
        time.sleep((self.eYear - self.sYear + 1)*1.5)
        try:
            self.df = pd.DataFrame()
            table = browser.find_element_by_xpath('//*[@id="ctl00_contentPlaceHolder_panel"]/table[3]')
            data = pd.read_html(table.get_attribute("outerHTML"))
        except:
            pass
        else:
            # 轉為dataframe
            self.df = data[0]
            self.df.columns = ['日期', '產品', '上價', '中價', '下價', '平均價(元/公斤)', '跟前一交易日比較%', '交易量(公斤)', '跟前一交易日比較%']
            self.df.drop([0, 1], inplace=True)
            self.df.fillna('-', inplace=True)
            self.df.reset_index(drop=True, inplace=True)
        finally:
            browser.quit()
            
    def getDF(self):
        return self.df
