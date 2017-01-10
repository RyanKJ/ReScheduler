"""
Module for the employee and department page.
"""

import Tkinter as tk
import ttk
import datetime
import bisect
import collections
from datetime_widgets import DateEntry, TimeEntry, yearify
from orm_models import Employee, Department, Vacation, UnavailableTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



class EmployeePage(tk.Frame):
    """
    Controller class for all employee composite widgets classes. There are 5 
    composite widget classes for Employee page: EmployeeList, a list of 
    employees, DepartmentList, a list of departments, EmployeeInfoForm, the 
    area where the user can edit a new or existing employee,
    EmployeeRepeatUnavailable, a form for the user to add unavailable repeats
    of an employee, and EmployeeVacations, a form to add a vacation for an
    employee.
    
    Employee page acts as the controller to let the different composite
    widgets talk to each other and to know the current selected employee.
    """
    
    def __init__(self, parent, session):
        """Initialize EmployeePage and the different composite widgets."""
        tk.Frame.__init__(self, parent)
        self.session = session
        self.curr_sel_employee = None
        
        # Left Panel Frame Widgets for Employee/Department Lists
        employee_department_nb = ttk.Notebook(self)
        employee_department_nb.pack(side="left", fill="both", expand=True,
                                    padx=10, pady=10)
        
        self.employee_list_frame = tk.Frame(employee_department_nb)
        self.employee_list_frame.pack()
        self.employee_list = EmployeeList(self.employee_list_frame, self)
        self.employee_list.pack()
        
        self.dep_list_frame = tk.Frame(employee_department_nb)
        self.dep_list_frame.pack()
        self.dep_list = DepartmentList(self.dep_list_frame, self)
        self.dep_list.pack()

        employee_department_nb.add(self.employee_list_frame, text="Employee List")
        employee_department_nb.add(self.dep_list_frame, text="Department List")
        
        
        # Center Panel Frame Widgets for Employee Info Form
        self.employee_info_frame = ttk.LabelFrame(self,
                                                  text='Employee Information')
        self.employee_info_frame.pack(side="left", fill="both", expand=True,
                                      padx=10, pady=24, anchor='center')
        self.e_info_form = EmployeeInfoForm(self.employee_info_frame, self)     
        self.e_info_form.pack()
                             

        # Right Panel Frame Widgets for Various Unavailability Lists
        self.unavailability_nb = ttk.Notebook(self)
        self.unavailability_nb.pack(side="left", fill="both", expand=True,
                                    padx=10, pady=10)

        self.repeat_unav_frame = tk.Frame(self.unavailability_nb,)
        self.repeat_unav_frame.pack(side="left", fill="both", expand=True,
                                      padx=10, pady=24, anchor='center')                            
        self.e_unav_form = EmployeeRepeatUnavailable(self.repeat_unav_frame, 
                                                     self) 
        self.e_unav_form.pack()                                        
                                      
                                      
        self.vacation_frame = tk.Frame(self.unavailability_nb)
        self.vacation_frame.pack(side="left", fill="both", expand=True,
                                      padx=10, pady=24, anchor='center')
        self.e_vacation_form = EmployeeVacations(self.vacation_frame, 
                                                 self)  
        self.e_vacation_form.pack()
        
        self.unavailability_nb.add(self.repeat_unav_frame, 
                                   text="Unavailable Days")
        self.unavailability_nb.add(self.vacation_frame, 
                                   text="Vacation Times")
                  
                  
    def get_employee(self, id):
        """Return employee in database given employee id."""
        employee = (self.session.query(Employee)
                                .filter(Employee.employee_id == id)
                                .first())
        return employee
        
                                   
    def load_employee_data(self, employee_id):
        """Load employee info, repeating unavailability, and vacations."""
        self.e_info_form.load_employee_form(employee_id)
        self.e_unav_form.load_unav_times(employee_id)
        self.e_vacation_form.load_vacations(employee_id)
        
        
    def update_e_list(self, employee_id):
        """Update list of employees in employee listbox."""
        self.employee_list.update_listbox(employee_id)
        
        
    def add_new_e_info(self):
        """Fill in employee info form as a new employee."""
        self.e_info_form.add_new_e_info()
                             
                                  
        
