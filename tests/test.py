"""
Exhaustively enumerate cases for:
-get_availability
-get_eligables
"""

import unittest
import orm_models as orm
import datetime
from test_doubles import DayModelDummy
from calendar_page import EligableModel


def create_department(session, dep):
    """Create department given string dep, return department object."""
    department = orm.Department(dep)        
    session.add(department)
    session.commit()
                   
    return department
    
    
def create_employee(session, id, f_name="John", l_name="Doe", p_dep="Front",
                    alt1_dep="None", alt2_dep="None", wage="9.5", d_hours="40",
                    overtime="48", medical="0", work_comp="50", social_s="7.5"):
    """Create employee object, commit and return created employee."""     
    employee = orm.Employees(id, f_name, l_name, p_dep, alt1_dep, alt2_dep,
                             wage, d_hours, overtime, medical, work_comp, 
                             social_s)                            
    session.add(employee)
    session.commit()
                   
    return employee

    
def create_schedule(session, start_dt, end_dt, dep,
                    s_undet=False, e_undet=False):
    """Create schedule object, commit and return created schedule."""
    schedule = orm.DB_Schedule(start_dt, end_dt, s_undet, e_undet, dep)                           
    session.add(schedule)
    session.commit()
                   
    return schedule
    
    
def assign_schedule(session, employee, schedule):
    """Assign schedule to supplied employee."""
    employee.add_schedule(schedule)
    session.commit()
    
    
def remove_schedule(session, schedule):
    """Delete schedule from database."""
    session.delete(schedule)
    session.commit()
    
    
def create_vacation(session, start_dt, end_dt, employee_id):
    """Create schedule object, commit and return created schedule."""
    vacation = orm.Unavailable_Schedule(start_dt, end_dt, employee_id)                           
    session.add(vacation)
    session.commit()
                   
    return vacation
    
    
def remove_vacation(session, vacation):
    """Delete vacation (unavailable schedule) from database."""
    session.delete(vacation)
    session.commit()    

    
    
def create_unavailable(session, start_time, end_time, weekday, employee_id):
    """Create unavailable repeat object, commit and return it."""
    unavailable_repeat = orm.UnavailableTime(start_time, end_time, 
                                             weekday, employee_id)                           
    session.add(unavailable_repeat)
    session.commit()
                   
    return unavailable_repeat
    

def get_overlapping_schedule(session, schedule, time_delta, overlap_style):
    """
    Return a schedule that will overlap according to time_delta and style
    
    There are 4 ways an interval/period of time can overlap for a schedule that 
    is assigned. An overlap between the start time but not end time 'START', 
    overlap of end time but not start time 'END', an overlap of a schedule that 
    fits inside the schedule 'INNER', and an overlap of the schedule whose 
    start and end times lie outside the assigned schedule 'OUTER'. One can 
    think of these overlaps as the different possible intersections of 2 sets 
    that are real-number intervals [a, b] intersect [c, d] where a, b, c, d 
    are the start and end times respectively of the 2 time intervals.
    
    Args:
        schedule: db schedule for which to create an overlapping schedule with.
        time_delta: the amount of overlapped time between the supplied
            schedule and the schedule to be created.
        overlap_style: the style of overlap between the two schedules desired.
    Returns:
        A db schedule object that overlaps with supplied schedule by the
        time_delta amount of time in the overlapping style supplied.
    """
    
    start = schedule.start_datetime
    end = schedule.end_datetime
    dep = schedule.department
    
    if overlap_style == 'START':
        new_start = start - time_delta
        new_end = start + time_delta
        overlap_schedule = create_schedule(session, new_start, new_end, dep)
        return overlap_schedule
        
    elif overlap_style == 'END':
        new_start = end - time_delta
        new_end = end + time_delta
        overlap_schedule = create_schedule(session, new_start, new_end, dep)
        return overlap_schedule    
        
    elif overlap_style == 'INNER':
        new_start = start + time_delta
        new_end = end - time_delta
        overlap_schedule = create_schedule(session, new_start, new_end, dep)
        return overlap_schedule
        
    elif overlap_style == 'OUTER':
        new_start = start - time_delta
        new_end = end + time_delta
        overlap_schedule = create_schedule(session, new_start, new_end, dep)
        return overlap_schedule
        
    else:
        print "Error: Invalid input for overlap_style parameter."


        
