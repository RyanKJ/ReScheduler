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

class Schedule(Base):
    """ORM representation of an employee schedule
    
    A schedule has a start and end datetime to represent its duration. Each
    schedule is assigned to a department. There are optional booleans to 
    hide the start and/or end time of a schedule in the view (This is for 
    cases where the user wants to assign an employee to schedule with an
    undetermined end time, say black Friday.) Schedules may or may not have 
    an employee assigned to them. In the case there is an assigned employee,
    the cost() method can be called to determine the amount of USD this
    schedule costs.
    """
    
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
    
    employee_id = Column(Integer, ForeignKey('Employee.employee_id'), 
                         nullable = True)
    employee = relationship('Employee')
    
    def __init__(self, start_dt, end_dt, s_undetermined, e_undetermined, 
                 department):
        """Initialize a Schedule ORM object."""
        self.start_datetime = start_dt
        self.end_datetime = end_dt
        self.department = department
        self.s_undetermined_time = s_undetermined
        self.e_undetermined_time = e_undetermined
        
        # Using the start and end datetime objects, create correspoding start
        # and end time objects for comparison with time objects for Queries
        self.start_time = datetime.time(start_dt.hour, start_dt.minute)
        self.end_time = datetime.time(end_dt.hour, end_dt.minute)
        # Create cal_date for calendar month and year comparisons and sch_date
        # for Queries involving datetime.date() objects.
        self.calendar_date = datetime.date(start_dt.year, start_dt.month, 1)
        self.schedule_date = datetime.date(start_dt.year, start_dt.month,
                                           start_dt.day)
        
        
    def cost(self):
        """Calculate the cost of this schedule given assigned employee."""
        if self.employee_id == None:
            return 0
        timedelta = self.end_datetime - self.start_datetime
        hours = timedelta.seconds / 3600
        return hours * self.employee.wage


    
class Vacation(Base):
    """ORM representation of a vacation period with start and end date.
    
    A vacation is represented as two datetime.dates that represent the start
    and end dates of a vacation, and then the employee assigned to that given
    Vacation.
    """

    __tablename__ = 'unavailable'
    
    id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    end_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    
    employee_id = Column(Integer, ForeignKey('Employee.employee_id'),
                         nullable = True)
    employee = relationship('Employee')
    
    def __init__(self, start_datetime, end_datetime, employee_id):
        """Initialize a Vacation ORM object."""
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.employee_id = employee_id
        

    def get_str_dates(self):
        """Return a string formatted month, day, year of start/end dates."""
        start_str = self.start_datetime.strftime("%B %d, %Y")
        end_str = self.end_datetime.strftime("%B %d, %Y")
        return start_str + " - " + end_str
        
        
class UnavailableTime(Base):
    """ORM representation of a repeating unavailabile time period.
    
    An UnavailableTime or repeating unavailability is represented as two 
    datetime.time that represent the start and end times, an integer
    representing the day of the week, and an assigned employee for this 
    repeating unavailability.
    """

    WEEKDAY_TO_STR = {0: 'Mon', 1: 'Tu', 2: 'Wed', 3: 'Thu', 
                      4: 'Fri', 5: 'Sat', 6: 'Sun'}
                      
    __tablename__ = 'unavailable_time'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(Time)
    end_time = Column(Time)
    weekday = Column(Integer)
    
    employee_id = Column(Integer, ForeignKey('Employee.employee_id'),
                         nullable = True)
    employee = relationship('Employee')
    
    def __init__(self, start_time, end_time, weekday, employee_id):
        """Initialize a repeating unavailability ORM object."""
        self.start_time = start_time
        self.end_time = end_time
        self.weekday = weekday
        self.employee_id = employee_id
        
    
    def get_str(self):
        """Returns a string formatted weekday, start time - end time."""
        start_str = self.start_time.strftime("%I:%M %p")
        end_str = self.end_time.strftime("%I:%M %p")
        return self.WEEKDAY_TO_STR[self.weekday] + " " + start_str + " - " + end_str
        
        
        