class EmployeeList(tk.Frame):
    """
    Composite widget to display the list of employees.
    
    EmployeeList loads all employees and displays them. It also contains two
    buttons to add and remove employees. If an employee is clicked on, it will
    use a callback that will tell EmployeeInfoForm to load the appropriate
    information for that employee.
    """
    
    employee_id_list = []
        
    def __init__(self, parent, controller):
        """Initialize EmployeeList widgets, load employees."""
    
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Create and load listbox and its parallel list
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
        self.load_listbox_and_parallel_list()
            
        # Add and remove employee buttons
        self.add_employee_button = ttk.Button(self, 
                                             text='Add Employee', 
                                             command=self.add_new_employee)
        self.add_employee_button.grid(row=9, column=0)
        self.remove_employee_button = ttk.Button(self, 
                                                text='Remove Employee', 
                                                command=self.remove_employee)
        self.remove_employee_button.grid(row=9, column=2)

        
    def load_listbox_and_parallel_list(self):
        """Load listbox of employee names and parallel list of employee_id."""
        employee_db_list = self.controller.session.query(Employee).all()
        employee_db_list.sort(key=lambda e: e.first_name)
        
        for e in employee_db_list:
            str = e.first_name + " " + e.last_name
            self.employee_listbox.insert(tk.END, str)
            
        self.employee_id_list = [e.employee_id for e in employee_db_list]
        
        
    def add_new_employee(self):
        """Add new employee to listbox."""
        self.employee_listbox.selection_clear(0, tk.END)
        self.employee_listbox.insert(tk.END, "New Employee")
        self.employee_listbox.selection_set(tk.END)
        self.controller.curr_sel_employee = "New Employee"
        
        self.controller.add_new_e_info()
       
        
        
    def load_employee(self, event):
        """Tell controller to load the employee that whose name was clicked."""
        employee_id = self.get_employee_id()
        self.controller.curr_sel_employee = employee_id
        self.controller.load_employee_data(employee_id)
        
    
    def remove_employee(self):
        """Delete employee from lb and tell controller to remove employee."""
        if self.employee_listbox.curselection() == ():
            return 
        index = self.employee_listbox.curselection()[0]
        self.employee_listbox.delete(index)
        # Employee in listbox may be new employee not in parallel list
        if index < len(self.employee_id_list):
            employee_id = self.employee_id_list[index]
            employee = self.controller.get_employee(employee_id)
            self.controller.session.delete(employee)
            self.controller.session.commit()
            del self.employee_id_list[index]

        
    def get_employee_id(self):
        """Get the employee id from lb click.
        
        Returns:
            None: if no element in listbox was selected
            employee_id: if employee existing in database is clicked
            "New Employee": A new employee that doesn't exist in database, but
                exists in the listbox.
        """
        if self.employee_listbox.curselection() == ():
            return None
        index = self.employee_listbox.curselection()[0]
        # Case where index is larger than length means that listbox curselect
        # refers to element not in parallel list, or, new employee.
        if index < len(self.employee_id_list):
            return self.employee_id_list[index]
        else:
            return "New Employee"

        
    def update_listbox(self, employee_id):
        """Update the name of employee in the listbox."""
        employee = self.controller.get_employee(employee_id)
        str = employee.first_name + " " + employee.last_name
        if employee_id in self.employee_id_list:
            index = self.employee_id_list.index(employee_id)
            self.employee_listbox.delete(index)
            self.employee_listbox.insert(index, str)
            self.employee_listbox.selection_set(index)
        else:
            self.employee_id_list.append(employee_id)
            list_of_names = self.employee_listbox.get(0, tk.END)
            for text in list_of_names:
                if text == "New Employee":
                    index = list_of_names.index(text)
                    self.employee_listbox.delete(index)
                    self.employee_listbox.insert(index, str)
                    self.employee_listbox.selection_clear(0, tk.END)
                    self.employee_listbox.selection_set(index)
                    break
            
         
        
