"""
Module for the database ORM representation
"""

import datetime
import calendar
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Time, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

Base = declarative_base()

class DB_Schedule(Base):
    
    __tablename__ = 'schedules'
        
        
    id = Column(Integer, primary_key=True)
    calendar_date = Column(Date)
    schedule_date = Column(Date)
    start_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    end_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    start_time = Column(Time)
    end_time = Column(Time)
    department = Column(String)
    s_undetermined_time = Column(Boolean)
    e_undetermined_time = Column(Boolean)
    
    employee_id = Column(Integer, ForeignKey('Employees.employee_id'), 
                         nullable = True)
    employee = relationship('Employees')
    
    def __init__(self, start_dt, end_dt, s_undetermined, e_undetermined, 
                 department):

        self.start_datetime = start_dt
        self.end_datetime = end_dt
        self.department = department
        self.s_undetermined_time = s_undetermined
        self.e_undetermined_time = e_undetermined
        
        # Using the start and end datetime objects, create correspoding start
        # and end time objects for comparison with time objects
        self.start_time = datetime.time(start_dt.hour, start_dt.minute)
        self.end_time = datetime.time(end_dt.hour, end_dt.minute)
        # Create cal_date for calendar month and year comparisons and sch_date
        # for date comparisons
        self.calendar_date = datetime.date(start_dt.year, start_dt.month, 1)
        self.schedule_date = datetime.date(start_dt.year, start_dt.month,
                                           start_dt.day)
        
        
    def cost(self):
        # Cost is a fairly straight forward function...in theory
        # 1 - Get a floating number that represents the amount of hours
        #     the employee is scheduled, so, if a schedule is from 10 am to
        #     4:45 pm, then the employee will work 6.75 hours
        # 2 - Fetch employee wage
        #     Return hours worked times employee wage. Return 0 if no employee
        #     is assigned. The only difficult part is converting a time delta.
        if self.employee_id == None:
            return 0
            
        timedelta = self.end_datetime - self.start_datetime
        hours = timedelta.seconds / 3600
        return hours * self.employee.wage
        
    def get_time(self):
        hour = star
        
    
    
class Unavailable_Schedule(Base):

    __tablename__ = 'unavailable'
    
    id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    end_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    
    employee_id = Column(Integer, ForeignKey('Employees.employee_id'),
                         nullable = True)
    employee = relationship('Employees')
    
    def __init__(self, start_datetime, end_datetime, employee_id):
        
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.employee_id = employee_id
        
    # Returns a string formatted start month, start day, start year - end month, end day, end year
    def get_str_dates(self):
        start_str = self.start_datetime.strftime("%B %d, %Y")
        end_str = self.end_datetime.strftime("%B %d, %Y")
        return start_str + " - " + end_str
        
        
class UnavailableTime(Base):

    WEEKDAY_TO_STR = {0: 'Mon', 1: 'Tu', 2: 'Wed', 3: 'Thu', 
                      4: 'Fri', 5: 'Sat', 6: 'Sun'}
    __tablename__ = 'unavailable_time'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(Time)
    end_time = Column(Time)
    weekday = Column(Integer)
    
    employee_id = Column(Integer, ForeignKey('Employees.employee_id'),
                         nullable = True)
    employee = relationship('Employees')
    
    def __init__(self, start_time, end_time, weekday, employee_id):
        
        self.start_time = start_time
        self.end_time = end_time
        self.weekday = weekday
        self.employee_id = employee_id
        
    # Returns a string formatted start month, start day, start year - end month, end day, end year
    def get_str(self):
        start_str = self.start_time.strftime("%I:%M %p")
        end_str = self.end_time.strftime("%I:%M %p")
        return self.WEEKDAY_TO_STR[self.weekday] + " " + start_str + " - " + end_str
        
