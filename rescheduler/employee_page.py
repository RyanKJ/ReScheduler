import Tkinter as tk
import ttk
import datetime
import bisect
import collections
from datetime_widgets import DateEntry, TimeEntry, yearify
from orm_models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



class EmployeePage(tk.Frame):
    
    
    def __init__(self, parent, session, calendar_page):
        tk.Frame.__init__(self, parent)
        
        self.session = session
        self.cal = calendar_page
        self.curr_sel_employee = None
        
        # Left Panel Frame Widgets for Employee/Department Lists
        employee_department_nb = ttk.Notebook(self)
        employee_department_nb.pack(side="left", fill="both", expand=True,
                                    padx=10, pady=10)
        
        self.employee_list_frame = tk.Frame(employee_department_nb)
        self.employee_list_frame.pack()
        self.employee_list = EmployeeList(self.employee_list_frame, session, self, calendar_page)
        self.employee_list.pack()
        
        self.dep_list_frame = tk.Frame(employee_department_nb)
        self.dep_list_frame.pack()
        self.dep_list = DepartmentList(self.dep_list_frame, session, calendar_page)
        self.dep_list.pack()

        employee_department_nb.add(self.employee_list_frame, text="Employee List")
        employee_department_nb.add(self.dep_list_frame, text="Department List")
        
        
        # Center Panel Frame Widgets for Employee Info Form
        self.employee_info_frame = ttk.LabelFrame(self,
                                                  text='Employee Information')
        self.employee_info_frame.pack(side="left", fill="both", expand=True,
                                      padx=10, pady=24, anchor='center')
        self.e_info_form = EmployeeInfoForm(self.employee_info_frame, session,
                                            self, calendar_page)     
        self.e_info_form.pack()
                             

        # Right Panel Frame Widgets for Various Unavailability Lists
        self.unavailability_nb = ttk.Notebook(self)
        self.unavailability_nb.pack(side="left", fill="both", expand=True,
                                    padx=10, pady=10)

        self.repeat_unav_frame = tk.Frame(self.unavailability_nb,)
        self.repeat_unav_frame.pack(side="left", fill="both", expand=True,
                                      padx=10, pady=24, anchor='center')                            
        self.e_unav_form = EmployeeRepeatUnavailable(self.repeat_unav_frame, 
                                                session, self, calendar_page) 
        self.e_unav_form.pack()                                        
                                      
                                      
        self.vacation_frame = tk.Frame(self.unavailability_nb)
        self.vacation_frame.pack(side="left", fill="both", expand=True,
                                      padx=10, pady=24, anchor='center')
        self.e_vacation_form = EmployeeVacations(self.vacation_frame, 
                                            session, self, calendar_page)  
        self.e_vacation_form.pack()
        
        self.unavailability_nb.add(self.repeat_unav_frame, 
                                   text="Unavailable Days")
        self.unavailability_nb.add(self.vacation_frame, 
                                   text="Vacation Times")
                                   
                                   
    def load_employee_data(self, employee):
        self.e_info_form.load_employee_form(employee)
        self.e_unav_form.load_unav_times(employee)
        self.e_vacation_form.load_vacations(employee)
        
    def update_e_list(self, employee):
        self.employee_list.update_listbox(employee)
        
    def add_new_e_info(self):
        self.e_info_form.add_new_e_info()
                             
                                  
        
