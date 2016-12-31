import Tkinter as tk
import ttk
import datetime



class DateEntry(tk.Frame):
    def __init__(self, master, frame_look={}, **look):
        args = dict(relief=tk.SUNKEN, border=1)
        args.update(frame_look)
        tk.Frame.__init__(self, master, **args)

        args = {'relief': tk.FLAT}
        args.update(look)

        self.entry_1 = tk.Entry(self, width=2, **args)
        self.label_1 = tk.Label(self, text='/', **args)
        self.entry_2 = tk.Entry(self, width=2, **args)
        self.label_2 = tk.Label(self, text='/', **args)
        self.entry_3 = tk.Entry(self, width=4, **args)

        self.entry_1.pack(side=tk.LEFT)
        self.label_1.pack(side=tk.LEFT)
        self.entry_2.pack(side=tk.LEFT)
        self.label_2.pack(side=tk.LEFT)
        self.entry_3.pack(side=tk.LEFT)

        self.entry_1.bind('<KeyRelease>', self._e1_check)
        self.entry_2.bind('<KeyRelease>', self._e2_check)
        self.entry_3.bind('<KeyRelease>', self._e3_check)

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, cont[:-1])

    def _e1_check(self, e):
        cont = self.entry_1.get()
        if len(cont) >= 2:
            self.entry_2.focus()
        if len(cont) > 2 or not cont[-1].isdigit():
            self._backspace(self.entry_1)
            self.entry_1.focus()

    def _e2_check(self, e):
        cont = self.entry_2.get()
        if len(cont) >= 2:
            self.entry_3.focus()
        if len(cont) > 2 or not cont[-1].isdigit():
            self._backspace(self.entry_2)
            self.entry_2.focus()

    def _e3_check(self, e):
        cont = self.entry_2.get()
        if len(cont) > 4 or not cont[-1].isdigit():
            self._backspace(self.entry_3)

    def get(self):
        return self.entry_1.get(), self.entry_2.get(), self.entry_3.get()
        
         
        
class TimeEntry(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
    
        self.hour_var = tk.StringVar(self)
        self.hour_var.set("9")
        self.hour_cb = ttk.Combobox(self, 
                                   textvariable=self.hour_var,
                                   values=("1", "2", "3", "4", "5", "6", 
                                           "7", "8", "9", "10", "11", "12"),
                                   width=2,
                                   state='readonly')
        self.hour_cb.pack(side=tk.LEFT)
        self.min_var = tk.StringVar(self)
        self.min_var.set("00")
        self.min_cb = ttk.Combobox(self, 
                                   textvariable=self.min_var,
                                   values=("00", "15", "30", "45"),
                                   width=3,
                                   state='readonly')
        self.min_cb.pack(side=tk.LEFT)
        self.meridiem_var = tk.StringVar(self)
        self.meridiem_var.set("AM")
        self.meridiem_cb = ttk.Combobox(self, 
                                        textvariable=self.meridiem_var,
                                        values=("AM", "PM"),
                                        width=3,
                                        state='readonly')
        self.meridiem_cb.pack(side=tk.LEFT)
        
        
    def get(self):
        return self.hour_var.get(), self.min_var.get(), self.meridiem_var.get()
        
        
    def get_time(self):
        """Return a datetime.time() object representing selected values """
        hour = int(self.hour_var.get())
        if self.meridiem_var.get() == "PM":
            hour += 12
        min = int(self.min_var.get())
        
        return datetime.time(hour, min)
        
        
        
def yearify(curr_year, n):
        """Return a string list of n+5 years starting 4 years before curr_year.
        
        Args:
            curr_year: string representation of present year
            n: number of years after present year desired to be in list
        """
        
        year_list = []
        start_year = int(curr_year) - 4
        
        for i in range(start_year, start_year + n + 5):
            year_list.append(str(i))
           
        return year_list