class Employee(Base):
    """ORM representation of an employee.
    
    An employee is primarily represented by their employee_id which must be
    a unique identifier. Then extra information such as their first and last
    names, wage, departments they can work, desired hours, overtime, medical
    benefit cost per month, workmans comp and social security. Then there
    are foreign keys for schedules, vacations, and repeating unavailability
    an employee can be assigned to.
    """

    __tablename__ = 'Employee'
    
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
    
    schedules = relationship("Schedule")
    unavailable_schedules = relationship("Vacation")
    unav_time_schedules = relationship("UnavailableTime")
    
    
    def __init__(self, employee_id, first_name, last_name, p_department, 
                 alt1_department, alt2_department, wage, desired_hours, overtime,
                 medical, work_comp, soc_sec):
        """Initialize an Employee ORM object."""
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
        
        self.schedule = relationship("Schedule")
        self.vacation = relationship("Vacation")
        
        
    def add_schedule(self, schedule):
        """Add schedule to list of schedule's this employee is assigned to."""
        self.schedules.append(schedule)
    
    
    def remove_schedule(self, schedule):
        """Remove schedule from list of assigned schedules for this employee."""
        index = self.schedules.index(schedule)
        del self.schedules[index]
    
    
    def add_unavailable_schedule(self, vacation):
        """Add vacation to list of vacations's this employee is assigned to."""
        self.unavailable_schedules.append(vacation)
        
        
    def add_unav_time(self, unav_time):
        """Add unrepeating unavailabile to to this employee."""
        self.unav_time_schedules.append(unav_time)
        
        
    def get_absent_schedules(self):
        """Get all vacations of this employee."""
        return self.unavailable_schedules	
        
        
    def get_unav_days(self):
        """Get all unrepeating unavailabile schedules of this employee."""
        return self.unav_time_schedules
        
    
    def get_availability(self, schedule):
        """Get availability of employee given schedule.
        
        There are 5 levels of availability of an employee given a schedule.
        Available (A): there are no conflicts for this employee. Overtime (O):
        Employee has no conflicts except overtime. Unavailable repeat (U):
        employee has a repeating conflict that has some time overlap with the
        supplied schedule. Vacation (V): employee has vacation that has some
        overlap with the schedule, and Schedule (S): employee has another
        schedule that has some overlap with the schedule to be assigned.
        
        Note that in order to not have a schedule conflict (S) with an employee
        already assigned to that schedule we must remove the schedule from the 
        list of assigned schedules for this employee.
        """
        
        schedules = list(self.schedules)
        if schedule in schedules:
            schedules.remove(schedule)
        for t in schedules:
            if schedule.start_datetime < t.end_datetime and t.start_datetime < schedule.end_datetime:
                return '(S)'
        for t in self.unavailable_schedules:
            if schedule.start_datetime < t.end_datetime and t.start_datetime < schedule.end_datetime:
                return '(V)'
        same_day_unav = [s for s in self.unav_time_schedules if (s.weekday 
                                                                 == schedule.schedule_date.weekday())]
        for s in same_day_unav:
            if schedule.start_time < s.end_time and s.start_time < schedule.end_time:
                return '(U)'
        if self.calculate_weekly_hours(schedule) > self.overtime:
            return '(O)'
        return '(A)'
        
        
    def calculate_weekly_hours(self, schedule):
        """Calculate number of hours worked by employee for week of schedule."""
        return 0
    
    
        
class MonthSales(Base):
    """ORM representation of the total revenue for given month and year."""

    __tablename__ = 'Sales'
    
    id = Column(Integer, primary_key=True)
    month_and_year = Column(Date)
    total_sales = Column(Integer)
    
    def __init__(self, m_and_y, sales):
        """Initialize a MonthSales ORM object."""
        self.month_and_year = m_and_y
        self.total_sales = sales
        
        
    def get_string(self):
        """ Returns a string formatted to Month, Year Amount """
        date_str = self.month_and_year.strftime("%Y %B, Sales Total: ")
        amt_str = "$" + str(self.total_sales)
        return date_str + amt_str
        
        
class Department(Base):  
    """ORM representation of a department."""
    
    __tablename__ = 'Department'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __init__(self, department):
        """Initialize a Department ORM object."""
        self.name = department

        
def start_db(db_name, test=False):
    """Function to start database, for normal usage or for testing."""
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