class DepartmentList(tk.Frame):
    """
    Composite widget to display the list of departments.
    
    DepartmentList loads all departments and displays them. It also contains 
    two buttons to add and remove departments.
    """
    
    dep_list = []

    def __init__(self, parent, controller):
        """Initialize DepartmentList widgets, load departments and fill lb."""
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.department_listbox = tk.Listbox(self, 
                                             height=6, width=25, 
                                             font=('Tahoma', 14, tk.NORMAL))
        self.department_listbox.grid(row=11, column=0, 
                                     rowspan=6, columnspan=3,
                                     pady=8)
        
        self.dep_list = [d.name for d in 
                         self.controller.session.query(Department).all()]
        for d in self.dep_list:
            self.department_listbox.insert(tk.END, d)
        
        self.add_department_button = ttk.Button(self, 
                                               text='Add Department', 
                                               command=self.add_department)
        self.add_department_button.grid(row=20, column=0)
        self.add_dep_label = tk.Label(self, 
                                      text="New Department:", 
                                      font=('Tahoma', 14, tk.NORMAL))
        self.add_dep_label.grid(row=21, column=0, columnspan=2)
        
        self.dep_name = tk.StringVar(self)
        self.dep_entry = ttk.Entry(self, 
                                  font=('Tahoma', 14, tk.NORMAL), 
                                  textvariable=self.dep_name)
        self.dep_entry.grid(row=21, column=2)
        
        self.remove_department_button = ttk.Button(self, 
                                                  text='Remove Department', 
                                                  command=self.remove_department)
        self.remove_department_button.grid(row=20, column=2)
        
        
    def add_department(self):
        """Add department from listbox and database."""
        dep = Department(self.dep_name.get())
        self.controller.session.add(dep)
        self.controller.session.commit()
        
        self.department_listbox.insert(tk.END, self.dep_name.get())
        self.cal.dep_list.append(self.dep_name.get())
        
        
    def remove_department(self):
        """Remove department from listbox and database."""
        if self.department_listbox.curselection() == ():
            return
        index = self.department_listbox.curselection()[0]
        dep_str = self.department_listbox.get(index)
        db_department = (self.controller.session.query(Department)
                                     .filter(Department.name == dep_str)
                                     .first())
        self.controller.session.delete(db_department)
        self.controller.session.commit()
        self.department_listbox.delete(index)
        del self.cal.dep_list[index]
        self.cal.d['menu'].delete(index)
        
                   
        
