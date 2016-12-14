import Tkinter as tk
import calendar_page
from orm_models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



engine = create_engine('sqlite:///test30.db', echo=False)
# create a Session
Session = sessionmaker(bind=engine)
session = Session()


"""
dep_list = ["Front", "Office", "Designers", "Facilities", "Drivers"]

for d in dep_list:
    dep = Department(d)
    session.add(dep)
session.commit()
"""

# EDIT: Insert some check to make sure at least 1 department exists?

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