class AvailabilityTest(unittest.TestCase):
    """
    Create parent class for testing the different cases of get_availability
    
    get_availability can return 5 different string 'flags' that signal a
    given employee's availability given a schedule to assign them: 
    available (A), overtime conflict (O), unavailable repeat conflict (U), 
    vacation conflict (V), and an already assigned schedule conflict (S). This 
    parent class sets up and tears down the common states required for these 
    different cases: an employee and a schedule to assign to that employee.
    For testing purposes the schedule to be assigned will always be February 
    14th, 2017, from 11 am to 1 pm in the 'Front' department.
    
    For (S), (U), (V) we test cases of time overlapping. There are 4 ways an
    interval/period of time can overlap for a schedule that is assigned. 
    An overlap between the start time but not end time 'START', overlap of end
    time but not start time 'END', an overlap of a schedule that fits inside 
    the schedule 'INNER', and an overlap of the schedule whose start and end 
    times lie outside the assigned schedule 'OUTER'. One can think of these
    overlaps as the different possible intersections of 2 sets that are 
    real-number intervals [a, b] intersect [c, d] where a, b, c, d are the 
    start and end times respectively of the 2 time intervals.
    
    For (O) we test assigning 6 8-hour schedules around February 14th, 2017,
    then assign one more schedule which should put the employee into overtime 
    for that week-period.
    
    For (A) we test that all the warning flags are absent.
    """
    
    OVERLAP_STYLES = ['START', 'END', 'INNER', 'OUTER']
    
    def setUp(self):
        """
        Get a session, create employee and department, along with any other 
        set up requied to create the employee and department.
        """
        
        self.session = orm.start_db('33', True)
                 
        self.department = create_department(self.session, 'Front')
        self.employee = create_employee(self.session, 'Bob')
        
        self.dt = datetime.datetime(2017, 2, 14, 12, 0)
        self.schedule_length = datetime.timedelta(0, 3600) # 3600 sec = 1 Hour
        self.start = self.dt - self.schedule_length
        self.end = self.dt + self.schedule_length
        self.schedule = create_schedule(self.session, self.start, self.end, 
                                        self.department.name)
        
        
    def tearDown(self):
        """Remove everything from the database."""
        employees = self.session.query(orm.Employees).all()
        for e in employees:
            self.session.delete(e)
        
        departments = self.session.query(orm.Department).all()
        for d in departments:
            self.session.delete(d)

        schedules = self.session.query(orm.DB_Schedule)
        for s in schedules:
            self.session.delete(s)
            
        vacations = self.session.query(orm.Unavailable_Schedule)
        for v in vacations:
            self.session.delete(v)
            
        unavailable_repeats = self.session.query(orm.UnavailableTime)
        for u_re in unavailable_repeats:
            self.session.delete(u_re)
        
        self.session.commit()
        
        
        
class ScheduleConflictTest(AvailabilityTest):
    """Tests where availability results in a schedule conflict."""
    
    
    def test_schedule_conflict(self):
        """Test for assigning schedule that overlaps with pre-assigned schedule
            
        Create 4 different schedules that will each have a 15 minute overlap
        in the 4 possible overlapping cases that can occur between intersecting
        time-periods.
        """
        
        t_delta = datetime.timedelta(0, 900) # 15 minutes
        for style in self.OVERLAP_STYLES:
            overlap_sch = get_overlapping_schedule(self.session,
                                                   self.schedule, 
                                                   t_delta, style)
            assign_schedule(self.session, self.employee, overlap_sch)
            availability = self.employee.get_availability(self.schedule)
            err_msg = 'Overlap style "%s" has failed' % style
            self.assertEqual(availability, '(S)', msg=err_msg)
            # Remove assigned schedule before testing next style
            remove_schedule(self.session, overlap_sch)
            
            
    def test_one_second_conflict(self):
        """Assert that one second of conflict means employee not available."""
        t_delta = datetime.timedelta(0, 1) # 1 second
        for style in self.OVERLAP_STYLES:
            overlap_sch = get_overlapping_schedule(self.session,
                                                   self.schedule, 
                                                   t_delta, style)
            assign_schedule(self.session, self.employee, overlap_sch)
            availability = self.employee.get_availability(self.schedule)
            err_msg = 'Overlap style "%s" has failed' % style
            self.assertEqual(availability, '(S)', msg=err_msg)
            # Remove assigned schedule before testing next style
            remove_schedule(self.session, overlap_sch)
   
        