class EmployeeInfoForm(tk.Frame):
    """
    Composite widget to display information about the employee.
    
    EmployeeInfoForm is given an employee id number which is then used to fetch
    the employee information from the database. All relevant information about
    the employee is loaded. Then if the user clicks save, the class validates
    the information and if it is appropriate information is then committed to
    the database.
    """

    def __init__(self, parent, controller):
        """Init widgets to display employee information and save button."""
        tk.Frame.__init__(self, parent)
        self.controller = controller
          
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
        
        
    def load_employee_form(self, employee_id):
        """Load employee information into the various fields."""
        if employee_id != None and employee_id != "New Employee":
            employee = self.controller.get_employee(employee_id)
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
        else:
            self.add_new_e_info()
          
    
    def save_employee_info(self):
        """Save information in fields to employee in database.
        
        First the method checks to make sure valid entries were supplied for
        the values. Then the method commits these values to the employee in 
        the database. If the controller says the current employee is 
        "New Employee", then this method creates a new employee in database
        then tells the controller to update the EmployeeList.
        """
        
        errors = []
        f_name = self.f_name_var.get()
        if not isinstance(f_name, basestring):
            errors.append("Employee name must be alphanumeric characters. "
                          "Employee name currently is: %s" % f_name)
        l_name = self.l_name_var.get()
        if not isinstance(l_name, basestring):
            errors.append("Employee name must be alphanumeric characters. "
                          "Employee name currently is: %s" % l_name)
        new_e_id = self.e_id.get()
        if type(new_e_id) is not int:
            errors.append("Employee ID must be non-decimal number. "
                          "Employee ID currently is: %s" % new_e_id)
        wage_value = self.e_wage.get()
        if type(wage_value) is not float:
            errors.append("Employee wage must be a number. "
                          "Wage currently is: %s" % wage_value)
        o_time = self.ovrt_var.get()
        medical_value = self.medical_var.get()
        work_comp = self.work_comp_var.get()
        social = self.soc_sec_var.get()
        if self.employee_id_conflict(new_e_id):
            errors.append("Employee ID %s is already taken." % new_e_id)
        if errors == []:
            employee_id = self.controller.curr_sel_employee
            if employee_id != None and employee_id != "New Employee":
                employee = self.controller.get_employee(employee_id)
                employee.first_name = f_name
                employee.last_name = l_name
                employee.employee_id = new_e_id
                employee.primary_department = self.dep1.get()
                employee.alternate1_department = self.dep2.get()
                employee.alternate2_department = self.dep3.get()
                employee.wage = wage_value
                employee.desired_hours = self.d_hours.get()
                employee.overtime = o_time
                employee.medical = medical_value
                employee.workmans_comp = work_comp
                employee.social_security = social   
                self.controller.session.commit()
                self.controller.update_e_list(new_e_id)
            elif employee_id == "New Employee": 
                employee = Employee(new_e_id, 
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
                self.controller.session.add(employee)
                self.controller.session.commit()
                self.controller.update_e_list(new_e_id)
        else:
            print "Errors were: ", errors
            # Replace with warning dialog
            

    def employee_id_conflict(self, id):
        """Return true if there exists an employee id conflict.
        
        There is only a conflict if there is an employee with the supplied
        id and that employee is not currently selected.
        """
        
        potential_employee = (self.controller.session
                                  .query(Employee)
                                  .filter(Employee.employee_id == id)
                                  .first())
        if potential_employee == None or potential_employee.employee_id == id:
            return False
        else:
            return True
            
            
    def add_new_e_info(self):
        """Fill out employee info widgets with new employee default values."""
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
    """
    Form for a user to enter in repeat unavailabilities
    
    EmployeeRepeatUnavailable is a composite widget consisting of time widgets
    widgets to enter in a day of the week, and add and remove buttons. The
    employee id for employee to be assigned is supplied by the controller.
    """

    unav_days = []
    DAYS_TO_NUM = {'Sunday':6, 'Monday':0, 'Tuesday':1, 'Wednesday':2,
                    'Thursday':3, 'Friday':4, 'Saturday':5}

    def __init__(self, parent, controller):
        """Initialize widgets for adding and removing repeat unavailabilities."""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.unavailable_d_lb = tk.Listbox(self, height=18, width=30, 
                                           font=('Tahoma', 12, tk.NORMAL))
        self.unavailable_d_lb.pack(pady=16)
        
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
        
        
    def load_unav_times(self, employee_id):       
        """Load repeat unavailabilities associated with employee."""
        self.unavailable_d_lb.delete(0, tk.END)
        self.unav_days = []
        if employee_id != None and employee_id != "New Employee":
            employee = self.controller.get_employee(employee_id)
            self.unav_days = employee.get_unav_days()
            self.unav_days.sort(key=lambda v: v.start_time)
            self.unav_days.sort(key=lambda v: v.weekday)
            for u in self.unav_days:
                self.unavailable_d_lb.insert(tk.END, u.get_str())
            self.unav_days = [u.id for u in self.unav_days]                                 
            
            
    def remove_unav_time(self):
        """Remove repeat unavailability clicked from listbox."""
        if self.unavailable_d_lb.curselection() == ():
            return
        index = self.unavailable_d_lb.curselection()[0]
        self.unavailable_d_lb.delete(index)
        
        unav_time_id = self.unav_days[index]
        unav_time = (self.controller.session.query(UnavailableTime)
                                .filter(UnavailableTime.id == unav_time_id)
                                .first())
        self.controller.session.delete(unav_time)
        self.controller.session.commit()
        
        del self.unav_days[index]
        
        
    def add_unav_time(self):
        """Add repeat unavailability to listbox and database."""
        start_time = self.unav_start_te.get_time()
        end_time = self.unav_end_te.get_time()
        weekday = self.DAYS_TO_NUM[self.unav_weekday_var.get()]
        
        if start_time < end_time:
            employee_id = self.controller.curr_sel_employee
            if employee_id != None and employee_id != "New Employee":

                unav_time = UnavailableTime(start_time, 
                                            end_time,
                                            weekday,
                                            employee_id)
                self.controller.session.add(unav_time)
                self.controller.session.commit()
                employee = self.controller.get_employee(employee_id)
                employee.add_unav_time(unav_time)
                self.controller.session.commit()
                # Insert newly added unavailable to listbox for display
                self.unavailable_d_lb.insert(tk.END, 
                                             unav_time.get_str())
                self.unav_days.append(unav_time.id)
               
               
        
class EmployeeVacations(tk.Frame):
    """
    Form for a user to enter in employee vacations
    
    EmployeeVacations is a composite widget consisting of date widgets  to
    enter the start and end dates of a vacation. The employee id for employee
    to be assigned is supplied by the controller.
    """ 
        
    def __init__(self, parent, controller):
        """Initialize widgets for adding and removing vacations."""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
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
         
        
    def load_vacations(self, employee_id):
        """Load past and future vacations associated with employee."""
        self.future_v_lb.delete(0, tk.END)
        self.past_v_lb.delete(0, tk.END)
        self.future_vacations = []
        self.past_vacations = []
        now = datetime.datetime.now()
        current_date = datetime.datetime(now.year, now.month, 1, 0, 0 ,0)
        vacations = []
        if employee_id != None and employee_id != "New Employee":
            employee = self.controller.get_employee(employee_id)
            vacations = employee.get_absent_schedules()
            self.future_vacations = [v for v in vacations if v.end_datetime >= current_date]
            self.past_vacations = [v for v in vacations if v.end_datetime < current_date]
        
            self.future_vacations.sort(key=lambda v: v.start_datetime)
            self.past_vacations.sort(key=lambda v: v.start_datetime)
            for v in self.future_vacations:
                self.future_v_lb.insert(tk.END, v.get_str_dates())
            for v in self.past_vacations:
                self.past_v_lb.insert(tk.END, v.get_str_dates())
            # We shed the ORM representation and keep parallel list of id's
            self.future_vacations = [v.id for v in self.future_vacations]
            self.past_vacations = [v.id for v in self.past_vacations]
   
    
    def add_vacation(self):
        """Add vacation to selected employee, warn user if conflicts exist.
        
        add_vacation checks for any conflicts with schedules they are already
        assigned to. If there is any time overlap between the vacation to be
        assigned to employee and schedules that employee is already assigned to
        the user is warned and given a dialog box to ask them if they are sure
        they want to assign the vacation to the employee.
        """
        
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
        
            employee_id = self.controller.curr_sel_employee
            
            conflicting_schedules = []
            
            if employee_id != None and employee_id != "New Employee":
                employee = self.controller.get_employee(employee_id)
                for t in employee.schedules:
                    if start_datetime < t.end_datetime and t.start_datetime < end_datetime:
                        conflicting_schedules.append(t)   
                if conflicting_schedules == []:
                    vacation = Vacation(start_datetime, end_datetime, 
                                        employee_id)
                    self.controller.session.add(vacation)
                    employee.add_unavailable_schedule(vacation)
                    self.controller.session.commit()
                    self.future_v_lb.insert(tk.END, 
                                            vacation.get_str_dates())
                    self.future_vacations.append(vacation.id)
                else:
                    for e in conflicting_schedules:
                        print 'Confliction schedules are...'
                        print e
                        # Replace with warning dialog
            else:
                print "Please select an employee already in Database"
                # Replace with warning dialog
                
        
    def remove_future_v(self):
        """Remove vacation from future listbox and database."""
        if self.future_v_lb.curselection() == ():
            return
        index =  self.future_v_lb.curselection()[0]
        
        self.future_v_lb.delete(index)
        vacation_id = self.future_vacations[index]
        vacation = (self.controller.session.query(Vacation)
                                .filter(Vacation.id == vacation_id)
                                .first())
        
        
        self.controller.session.delete(vacation)
        self.controller.session.commit()
        
        del self.future_vacations[index]
        
        
    def remove_past_v(self):
        """Remove vacation from past listbox and database."""
        if self.past_v_lb.curselection() == ():
            return
        index = self.past_v_lb.curselection()[0]
        
        self.past_v_lb.delete(index)
        vacation_id = self.past_vacations[index]
        vacation = (self.controller.session.query(Vacation)
                                .filter(Vacation.id == vacation_id)
                                .first())
        
        self.controller.session.delete(vacation)
        self.controller.session.commit()
        
        del self.past_vacations[index]
    
        
        
        
        
        
        
        
        