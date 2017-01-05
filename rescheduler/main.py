""" 
Rescheduler Alpha

Author: Ryan Johnson
Python 2.7.11
openpyxl 2.3.2
SQLAlchemy 1.0.12
"""

import Tkinter as tk
import calendar_page
from orm_models import start_db


session = start_db('32')

# Instantiate the Tkinter program
sizex = 1420
sizey = 800
posx  = 100
posy  = 100

root = tk.Tk()
root.title("Retail Scheduler")
root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))
gui = calendar_page.ReScheduler(root, session)

root.mainloop()