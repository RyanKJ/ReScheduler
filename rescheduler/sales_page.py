"""
Module for the employee and department page.
"""

import Tkinter as tk
import ttk
import calendar
import datetime
from datetime_widgets import yearify
from orm_models import MonthSales
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

MEDIUM_FONT = ('Tahoma', 12, tk.NORMAL)

class SalesPage:
    """
    Sales page acts as a simple add and remove listbox. It adds revenue data
    to the database that includes information about the month and the year of
    the revenue data. This revenue data is then used to calculate the cost
    employment for a given month relative to the average revenue of that month.
    """

    MONTH_TO_NUM = {"January":1, "February":2, "March":3, "April":4, 
                    "May":5, "June":6, "July":7, "August":8, "September":9, 
                    "October":10, "November":11, "December":12}

    def __init__(self, master, session, calendar_page):
        """Initialize SalesPage and the different composite widgets."""
        self.master = master
        self.session = session
        self.cal = calendar_page
        
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        
        self.page_frame = tk.Frame(self.master, borderwidth=1, 
                                   relief=tk.RIDGE)
        self.page_frame.pack()
        
        self.title = tk.Label(self.page_frame, 
                              text="Monthly Revenue Data",
                              font=MEDIUM_FONT)
        self.title.pack()
        
        self.sales_lb = tk.Listbox(self.page_frame, 
                                   height=22, width=35, 
                                   font=MEDIUM_FONT)
        self.sales_lb.pack()
        
        self.sales_button_frame = tk.Frame(self.page_frame)
        self.sales_button_frame.pack()
        self.sales_add_frame = tk.Frame(self.page_frame)
        self.sales_add_frame.pack()
        
        self.month_label = tk.Label(self.sales_add_frame, 
                                    text = "Month: ", 
                                    font=MEDIUM_FONT)
        self.month_label.pack(side=tk.LEFT)
        self.month_var = tk.StringVar(self.sales_add_frame)
        self.month_var.set("January")     
        months = ("January", "February", "March", "April",
                  "May", "June", "July", "August", "September", 
                  "October", "November", "December")
        self.m = ttk.Combobox(self.sales_add_frame, 
                              textvariable=self.month_var,
                              values=months,
                              width=12,
                              state='readonly') 
        self.m.pack(side=tk.LEFT)
        
                               
        self.year_label = tk.Label(self.sales_add_frame, 
                                   text = "Year: ", 
                                   font=MEDIUM_FONT)
        self.year_label.pack(side=tk.LEFT)
        self.year_var = tk.StringVar(self.sales_add_frame)
        self.year_var.set(year)
        
        year_list = yearify(year, 8)
        
        self.y = ttk.Combobox(self.sales_add_frame, 
                              textvariable=self.year_var,
                              values=year_list,
                              width=5,
                              state='readonly')
        self.y.pack(side=tk.LEFT)
        
        self.amount_var = tk.IntVar(self.sales_add_frame)
        self.amt_label = tk.Label(self.sales_add_frame, 
                                  text="Sales Amount: ", 
                                  font=MEDIUM_FONT)      
        self.amt_label.pack(side=tk.LEFT)
       
        self.amt_entry = ttk.Entry(self.sales_add_frame, 
                                  font=MEDIUM_FONT, 
                                  textvariable=self.amount_var)
        self.amt_entry.pack(side=tk.LEFT)
        
        
        
        self.add_sales_info = ttk.Button(self.sales_button_frame, 
                                         text='Add Sales Info',  
                                         command=self.add_sales_info)
        self.add_sales_info.pack(side=tk.LEFT)
        self.remove_sales_info = ttk.Button(self.sales_button_frame, 
                                            text='Remove Sales Info',  
                                            command=self.remove_sales_info)
        self.remove_sales_info.pack(side=tk.LEFT)
        
        # Parallel list to the sales info in the Sales table in DB
        self.sales_info = []
        self.load_sales_info()
        
        
    def load_sales_info(self):
        """Load db obj from Sales table and put into listbox/parallel list."""
        self.sales_lb.delete(0, tk.END)
        self.sales_info = self.session.query(MonthSales).all()
        self.sales_info.sort(key=lambda sales: sales.month_and_year)
        for s in self.sales_info:
            text = s.get_string()
            self.sales_lb.insert(tk.END, text)
        
    def add_sales_info(self):
        """Commit data fields in widgets to listbox and DB Sales table."""
        year = int(self.year_var.get())
        month = self.MONTH_TO_NUM[self.month_var.get()]
        amount = self.amount_var.get()
        sales_date = datetime.date(year, month, 1)
        sales_info = MonthSales(sales_date, amount)
        self.session.add(sales_info)
        self.session.commit()
        self.load_sales_info()
        
        self.cal.update_costs()
        
    def remove_sales_info(self):
        """Remove selected listbox element and object from DB."""
        if self.sales_lb.curselection() == ():
            return
        index =  self.sales_lb.curselection()[0]
        self.sales_lb.delete(index)
        sales_info_obj = self.sales_info[index]
        self.session.delete(sales_info_obj)
        self.session.commit()
        del self.sales_info[index]
        
        self.cal.update_costs()