class EmployeeList(tk.Frame):
        
        
    def __init__(self, parent, session, e_page, calendar_page):
        tk.Frame.__init__(self, parent)
        
        self.session = session
        self.e_page = e_page
        self.cal = calendar_page
        
        self.employee_listbox = tk.Listbox(self, 
                                           exportselection=0, 
                                           height=14, width=25, 
                                           font=('Tahoma', 14, tk.NORMAL))
        self.employee_listbox.grid(row=1, column=0, 
                                   rowspan=6, columnspan=3,
                                   pady=8)
        self.employee_listbox.bind('<<ListboxSelect>>', self.load_employee)
        self.employee_listbox.bind('<Double-1>', self.load_employee)
        self.employee_listbox.bind('<Return>', self.load_employee)
        
        # 2 Parallel lists, employee_name_list is synced with employee_db_list. 
        self.employee_db_list = self.session.query(Employees).all()
        self.employee_db_list.sort(key=lambda e: e.first_name)
        for e in self.employee_db_list: # Do we need a for loop for this? Isn't there a way to instantiate listbox with a list?
            self.employee_listbox.insert(tk.END, e.first_name)
            
            
        # Add and remove employee buttons
        self.add_employee_button = ttk.Button(self, 
                                             text='Add Employee', 
                                             command=self.add_new_employee)
        self.add_employee_button.grid(row=9, column=0)
        self.remove_employee_button = ttk.Button(self, 
                                                text='Remove Employee', 
                                                command=self.remove_employee)
        self.remove_employee_button.grid(row=9, column=2)


        
        
    def add_new_employee(self):
        self.employee_listbox.selection_clear(0, tk.END)
        self.employee_listbox.insert(tk.END, "New Employee")
        self.employee_listbox.selection_set(tk.END)
        self.e_page.curr_sel_employee = "New Employee"
        
        self.e_page.add_new_e_info()
       
        
        
    def load_employee(self, event):
        # When listbox employee is clicked, from parallel list find employee, then fetch all relevant data and input into appopriate widgets
        employee = self.get_employee()
        self.e_page.curr_sel_employee = employee
        self.e_page.load_employee_data(employee)
        
    
    def remove_employee(self):
        employee = self.get_employee()
        if self.employee_listbox.curselection() == ():
            return
        index = self.employee_listbox.curselection()[0]
        self.employee_listbox.delete(index)
        # Employee in listbox may be uncommitted new employee not in parallel list
        if index < len(self.employee_db_list):
            self.session.delete(employee)
            self.session.commit()
            del self.employee_db_list[index]

        

    # Returns a the selected employee, returns None is nothing is 
    # clicked yet or employee is a New Employee yet to be added to the database
    def get_employee(self):
        if self.employee_listbox.curselection() == ():
            return None
        index = self.employee_listbox.curselection()[0]
        # Case where DB employee list is smaller signals uncomitted mew employees
        if index < len(self.employee_db_list):
            return self.employee_db_list[index]
        else:
            return "New Employee"
    
    def set_employee(self):
        pass
        
        
    def update_listbox(self, employee):
        # if  self.employee_db_list contains, potentially update name
        # if not, append to end, since new employee
        print "Employee is: " + employee.first_name
        if employee in self.employee_db_list:
            index = self.employee_db_list.index(employee)
            self.employee_listbox.delete(index)
            self.employee_listbox.insert(index, employee.first_name)
            self.employee_listbox.selection_set(index)
        else:
            self.employee_db_list.append(employee)
            list_of_names = self.employee_listbox.get(0, tk.END)
            print 'List of names is: '
            print list_of_names
            for text in list_of_names:
                if text == "New Employee":
                    index = list_of_names.index(text)
                    self.employee_listbox.delete(index)
                    self.employee_listbox.insert(index, employee.first_name)
                    self.employee_listbox.selection_set(index)
                    break
            
         
        
class DepartmentList(tk.Frame):


    def __init__(self, parent, session, calendar_page):
        tk.Frame.__init__(self, parent)
    
        self.session = session
        self.cal = calendar_page
        
        
        
        self.department_listbox = tk.Listbox(self, 
                                             height=6, width=25, 
                                             font=('Tahoma', 14, tk.NORMAL))
        self.department_listbox.grid(row=11, column=0, 
                                     rowspan=6, columnspan=3,
                                     pady=8)
        # 2 Parallel lists, employee_name_list is synced with employee_db_list. 
        for d in self.cal.dep_list: # Do we need a for loop for this? Isn't there a way to instantiate listbox with a list?
            self.department_listbox.insert(tk.END, d)
        
        self.add_department_button = ttk.Button(self, 
                                               text='Add Department', 
                                               command=self.add_department)
        self.add_department_button.grid(row=20, column=0)
        self.remove_department_button = ttk.Button(self, 
                                                  text='Remove Department', 
                                                  command=self.remove_department)
        self.remove_department_button.grid(row=20, column=2)
        
        self.add_dep_label = tk.Label(self, 
                                      text="New Department:", 
                                      font=('Tahoma', 14, tk.NORMAL))
        self.add_dep_label.grid(row=21, column=0, columnspan=2)
        
        self.dep_name = tk.StringVar(self)
        #self.dep_name.set("New Department Name")
        self.dep_entry = ttk.Entry(self, 
                                  font=('Tahoma', 14, tk.NORMAL), 
                                  textvariable=self.dep_name)
        self.dep_entry.grid(row=21, column=2)
        
        
    def add_department(self):
        dep = Department(self.dep_name.get())
        self.session.add(dep)
        self.session.commit()
        
        self.department_listbox.insert(tk.END, self.dep_name.get())
        self.cal.dep_list.append(self.dep_name.get())
        
        
    def remove_department(self):
        if self.department_listbox.curselection() == ():
            return
        index = self.department_listbox.curselection()[0]
        dep_str = self.department_listbox.get(index)
        # EDIT: This should be a Try/Except structure, throw error
        db_department = (self.session.query(Department)
                                     .filter(Department.name == dep_str)
                                     .first())
        self.session.delete(db_department)
        self.session.commit()
        # 1 - Find corresponding db department object
        # 2 - Delete it
        # 3 - Delete corresponding element in self.cal.dep_list
        self.department_listbox.delete(index)
        del self.cal.dep_list[index]
        # 4 - Delete listbox element
        self.cal.d['menu'].delete(index)
        
                   
        
