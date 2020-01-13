import tkinter as tk
from tkinter.ttk import Combobox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from main import Main
from threading import Thread
from time import sleep

class HomeFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        
        # 年份圖片
        self.canvas1 = tk.Canvas(self, width=1000, height=300, highlightthickness=0)
        self.canvas1.grid(row=0, column=0, rowspan=6, columnspan=10)
     
        # 相關變數設定、結果顯示
        self.marketLabel = tk.Label(self, text='市場：', font=('微軟正黑體', 15))
        self.marketLabel.grid(row=6, column=0, columnspan=2, sticky='e')
        
        self.taipeiLabel = tk.Label(self, text='台北一', font=('微軟正黑體', 15))
        self.taipeiLabel.grid(row=6, column=2, sticky='w')
        
        self.productLabel = tk.Label(self, text='品項：', font=('微軟正黑體', 15))
        self.productLabel.grid(row=7, column=0, columnspan=2, sticky='e')
        
        items = ["香蕉", "檸檬","馬鈴薯","花椰菜","小番茄","椰子"]
        self.itemCombox = Combobox(self, state="readonly", values=items, font=('微軟正黑體', 15))
        self.itemCombox.grid(row=7, column=2, sticky='w')
        
        self.lengthLabel = tk.Label(self, text='訓練年份數：', font=('微軟正黑體', 15))
        self.lengthLabel.grid(row=8, column=0, columnspan=2, sticky='e')
        
        timeItems = ["1年", "5年","10年","20年"]
        self.timeLengthCombox = Combobox(self, state="readonly", values=timeItems, font=('微軟正黑體', 15))
        self.timeLengthCombox.grid(row=8, column=2, sticky='w')
        
        self.resultLabel = tk.Label(self, text="預測下次開市價格：", font=('微軟正黑體', 15))
        self.resultLabel.grid(row=9, column=0, columnspan=2, sticky='w')
        
        self.result = tk.Label(self, text="-----元/公斤", font=('微軟正黑體', 15))
        self.result.grid(row=9, column=2, sticky='w')
        
        self.r2Label = tk.Label(self, text="決定係數：", font=('微軟正黑體', 15))
        self.r2Label.grid(row=10, column=0, columnspan=2, sticky='e')
        
        self.r2result = tk.Label(self, text="-----", font=('微軟正黑體', 15))
        self.r2result.grid(row=10, column=2, sticky='w')
        
        self.checkBtn = tk.Button(self, text="搜尋", font=('微軟正黑體', 15), command=self.btnEvent)
        self.checkBtn.grid(row=11, column=2)
        
        self.progress = tk.Label(self, text="", font=('微軟正黑體', 15))
        self.progress.grid(row=13, column=0, sticky='ws')
        
        # 近一週圖片
        self.canvas2 = tk.Canvas(self, width=600, height=400, highlightthickness=0)
        self.canvas2.grid(row=6, column=5, rowspan=8, columnspan=6)
        
        self.pack(fill='both', expand=1)
    
    def btnEvent(self):
        Thread(target=self.search).start()
#         Thread(target=self.countdown).start()
        
#     def countdown(self):
#         for i in range(0,101,10):
#             self.progress.configure(text=str(i))
#             sleep(2)
    
    def search(self):
        if(self.timeLengthCombox.get()=='' or self.itemCombox.get()==''):
            return
        main = Main(self, 2020, 1, 1, 2020, 1, 3, '台北一', self.itemCombox.get(), self.timeLengthCombox.get())
        root.after(0, self.drawFigure, main)
        
    def drawFigure(self, main):
        self.fig1 = main.getPlot1()
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().grid(row=0, column=0, rowspan=6, columnspan=10)
         
        self.fig2 = main.getPlot2()
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().grid(row=6, column=5, rowspan=8, columnspan=6)
         
        # 明日價格
        self.result.configure(text=str(main.getTomorrowPrice()) + '元/公斤')
        
        # 決定係數
        self.r2result.configure(text=main.getR2()) 
        
if __name__ == '__main__':
    root = tk.Tk()
    root.title('蔬果市場價格預測')
    root.geometry("1000x700")
    root.resizable(False, False)
    HomeFrame(root)
    root.mainloop()