class Employees(Base):

    __tablename__ = 'Employees'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    employee_id = Column(Integer)
    primary_department = Column(String)
    alternate1_department = Column(String)
    alternate2_department = Column(String)
    wage = Column(Integer)
    desired_hours = Column(Integer)
    scheduled_hours = Column(Integer)
    overtime = Column(Integer)
    medical = Column(Integer)
    workmans_comp = Column(Integer)
    social_security = Column(Integer)
    
    # These relationships are how we calculate the validity of assignment 
    #to a schedule, total scheduled hours, total cost of employment, etc.
    schedules = relationship("DB_Schedule")
    unavailable_schedules = relationship("Unavailable_Schedule")
    unav_time_schedules = relationship("UnavailableTime")
    
    def __init__(self, employee_id, first_name, last_name, p_department, 
                 alt1_department, alt2_department, wage, desired_hours, overtime,
                 medical, work_comp, soc_sec):
    
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.primary_department = p_department
        self.alternate1_department = alt1_department
        self.alternate2_department = alt2_department
        self.wage = wage
        self.desired_hours = desired_hours
        self.scheduled_hours = 0
        self.overtime = overtime
        self.medical = medical
        self.workmans_comp = work_comp
        self.social_security = soc_sec
        
        self.schedule = relationship("DB_Schedule")
        self.unavailable_schedule = relationship("Unavailable_Schedule")
        
    def add_schedule(self, db_schedule):
        self.schedules.append(db_schedule)
    
    def remove_schedule(self, db_schedule):
        index = self.schedules.index(db_schedule)
        del self.schedules[index] # Can this be made more succinct?
    
    def add_unavailable_schedule(self, unavailable_schedule):
        self.unavailable_schedules.append(unavailable_schedule)
        
    def add_unav_time(self, unav_time):
        self.unav_time_schedules.append(unav_time)
        
    def get_absent_schedules(self):
        return self.unavailable_schedules	
        
    def get_unav_days(self):
        return self.unav_time_schedules
        
    # Given a schedule returns true or false boolean
    # True if there is no scheduling conflict, false is there is.
    def get_availability(self, db_schedule):
        # If this employee is assigned to the db_schedule itself already, we
        # don't want to consider this a schedule conflict.
        schedules = list(self.schedules)
        if db_schedule in schedules:
            schedules.remove(db_schedule)
        for t in schedules:
            if db_schedule.start_datetime < t.end_datetime and t.start_datetime < db_schedule.end_datetime:
                return '(S)'
        for t in self.unavailable_schedules:
            if db_schedule.start_datetime < t.end_datetime and t.start_datetime < db_schedule.end_datetime:
                return '(V)'
        same_day_unav = [s for s in self.unav_time_schedules if (s.weekday 
                                                                 == db_schedule.schedule_date.weekday())]
        for s in same_day_unav:
            if db_schedule.start_time < s.end_time and s.start_time < db_schedule.end_time:
                return '(U)'
        if self.calculate_weekly_hours(db_schedule) > self.overtime:
            return '(O)'
        return '(A)'
        
    # Adds up all the hours scheduled for this employee
    # Find a way to filter all schedules for this employee filtered to same
    # week as the supplied schedule, then calculate the summed time delta of 
    # all the 
    def calculate_weekly_hours(self, schedule):
        return 0
    
    # Calculate cost to employ employee for that month's calendar
    def calculate_cost(self):
        pass
        
class MonthSales(Base):  

    __tablename__ = 'Sales'
    id = Column(Integer, primary_key=True)
    month_and_year = Column(Date)
    total_sales = Column(Integer)
    
    def __init__(self, m_and_y, sales):
    
        self.month_and_year = m_and_y
        self.total_sales = sales
        
        
    def get_string(self):
        """ Returns a string formatted to Month, Year Amount """
        date_str = self.month_and_year.strftime("%Y %B, Sales Total: ")
        amt_str = "$" + str(self.total_sales)
        return date_str + amt_str
        
        
class Department(Base):  


    __tablename__ = 'Departments'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __init__(self, department):
        self.name = department

        
def start_db(db_name, test=False):
    db = 'sqlite:///' + db_name + '.db'
    if test:
        db = 'sqlite:///' + db_name + 'test.db'

    engine = create_engine(db, echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Case where user starts program, but no departments in database
    departments = session.query(Department).all()
    if departments == [] and not test:
        dep_list = ["Front", "Office", "Designers", "Facilities", "Drivers"]
        for d in dep_list:
            dep = Department(d)
            session.add(dep)
        session.commit()

        
    return session