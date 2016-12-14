"""
Test cases:

Exhaustively enumerate cases for:
-get_availability
-get_eligables


What should get_availability do:


Args: datetime.date, employee, eligability='E'


For day X, employee A and eligability Y assign 


assign the 3 different 
schedules for that day, then assign 4 work-schedules, 3 with some kind of
overlap with the 3 unavailables and 1 with no overlap. Assert the availability
respectively for each day

Then repeat the month, but with schedules assigned to get overtime results

Edge cases:
    


What should get_eligables do:

The test should iterate through some month's days, and for each day consider
an ordering of the employees. Then assert that the returned sorted 


"""

import unittest

def fun(x):
    return x + 1

class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(fun(3), 4)
        
class GetAvailabilityTest(unittest.TestCase):

    def __init__(self):
        pass
        
        
    def no_conflict(self):
        pass
        
    def schedule_conflict(self):
        pass
        
        
        
if __name__ == '__main__':
    unittest.main()