class EmployeeInfoForm(tk.Frame):


    def __init__(self, parent, session, e_page, calendar_page):
        tk.Frame.__init__(self, parent)
        
        self.session = session
        self.e_page = e_page
        self.cal = calendar_page
          
        # First name widgets
        self.f_name_var = tk.StringVar(self)
        self.e_first_name_label = tk.Label(self, text="First Name: ", 
                                           font=('Tahoma', 12, tk.NORMAL))
        self.e_first_name_label.grid(row=2, column=0, sticky=tk.E)
        self.e_first_name_entry = ttk.Entry(self, 
                                            font=('Tahoma', 12, tk.NORMAL), 
                                            textvariable=self.f_name_var)
        self.e_first_name_entry.grid(row=2, column=1, sticky=tk.W)
        # Last name widgets
        self.l_name_var = tk.StringVar(self)
        self.e_last_name_label = tk.Label(self, text="Last Name: ", 
                                          font=('Tahoma', 12, tk.NORMAL))
        self.e_last_name_label.grid(row=3, column=0, sticky=tk.E)
        self.e_last_name_entry = ttk.Entry(self, 
                                           font=('Tahoma', 12, tk.NORMAL), 
                                           textvariable=self.l_name_var)
        self.e_last_name_entry.grid(row=3, column=1, sticky=tk.W)

        # Employee ID Number Widgets
        self.e_id = tk.IntVar(self)
        self.e_id_label = tk.Label(self, text="Employee ID Number: ", 
                                   font=('Tahoma', 12, tk.NORMAL))
        self.e_id_label.grid(row=4, column=0, sticky=tk.E)
        self.e_id_entry = ttk.Entry(self, font=('Tahoma', 12, tk.NORMAL), 
                                    textvariable=self.e_id)
        self.e_id_entry.grid(row=4, column=1, sticky=tk.W)
        # Wage Spinbox
        self.e_wage = tk.DoubleVar(self)
        self.e_wage_label = tk.Label(self, 
                                     text="Wage: ", 
                                     font=('Tahoma', 12, tk.NORMAL))
        self.e_wage_label.grid(row=5, column=0, sticky=tk.E)
        self.e_wage_sb = ttk.Entry(self, font=('Tahoma', 12, tk.NORMAL), 
                                   textvariable=self.e_wage)
        self.e_wage_sb.grid(row=5, column=1, sticky=tk.W)
        # Desired Hours Spinbox
        self.d_hours = tk.StringVar(self)
        self.e_dhours_label = tk.Label(self, text="Desired Hours: ", 
                                       font=('Tahoma', 12, tk.NORMAL))
        self.e_dhours_label.grid(row=6, column=0, sticky=tk.E)
        self.e_dhours_sb = tk.Spinbox(self, from_=0, to=70, 
                                      font=('Tahoma', 12, tk.NORMAL), 
                                      textvariable=self.d_hours)
        self.e_dhours_sb.grid(row=6, column=1, sticky=tk.W)
        # Deparment Spinboxes
        self.departments = ("None", "Front", "Office", 
                            "Designers", "Facilities", "Drivers")
        self.dep1 = tk.StringVar(self)
        self.dep2 = tk.StringVar(self)
        self.dep3 = tk.StringVar(self)
        # Primary Department
        self.p_dep_label = tk.Label(self, 
                                    text="Primary Department: ", 
                                    font=('Tahoma', 12, tk.NORMAL))
        self.p_dep_label.grid(row=7, column=0, sticky=tk.E)
        self.p_dep_sb = tk.Spinbox(self, 
                                   values=self.departments, 
                                   font=('Tahoma', 12, tk.NORMAL), 
                                   textvariable=self.dep1, 
                                   wrap=True)
        self.p_dep_sb.grid(row=7, column=1, sticky=tk.W)
        # Alternate Department #1
        self.alt1_dep_label = tk.Label(self, 
                                       text="Alternate Department #1: ", 
                                       font=('Tahoma', 12, tk.NORMAL))
        self.alt1_dep_label.grid(row=8, column=0, sticky=tk.E)
        self.alt1_dep_sb = tk.Spinbox(self, 
                                      values=self.departments, 
                                      font=('Tahoma', 12, tk.NORMAL), 
                                      textvariable=self.dep2, 
                                      wrap=True)
        self.alt1_dep_sb.grid(row=8, column=1, sticky=tk.W)
        # Alternate Department #2
        self.alt2_dep_label = tk.Label(self, 
                                       text="Alternate Department #2: ", 
                                       font=('Tahoma', 12, tk.NORMAL))
        self.alt2_dep_label.grid(row=9, column=0, sticky=tk.E)
        self.alt2_dep_sb = tk.Spinbox(self, 
                                      values=self.departments, 
                                      font=('Tahoma', 12, tk.NORMAL), 
                                      textvariable=self.dep3, wrap=True)
        self.alt2_dep_sb.grid(row=9, column=1, sticky=tk.W)
        # Overtime widgets
        self.ovrt_var = tk.StringVar(self)
        self.ovrt_label = tk.Label(self, text="Over Time: ", 
                                   font=('Tahoma', 12, tk.NORMAL))
        self.ovrt_label.grid(row=10, column=0, sticky=tk.E)
        self.ovrt_entry = ttk.Entry(self, font=('Tahoma', 12, tk.NORMAL), 
                                    textvariable=self.ovrt_var)
        self.ovrt_entry.grid(row=10, column=1, sticky=tk.W)
        # Workman's Comp widgets
        self.work_comp_var = tk.StringVar(self)
        self.work_comp_label = tk.Label(self, text="Workman's Comp Per $100: ", 
                                        font=('Tahoma', 12, tk.NORMAL))
        self.work_comp_label.grid(row=11, column=0, sticky=tk.E)
        self.work_comp_entry = ttk.Entry(self, font=('Tahoma', 12, tk.NORMAL), 
                                         textvariable=self.work_comp_var)
        self.work_comp_entry.grid(row=11, column=1, sticky=tk.W)
        # Social Security
        self.soc_sec_var = tk.StringVar(self)
        self.soc_sec_label = tk.Label(self, text="Social Security % of Wage: ", 
                                      font=('Tahoma', 12, tk.NORMAL))
        self.soc_sec_label.grid(row=12, column=0, sticky=tk.E)
        self.soc_sec_entry = ttk.Entry(self, font=('Tahoma', 12, tk.NORMAL), 
                                       textvariable=self.soc_sec_var)
        self.soc_sec_entry.grid(row=12, column=1, sticky=tk.W)
        # Medical Cost Per Month widgets
        self.medical_var = tk.StringVar(self)
        self.medical_label = tk.Label(self, text="Medical Insurance Cost Per Month: ", 
                                      font=('Tahoma', 12, tk.NORMAL))
        self.medical_label.grid(row=13, column=0, sticky=tk.E)
        self.medical_entry = ttk.Entry(self, 
                                            font=('Tahoma', 12, tk.NORMAL), 
                                            textvariable=self.medical_var)
        self.medical_entry.grid(row=13, column=1, sticky=tk.W)

        # Save Changes Button
        self.save_button = ttk.Button(self, text='Save',  
                                      command=self.save_employee_info)
        self.save_button.grid(row=15, column=1, sticky=tk.W)
        
        
        
    def load_employee_form(self, employee):
        # Case where employee is already in database
        if employee != None and employee != "New Employee":
            # Then edit all employee info widgets to represent the database data
            self.f_name_var.set(employee.first_name)
            self.l_name_var.set(employee.last_name)
            self.e_id.set(employee.employee_id)
            self.e_wage.set(str(employee.wage))
            self.d_hours.set(str(employee.desired_hours))
            self.dep1.set(employee.primary_department)
            self.dep2.set(employee.alternate1_department)
            self.dep3.set(employee.alternate2_department)
            self.ovrt_var.set(employee.overtime)
            self.work_comp_var.set(employee.workmans_comp)
            self.soc_sec_var.set(employee.social_security)
            self.medical_var.set(employee.medical)
        # Case where employe in the list has not yet been added to database
        else:
            self.f_name_var.set("New Employee")
            self.l_name_var.set("")
            self.e_id.set(0)
            self.e_wage.set("7.5")
            self.d_hours.set("48")
            self.dep1.set("None")
            self.dep2.set("None")
            self.dep3.set("None")
            self.ovrt_var.set("40")
            self.work_comp_var.set("50")
            self.soc_sec_var.set("7.5")
            self.medical_var.set("0")

            
            
            
            
    # Should add functionality where if a name change is committed, we change the listbox
    # index changes as well...Also error of multiple selections when adding an employee
    def save_employee_info(self):
        # Before committing any changes to the database we check if certain data fields have valid entries
        errors = []
        f_name = self.f_name_var.get()
        if not isinstance(f_name, basestring):
            errors.append("Employee name must be alphanumeric characters. "
                          "Employee name currently is: %s" % f_name)
        l_name = self.l_name_var.get()
        if not isinstance(l_name, basestring):
            errors.append("Employee name must be alphanumeric characters. "
                          "Employee name currently is: %s" % l_name)
        employee_id = self.e_id.get()
        if type(employee_id) is not int:
            errors.append("Employee ID must be non-decimal number. "
                          "Employee ID currently is: %s" % employee_id)
        wage_value = self.e_wage.get()
        if type(wage_value) is not float:
            errors.append("Employee wage must be a number. "
                          "Wage currently is: %s" % wage_value)
        o_time = self.ovrt_var.get()
        medical_value = self.medical_var.get()
        work_comp = self.work_comp_var.get()
        social = self.soc_sec_var.get()
        #if type(medical_value) is not float:
        #    errors.append("Medical insurance cost must be a number. "
        #                  "Medical currently is: %s" % medical_value)
        if self.employee_id_conflict(employee_id):
            errors.append("Employee ID %s is already taken." % employee_id)
        if errors == []:
            employee = self.e_page.curr_sel_employee
            if employee != None and employee != "New Employee":
                employee.first_name = f_name
                employee.last_name = l_name
                employee.employee_id = employee_id
                employee.primary_department = self.dep1.get()
                employee.alternate1_department = self.dep2.get()
                employee.alternate2_department = self.dep3.get()
                employee.wage = wage_value
                employee.desired_hours = self.d_hours.get()
                employee.overtime = o_time
                employee.medical = medical_value
                employee.workmans_comp = work_comp
                employee.social_security = social   
                self.session.commit()
                self.e_page.update_e_list(employee)
            elif employee == "New Employee": 
                employee = Employees(employee_id, 
                                     f_name, l_name,
                                     self.dep1.get(), 
                                     self.dep2.get(), 
                                     self.dep3.get(),
                                     wage_value, 
                                     self.d_hours.get(),
                                     o_time,
                                     medical_value,
                                     work_comp, 
                                     social)
                self.session.add(employee)
                self.session.commit()
                self.e_page.update_e_list(employee)
        else:
            print "Errors were: ", errors
            # Print out the errors in errors array onto an error label
            	
            # Then once we have a reference to an Employee instance, 
            # set its values to the values in the data entry widgets
            # Then commit changes to the database
            
            
    # A function to test if an employee ID is already registered in the database
    # If that ID is already taken, return true, else return false.
    # That isn't really the issue I am trying to work out here, 
    # the issue I am trying to work out is the case where:
    # The user is trying to change the ID of an employee, 
    def employee_id_conflict(self, id):
        # We first get potential employee with id and then any current selected employee
        potential_employee = (self.session
                                  .query(Employees)
                                  .filter(Employees.employee_id == id)
                                  .first())
        employee = self.e_page.curr_sel_employee
        # Then check to see if there is a conflict in id
        if potential_employee == None or potential_employee == employee: # Case where no employee already has this ID or the employee itself has the ID
            return False
        else: # Case where an employee is already using this ID
            return True
            
            
    def add_new_e_info(self):
        self.f_name_var.set("New Employee")
        self.l_name_var.set("")
        self.e_id.set(0)
        self.e_wage.set("9.5")
        self.d_hours.set("40")
        self.dep1.set("None")
        self.dep2.set("None")
        self.dep3.set("None")
        self.ovrt_var.set("48")
        self.work_comp_var.set("50")
        self.soc_sec_var.set("7.5")
        self.medical_var.set("0")
        
          

