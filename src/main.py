from SeleniumFrame import Crawler
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn import linear_model
import datetime

class Main():
    def __init__(self, frame, sYear, sMonth, sDay, eYear, eMonth, eDay, market, product, dataLength):
        self.frame = frame
        self.sYear = sYear
        self.sMonth = sMonth
        self.sDay = sDay
        self.eYear = eYear
        self.eMonth = eMonth
        self.eDay = eDay
        self.market = market
        self.product = product
        self.dataLength = dataLength
        
        # 讀檔
        fileName = ''
        if product == '香蕉':
            fileName = 'bananaDF.csv'
        elif product == '檸檬':
            fileName = 'lemonDF.csv'
        elif product == '馬鈴薯':
            fileName = 'potatoDF.csv'
        elif product == '花椰菜':
            fileName = 'cauliflowerDF.csv'
        elif product == '小番茄':
            fileName = 'tomatoDF.csv'
        elif product == '椰子':
            fileName = 'coconutDF.csv'
            
        if dataLength == '1年':
            fileName = '1_' + fileName    
        elif dataLength == '5年':
            fileName = '5_' + fileName
        elif dataLength == '10年':
            fileName = '10_' + fileName
        elif dataLength == '20年':
            fileName = '20_' + fileName
        readCSV = pd.read_csv(fileName)
        self.func(fileName, readCSV)
        
    def func(self, fileName, readCSV):
        # 爬資料
        crawler = Crawler(self.sYear, self.sMonth, self.sDay, self.eYear, self.eMonth, self.eDay, self.market, self.product)
        
        # 資料預處理
        saleVolumeDf = crawler.getDF()
        if saleVolumeDf.empty:
            saleVolumeDf = readCSV
        else:
            saleVolumeDf.drop(columns=['跟前一交易日比較%', '跟前一交易日比較%'], inplace=True)
            if str(saleVolumeDf.loc[len(saleVolumeDf)-1, '日期']) != str(readCSV.loc[len(readCSV)-1, '日期']):
                readCSV = readCSV.append(saleVolumeDf.loc[len(saleVolumeDf)-1], ignore_index=True)
                saleVolumeDf = readCSV
                saleVolumeDf.to_csv(fileName, index=False, encoding='utf_8_sig')
                print("CSV is Update.")
            else:
                saleVolumeDf = readCSV
                print("CSV is already up to date!")
        
        # dataframe增加[明日均價][昨日均價][昨日銷售量][年份][月份]
        print('0%...', end='')
        self.frame.progress.configure(text='0%')
        for i in range(len(saleVolumeDf)-1):
            saleVolumeDf.loc[i,'明日平均價(元/公斤)'] = saleVolumeDf.loc[i+1, '平均價(元/公斤)']
        print('20%...', end='')
        self.frame.progress.configure(text='20%')
        for i in range(1, len(saleVolumeDf)):
            saleVolumeDf.loc[i,'昨日平均價(元/公斤)'] = saleVolumeDf.loc[i-1, '平均價(元/公斤)']
        print('40%...', end='')
        self.frame.progress.configure(text='40%')
        for i in range(1, len(saleVolumeDf)):
            saleVolumeDf.loc[i,'昨日交易量(公斤)'] = saleVolumeDf.loc[i-1, '交易量(公斤)']
        print('60%...', end='')
        self.frame.progress.configure(text='60%')
        for i in range(0, len(saleVolumeDf)):
            saleVolumeDf.loc[i,'年份'] = str(saleVolumeDf.loc[i, '日期']).split('/')[0]
        print('80%...', end='')
        self.frame.progress.configure(text='80%')
        for i in range(0, len(saleVolumeDf)):
            saleVolumeDf.loc[i,'月份'] = str(saleVolumeDf.loc[i, '日期']).split('/')[1]
        print('100%')
        self.frame.progress.configure(text='')
        
        # 讀雨量、溫度資料
        rain = pd.read_excel('rain.xls')
        temp = pd.read_excel('temp.xls')
        
        # 合併資料
        saleVolumeDf['年份'] = saleVolumeDf['年份'].astype('int64')
        saleVolumeDf['月份'] = saleVolumeDf['月份'].astype('int64')
        saleVolumeDf = saleVolumeDf.merge(rain, on=['年份', '月份'], how='left')
        saleVolumeDf = saleVolumeDf.merge(temp, on=['年份', '月份'], how='left')
        
        # 合併資料存檔
        # saleVolumeDf.to_csv('Merge.csv', index=False, encoding='utf_8_sig')
        
        # 取特徵
        saleVolumeDf.drop([0], inplace=True)
        saleVolumeDf.reset_index(drop=True, inplace=True)
        saleVolumeDf.set_index("日期" , inplace=True)
        X = saleVolumeDf[['平均價(元/公斤)', '交易量(公斤)', '昨日平均價(元/公斤)', '昨日交易量(公斤)', '中南部雨量累積', '中南部平均溫度']]
        y = saleVolumeDf[['明日平均價(元/公斤)']]
        
        # 訓練、測試資料
        X_train = X[0:-1].copy()
        y_train = y[0:-1].copy()
        X_test = X[-1:].copy()
        y_test = y[-1:].copy()
        
        # 標準化
        sc = StandardScaler()
        sc.fit(X_train)
        X_train_std = sc.transform(X_train)
        X_test_std = sc.transform(X_test)
        
        # linear regression 物件
        regr = linear_model.LinearRegression()
        
        # 訓練模型
        regr.fit(X_train_std, y_train)
        
        # 決定係數
        self.score = regr.score(X_train_std, y_train)
        print('決定係數 = ', self.score)
        
        # 最後結果
        resultDF = pd.DataFrame(regr.predict(X_train_std))
        
        # 預測明天的平均價 當 今天的平均價
        tomorrow = regr.predict(X_test_std)[0][0]
        resultDF.loc[len(resultDF)] = [tomorrow]
        print('今天的平均價 = ', tomorrow)
        
        # 預測後天的平均價 當 明天的平均價
        X_test.loc[X_test.index[0], '昨日平均價(元/公斤)'] = X_test.loc[X_test.index[0], '平均價(元/公斤)']
        X_test.loc[X_test.index[0], '昨日交易量(公斤)'] = X_test.loc[X_test.index[0], '交易量(公斤)']
        X_test.loc[X_test.index[0], '平均價(元/公斤)'] = tomorrow
        X_test_std = sc.transform(X_test)
        self.afterTomorrow = regr.predict(X_test_std)[0][0]
        resultDF.loc[len(resultDF)] = [self.afterTomorrow]
        print('明天的平均價 = ', self.afterTomorrow)
        
        # resultDF 的 index 更換成日期
        date_list = list(X.index)
        today = datetime.datetime.now()
        tomo = today + datetime.timedelta(days=1)
        date_list.append(str(tomo.year - 1911) + '/' + str(tomo.month).zfill(2) + '/' + str(tomo.day).zfill(2))
        resultDF.set_index(keys=pd.np.array(date_list), inplace=True, drop=True)
        
        # 畫圖
        resultDF.drop(resultDF.index[0], inplace=True)
        font = {'family': 'DFKai-SB', 'size': 14}
        self.fig1 = plt.figure()
        plt.gcf().set_size_inches(10, 3)
        plt.plot(saleVolumeDf.index, saleVolumeDf['平均價(元/公斤)'], label='real')
        plt.plot(resultDF.index, resultDF, label='predict')
        plt.xticks([])
        plt.ylabel("平均價(元/公斤)", font)
        plt.grid()
        plt.legend()
        
        self.fig2 = plt.figure()
        plt.gcf().set_size_inches(6, 4)
        plt.plot(saleVolumeDf.index[-7:], saleVolumeDf['平均價(元/公斤)'][-7:], label='real', lw=5)
        plt.plot(resultDF.index[-8:], resultDF[-8:], label='predict', lw=5)
        plt.xlabel("日期", font)
        plt.ylabel("平均價(元/公斤)", font)
        plt.xticks(fontsize=6)
        plt.grid()
        plt.legend()

    def getPlot1(self):
        return self.fig1
    
    def getPlot2(self):
        return self.fig2
    
    def getTomorrowPrice(self):
        return format(self.afterTomorrow, '.4f')
    
    def getR2(self):
        return format(self.score, '.6f')