class VacationConflictTest(AvailabilityTest):
    """Tests where availability results in a vacation conflict."""
    
    
    def test_vacation_conflict(self):
        """Create a vacation that occurs on February 14th, 2017."""
        start = datetime.datetime(2017, 2, 14, 0, 0, 0)
        end = datetime.datetime(2017, 2, 14, 23, 59, 59)
        vacation = create_vacation(self.session, start, end, 
                                   self.employee.employee_id)
        availability = self.employee.get_availability(self.schedule)
        self.assertEqual(availability, '(V)', msg='Vacation conflict failed')
          
    
    
class UnavailableConflictTest(AvailabilityTest):
    """Tests where availability results in an unavailable repeat conflict."""
    
    
    def test_unavailable_repeat_conflict(self):
        """Create an unavailable repeat that occurs on Tuesday from 12-4 pm."""
        start_time = datetime.time(12, 0)
        end_time = datetime.time(16, 0)
        weekday = 1 # Tuesday
        unavailable = create_unavailable(self.session, start_time, end_time, 
                                         weekday, self.employee.employee_id)
                                         
        availability = self.employee.get_availability(self.schedule)
        self.assertEqual(availability, '(U)', msg='Unavailable repeat failed')

     
        
class OvertimeConflictTest(AvailabilityTest):
    """calculate_weekly_hours method has not yet been implemented."""
    pass
        
        
        
class NoConflictTest(AvailabilityTest):    
    """Tests where availability results in no conflicts at all."""    
            
            
    def test_no_conflict(self):
        """
        Test for assigning with no overlaps of other schedules.
        
        Build 2 schedules: one schedule that ends exactly before the schedule
        to be assigned starts and one that starts exactly after the schedule
        to be assigned ends.
        """
        
        b_start = datetime.datetime(2017, 2, 14, 9, 0)
        b_end = datetime.datetime(2017, 2, 14, 11, 0)
        before_sch = create_schedule(self.session, b_start, b_end, 
                                     self.department.name)        
        assign_schedule(self.session, self.employee, before_sch)
        
        a_start = datetime.datetime(2017, 2, 14, 13, 0)
        a_end = datetime.datetime(2017, 2, 14, 18, 0)
        after_sch = create_schedule(self.session, a_start, a_end, 
                                     self.department.name)        
        assign_schedule(self.session, self.employee, after_sch)
           
        availability = self.employee.get_availability(self.schedule)
        self.assertEqual(availability, '(A)', msg='No conflict')
        

        