class EmployeeRepeatUnavailable(tk.Frame):

    DAYS_TO_NUM = {'Sunday':6, 'Monday':0, 'Tuesday':1, 'Wednesday':2,
                    'Thursday':3, 'Friday':4, 'Saturday':5}

    def __init__(self, parent, session, e_page, calendar_page):
        tk.Frame.__init__(self, parent)
    
        self.session = session
        self.e_page = e_page
        self.cal = calendar_page
        
        
        # Unavailable day widgets
        self.unavailable_d_lb = tk.Listbox(self, height=18, width=30, 
                                           font=('Tahoma', 12, tk.NORMAL))
        self.unavailable_d_lb.pack(pady=16)
        # Parallel list to listbox
        self.unav_days = []
        
        self.remove_unav_day_b = ttk.Button(self, 
                                            text='Remove Unavailable Time',
                                            command=self.remove_unav_time)
        self.remove_unav_day_b.pack()
        
        
        # Widgets for adding an unavailable time
        self.unav_add_frame = ttk.LabelFrame(self, text='Add Unavailable Time')
        self.unav_add_frame.pack(pady=12)
        # Start time widgets
        self.unav_start_label = tk.Label(self.unav_add_frame, 
                                         text="Start Time: ", 
                                         font=('Tahoma', 12, tk.NORMAL))
        self.unav_start_label.grid(row=0, column=0)
        self.unav_start_te = TimeEntry(self.unav_add_frame)
        self.unav_start_te.grid(row=0, column=1)
        # End time widgets
        self.unav_end_label = tk.Label(self.unav_add_frame, 
                                       text="End Time: ", 
                                       font=('Tahoma', 12, tk.NORMAL))
        self.unav_end_label.grid(row=1, column=0)
        self.unav_end_te = TimeEntry(self.unav_add_frame)
        self.unav_end_te.grid(row=1, column=1)
        
        
        self.unav_weekday_label = tk.Label(self.unav_add_frame, 
                                           text="Weekday: ", 
                                           font=('Tahoma', 12, tk.NORMAL))
        self.unav_weekday_label.grid(row=2, column=0)
        self.unav_weekday_var = tk.StringVar(self.unav_add_frame)
        self.unav_weekday_var.set('Sunday')
        self.unav_weekday_cb = ttk.Combobox(self.unav_add_frame, 
                                            textvariable=self.unav_weekday_var,
                                            values=('Sunday', 'Monday', 
                                                    'Tuesday', 'Wednesday',
                                                    'Thursday', 'Friday', 'Saturday'),
                                            width=8,
                                            state='readonly')
        self.unav_weekday_cb.grid(row=2, column=1)
        self.add_unav_day_b = ttk.Button(self.unav_add_frame, 
                                            text='Add Unavailable Time', 
                                            command=self.add_unav_time)
                                                                                
                                            
        self.add_unav_day_b.grid(row=3, column=0, columnspan=2, pady=16)     
        
        
    def load_unav_times(self, employee):       
        """Load past and future vacations associated with employee. """
        # Delete any previously displayed vacations for different employee
        self.unavailable_d_lb.delete(0, tk.END)
        self.unav_days = []
        if employee != None and employee != "New Employee":
            self.unav_days = employee.get_unav_days()
            self.unav_days.sort(key=lambda v: v.start_time)
            self.unav_days.sort(key=lambda v: v.weekday)
            # Load the parallel lists into listbox
            for u in self.unav_days:
                self.unavailable_d_lb.insert(tk.END, 
                                             u.get_str())
            
    def remove_unav_time(self):
        if self.unavailable_d_lb.curselection() == ():
            return
        index =  self.unavailable_d_lb.curselection()[0]
        
        self.unavailable_d_lb.delete(index)
        unav_time = self.unav_days[index]
        
        self.session.delete(unav_time)
        self.session.commit()
        
        del self.unav_days[index]
        
        
        
    def add_unav_time(self):
        start_time = self.unav_start_te.get_time()
        end_time = self.unav_end_te.get_time()
        weekday = self.DAYS_TO_NUM[self.unav_weekday_var.get()]
        
        if start_time < end_time:
            employee = self.e_page.curr_sel_employee
            if employee != None and employee != "New Employee":

                unav_time = UnavailableTime(start_time, 
                                            end_time,
                                            weekday,
                                            employee.id)
                self.session.add(unav_time)
                employee.add_unav_time(unav_time)
                self.session.commit()
                # EDIT: Insert needs to both apply to correct lb and
                # keep everything sorted
                self.unavailable_d_lb.insert(tk.END, 
                                             unav_time.get_str())
                self.unav_days.append(unav_time)
               
               
        
