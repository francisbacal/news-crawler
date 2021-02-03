import datetime
from ..exceptions import helperError
from dateutil.parser import parse


class DateChecker:
    """
    Class for date checking
    """
    def __init__(self):
        self.today = datetime.datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
        self.weekends = [4, 5, 6]
    
    def is_today(self, input_date: type(datetime.datetime)) -> bool:
        """
        Checks input datetime date if is today
        """

        if not isinstance(input_date, datetime.datetime):
            try:
                input_date = parse(input_date)
            except:
                raise helperError("Invalid input type. datetime.datetime obj expected")
        

        if self.today.date() != input_date.date():
            return False
        
        else:
            return True

    def less_week(self, input_date: type(datetime.datetime), number_of_weeks: int=2):
        """
        Checks if input date is less than number_of_weeks
        """
        if not isinstance(input_date, datetime.datetime):
            try:
                input_date = parse(input_date)
            except:
                raise helperError("Invalid input type. datetime.datetime obj expected")

        
        n_weeks = self.today - datetime.timedelta(number_of_weeks * 7)

        if input_date.date() > n_weeks.date():
            return False
        else:
            return True

    def is_weekend(self, input_date: type(datetime.datetime)) -> bool:
        """
        Check input date if falls on a weekend [ Friday, Saturday, Sunday ]
        """

        if not isinstance(input_date, datetime.datetime):
            try:
                input_date = parse(input_date)
            except:
                raise helperError("Invalid input type. datetime.datetime obj expected")

        if input_date.weekday() in self.weekends:
            return True
        else:
            return False