class GetEligablesTest(unittest.TestCase): 
    """
    get_eligables is ultimately a sorting method using the heuristic of 
    'availability'. For get_eligables, availability is defined by the
    get_available method which has 5 tiers of availability: available with no
    conflicts, available but working overtime, unavailable due to a repeating
    unavailable (Employee can't work Tuesdays 10 am - 2 pm), unavailable due to
    vacation, and unavailable because the employee is already assigned to a 
    schedule that overlaps with the schedule the user is trying to assign.
    
    In addition to these 5 tiers of availability, within each tier employees
    are ranked by if the department of the schedule to be assigned is their
    primary department. So, if someone primarily works front, they are more
    eligable than someone who could work front, but typically does not and 
    works in some other department. So get_eligables sorts the whole list of
    employees according to get_availability, then sorts each tier sub-list by 
    primary and secondary department status. 
    
    Therefore, in order to test get_eligables, at least 11 employees are needed: 
    5 tiers of availability * 2 primary or secondary department + 1 employee
    that does not have the schedule department at all either as primary or 
    secondary, thus should never appear on the list of eligables.
    """
    
    EMPLOYEE_NAMES = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I'}
    employees = []
    
    def setUp(self):
        """
        Set up the 2 departments, 11 employees, schedule to get eligables 
        from, eligable model that contains the get_eligable method.
        
        get_eligables is ultimately a sorting method for the heuristic of
        'availability'. For get_eligables, availability is defied 
        """
        
        self.session = orm.start_db('33', True)
                 
        self.dep1 = create_department(self.session, 'Front')
        self.dep2 = create_department(self.session, 'Designer')
        
          
        # Create the schedule to use for get_eligables
        self.dt = datetime.datetime(2017, 2, 14, 12, 0)
        self.schedule_length = datetime.timedelta(0, 3600) # 3600 sec = 1 Hour
        self.start = self.dt - self.schedule_length
        self.end = self.dt + self.schedule_length
        self.schedule = create_schedule(self.session, self.start, self.end, 
                                        self.dep1.name)
    
        self.eligable_model = EligableModel(self.session, self.schedule.id, 
                                            self.dep1.name, DayModelDummy)
        
        # Create employees
        for i in range(0, 4):
            employee = create_employee(self.session, i, self.EMPLOYEE_NAMES[i], 
                                       self.EMPLOYEE_NAMES[i], self.dep1.name)
            self.employees.append(employee)
        for i in range(4, 8):
            employee = create_employee(self.session, i, self.EMPLOYEE_NAMES[i], 
                                       self.EMPLOYEE_NAMES[i], self.dep2.name, 
                                       self.dep1.name)
            self.employees.append(employee)
        employee = create_employee(self.session, 8, 'I', 'I', 'Driver')  
        self.employees.append(employee)

        # Create unavailable repeat conflicts
        start_time = datetime.time(12, 0)
        end_time = datetime.time(16, 0)
        unavailable1 = create_unavailable(self.session, start_time, end_time, 
                                          1, self.employees[1].employee_id)                           
        unavailable2 = create_unavailable(self.session, start_time, end_time, 
                                          1, self.employees[5].employee_id)
                                          
        # Create vacation conflicts
        v_start = datetime.datetime(2017, 2, 14, 0, 0, 0)
        v_end = datetime.datetime(2017, 2, 14, 23, 59, 59)
        vacation1 = create_vacation(self.session, v_start, v_end, 
                                    self.employees[2].employee_id)
        vacation2 = create_vacation(self.session, v_start, v_end, 
                                    self.employees[6].employee_id)
                                    
        # Create schedule conflicts
        t_delta = datetime.timedelta(0, 900) # 15 minutes
        overlap_sch1 = get_overlapping_schedule(self.session,
                                                self.schedule, 
                                                t_delta, 'START')
        overlap_sch2 = get_overlapping_schedule(self.session,
                                                self.schedule, 
                                                t_delta, 'START')
        assign_schedule(self.session, self.employees[3], overlap_sch1)
        assign_schedule(self.session, self.employees[7], overlap_sch2)
                                    
        
    def testGetEligables(self):
        """get_eligables creates 2 list, for the model and the view.
        
        Assert that e_listbox_list is correct, this represents a sorted list
        of strings that represents the view the user sees of the eligible 
        employees for this schedule.
        
        Assert that eligable_model.eligable_id_list is correct, this represents
        a sorted order reference to the database employee entries by their
        employee_id field.
        """
        
        expected_lb_list = [u'A', u'E', u'(U) B', u'(U) F', u'(V) C', u'(V) G', u'(S) D', u'(S) H']
        eligable_list = self.eligable_model.get_eligables()
        self.assertEqual(expected_lb_list, eligable_list, 
                         msg='Eligable listbox list not correct.')
        
        expected_id_list = [0, 4, 1, 5, 2, 6, 3, 7]
        eligable_id_list = self.eligable_model.eligable_id_list
        self.assertEqual(expected_id_list, eligable_id_list, 
                         msg='Eligable id list is not correct.')
     
    def tearDown(self):
        """Remove everything from the database."""
        employees = self.session.query(orm.Employees).all()
        for e in employees:
            self.session.delete(e)
        
        departments = self.session.query(orm.Department).all()
        for d in departments:
            self.session.delete(d)

        schedules = self.session.query(orm.DB_Schedule)
        for s in schedules:
            self.session.delete(s)
            
        vacations = self.session.query(orm.Unavailable_Schedule)
        for v in vacations:
            self.session.delete(v)
            
        unavailable_repeats = self.session.query(orm.UnavailableTime)
        for u_re in unavailable_repeats:
            self.session.delete(u_re)
        
        self.session.commit()


        
if __name__ == '__main__':
    unittest.main()