class EmployeeVacations(tk.Frame):
        
        
    def __init__(self, parent, session, e_page, calendar_page):
        tk.Frame.__init__(self, parent)
    
        self.session = session
        self.e_page = e_page
        self.cal = calendar_page
        
        
        # Vacation and Absent Schedules
        self.future_past_nb = ttk.Notebook(self)
        self.future_past_nb.grid(row=1, column=0, columnspan=4, 
                                 padx=10, pady=10)
        self.future_v_frame = tk.Frame(self.future_past_nb)                            
        self.past_v_frame = tk.Frame(self.future_past_nb)
        self.future_past_nb.add(self.future_v_frame, text="Future Vacations")
        self.future_past_nb.add(self.past_v_frame, text="Past Vacations")
        
        # Future and past vacation listboxes
        self.future_v_lb = tk.Listbox(self.future_v_frame, 
                                      height=18, width=30, 
                                      font=('Tahoma', 12, tk.NORMAL))
        self.future_v_lb.pack()
        
        self.past_v_lb = tk.Listbox(self.past_v_frame, 
                                    height=18, width=30, 
                                    font=('Tahoma', 12, tk.NORMAL))
        self.past_v_lb.pack()
        # Parallel list for each listbox to contain the actual database items
        self.future_vacations = []
        self.past_vacations = []
        
        # Widgets for removing future and past vacation times
        self.remove_future_v_btn = ttk.Button(self.future_v_frame, 
                                          text='Remove Vacation', 
                                          command=self.remove_future_v)
        self.remove_future_v_btn.pack(pady=16)
        self.remove_past_v_btn = ttk.Button(self.past_v_frame, 
                                            text='Remove Vacation', 
                                            command=self.remove_past_v)
        self.remove_past_v_btn.pack(pady=16)
        
        # Widgets for adding a vacation time
        # Date spinbox widgets for user to pick date for vacations
        self.start_date_label = tk.Label(self, 
                                         text="Start Date ", 
                                         font=('Tahoma', 12, tk.NORMAL))
        self.start_date_label.grid(row=2, column=0, sticky=tk.E, pady=5)
        self.start_date = DateEntry(self, 
                                    font=('Tahoma', 12, tk.NORMAL), 
                                    border=0)
        self.start_date.grid(row=2, column=1, sticky=tk.W)
        
        self.end_date_label = tk.Label(self, 
                                       text="End Date ", 
                                       font=('Tahoma', 12, tk.NORMAL))
        self.end_date_label.grid(row=3, column=0, sticky=tk.E)
        self.end_date = DateEntry(self, 
                                  font=('Tahoma', 12, tk.NORMAL), 
                                  border=0)
        self.end_date.grid(row=3, column=1, sticky=tk.W)
        
        self.add_vacation = ttk.Button(self, 
                                    text='Add Vacation',  
                                    command=self.add_vacation)
        self.add_vacation.grid(row=4, column=0, columnspan=2, pady=12)
         
        
    def load_vacations(self, employee):
        """Load past and future vacations associated with employee. """
        # Delete any previously displayed vacations for different employee
        self.future_v_lb.delete(0, tk.END)
        self.past_v_lb.delete(0, tk.END)
        self.future_vacations = []
        self.past_vacations = []
        # Fetch current date to compare the time of schedules to be displayed
        now = datetime.datetime.now()
        current_date = datetime.datetime(now.year, now.month, 1, 0, 0 ,0)
        vacations = []
        if employee != None and employee != "New Employee":
            vacations = employee.get_absent_schedules()
            self.future_vacations = [v for v in vacations if v.end_datetime >= current_date]
            self.past_vacations = [v for v in vacations if v.end_datetime < current_date]
        
            self.future_vacations.sort(key=lambda v: v.start_datetime)
            self.past_vacations.sort(key=lambda v: v.start_datetime)
            # Load the parallel lists into respect listboxes
            for v in self.future_vacations:
                self.future_v_lb.insert(tk.END, v.get_str_dates())
            for v in self.past_vacations:
                self.past_v_lb.insert(tk.END, v.get_str_dates())
   
    
    def add_vacation(self):
        # Step 0: Button is clicked to call this function
        # Step 1: Create a string from the 
        # spinbox values for start_date and end_date
        # Step 2: create a Datetime.date() 
        # Step 3: check to see if this date object 
        # conflicts with any time schedules
        # 	-If conflict: flag user via pop-up box and tell the 
        #    datetime schedules that conflicts with 
        #	 with desired schedule, then don't commit anything, end function
        # 	-If no conflict: commit schedules to database,
        #    add to listbox and parallel list
        
        start_tuple = self.start_date.get()
        s_year = int(start_tuple[2])
        s_month = int(start_tuple[0])
        s_day = int(start_tuple[1])
        start_date = datetime.date(s_year, s_month, s_day)
        start_datetime = datetime.datetime(s_year, s_month, s_day, 0, 0, 0)
        
        
        end_tuple = self.end_date.get()
        e_year = int(end_tuple[2])
        e_month = int(end_tuple[0])
        e_day = int(end_tuple[1])
        end_date = datetime.date(e_year, e_month, e_day)
        end_datetime = datetime.datetime(e_year, e_month, e_day, 23, 59, 59)
        
        if start_datetime <= end_datetime:
        
            employee = self.e_page.curr_sel_employee
            
            conflicting_schedules = []
            
            if employee != None and employee != "New Employee":
                for t in employee.schedules:
                    if start_datetime < t.end_datetime and t.start_datetime < end_datetime:
                        conflicting_schedules.append(t)
                for t in employee.unavailable_schedules:
                    if start_datetime < t.end_datetime and t.start_datetime < end_datetime:
                        conflicting_schedules.append(t)
                        
                if conflicting_schedules == []:
                    unavailable_schedule = Unavailable_Schedule(start_datetime, 
                                                                end_datetime, 
                                                                employee.id)
                    self.session.add(unavailable_schedule)
                    employee.add_unavailable_schedule(unavailable_schedule)
                    self.session.commit()
                    # EDIT: Insert needs to both apply to correct lb and
                    # keep everything sorted
                    self.future_v_lb.insert(tk.END, 
                                            unavailable_schedule.get_str_dates())
                    self.future_vacations.append(unavailable_schedule)
                else:
                    for e in conflicting_schedules:
                        print 'Confliction schedules are...'
                        print e
                        # display errors in some sort of box, give option for 
                        # user to delete conflicting schedules? I almost want to say no...
                        # Then again, the purpose of this program 
                        # is to streamline retail scheduling...
                        # Should call another function because 
                        # there will be a lot of logic here
            else:
                print "Please select an employee already in Database"
                # print out errors, need a valid employee etc.
                
            
            # else display error box containing a 
            # printed list of all conflicing schedules. 
            # give option for user to delete 
            # conflicting schedules to add vacation day?
    	
        
    def remove_future_v(self):
        if self.future_v_lb.curselection() == ():
            return
        index =  self.future_v_lb.curselection()[0]
        
        self.future_v_lb.delete(index)
        un_schedule = self.future_vacations[index]
        
        self.session.delete(un_schedule)
        self.session.commit()
        
        del self.future_vacations[index]
        
    def remove_past_v(self):
        if self.past_v_lb.curselection() == ():
            return
        index = self.past_v_lb.curselection()[0]
        
        self.past_v_lb.delete(index)
        un_schedule = self.past_vacations[index]
        
        self.session.delete(un_schedule)
        self.session.commit()
        
        del self.past_vacations[index]
    
        
        
        
        
        
        
        
        