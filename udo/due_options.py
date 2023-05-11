from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

due_options = {
        None: None,
        "now": "today",
        "day": "today",
        "week": "week",
        "wk": "week",
        "month": "month",
        "mn": "month",
        "year": "year",
        "today": "today",
        "td": "today",
        "tomorrow": "tomorrow",
        "tm": "tomorrow",
        "Monday": "mon",
        "Tuesday": "tue",
        "Wednesday": "wed",
        "Thursday": "thu",
        "Friday": "fri",
        "Saturday": "sat",
        "Sunday": "sun",        
        "monday": "mon",
        "tuesday": "tue",
        "wednesday": "wed",
        "thursday": "thu",
        "friday": "fri",
        "saturday": "sat",
        "sunday": "sun", 
        "mon": "mon",
        "tue": "tue",
        "wed": "wed",
        "thu": "thu",
        "fri": "fri",
        "sat": "sat",
        "sun": "sun",
        "January": "jan",
        "February": "feb",
        "March": "mar",
        "April": "apr",
        "May": "may",
        "Jun": "jun",
        "July": "jul",
        "August": "aug",
        "September": "sep",
        "October": "oct",
        "November": "nov",
        "December": "dec",
        "january": "jan",
        "february": "feb",
        "march": "mar",
        "april": "apr",
        "may": "may",
        "jun": "jun",
        "july": "jul",
        "august": "aug",
        "september": "sep",
        "october": "oct",
        "november": "nov",
        "december": "dec",
        "jan": "jan",
        "feb": "feb",
        "mar": "mar",
        "apr": "apr",
        "may": "may",
        "jun": "jun",
        "jul": "jul",
        "aug": "aug",
        "sep": "sep",
        "oct": "oct",
        "nov": "nov",
        "dec": "dec",
        "2023": "2023",
        "2024": "2024",
        "2025": "2025",
        "2026": "2026",
        "2027": "2027",
        "2028": "2028",
        "2029": "2029",
        "2030": "2030",
        "2031": "2031",
        "2032": "2032",
        "2033": "2033",
        "2034": "2034",
        "2035": "2035",
        "2036": "2036",
        "2037": "2037",
        "2038": "2038",
        "2039": "2039",
        "2040": "2040",
        "01": "01",
        "02": "02",
        "03": "03",
        "04": "04",
        "05": "05",
        "06": "06",
        "07": "07",
        "08": "08",
        "09": "09",
        "10": "10",
        "11": "11",
        "12": "12",
        "13": "13",
        "14": "14",
        "15": "15",
        "16": "16",
        "17": "17",
        "18": "18",
        "19": "19",
        "20": "20",
        "21": "21",
        "22": "22",
        "23": "23",
        "24": "24",
        "25": "25",
        "26": "26",
        "27": "27",
        "28": "28",
        "29": "29",
        "30": "30",
        "31": "31"
}

map_options = {
    "today": "today",
    "tomorrow": "tomorrow",
    "mon": "day",
    "tue": "day",
    "wed": "day",
    "thu": "day",
    "fri": "day",
    "sat": "day",
    "sun": "day",
    "week": "this_week",
    "month": "this_month",
    "jan": "month",
    "feb": "month",
    "mar": "month",
    "apr": "month",
    "may": "month",
    "jun": "month",
    "jul": "month",
    "aug": "month",
    "sep": "month",
    "oct": "month",
    "nov": "month",
    "dec": "month",
    "year": "this_year",
    "2023": "year",
    "2024": "year",
    "2025": "year",
    "2026": "year",
    "2027": "year",
    "2028": "year",
    "2029": "year",
    "2030": "year",
    "2031": "year",
    "2032": "year",
    "2033": "year",
    "2034": "year",
    "2035": "year",
    "2036": "year",
    "2037": "year",
    "2038": "year",
    "2039": "year",
    "2040": "year",
    "01": "date",
    "02": "date",
    "03": "date",
    "04": "date",
    "05": "date",
    "06": "date",
    "07": "date",
    "08": "date",
    "09": "date",
    "10": "date",
    "11": "date",
    "12": "date",
    "13": "date",
    "14": "date",
    "15": "date",
    "16": "date",
    "17": "date",
    "18": "date",
    "19": "date",
    "20": "date",
    "21": "date",
    "22": "date",
    "23": "date",
    "24": "date",
    "25": "date",
    "26": "date",
    "27": "date",
    "28": "date",
    "29": "date",
    "30": "date",
    "31": "date"
}

def map_weekday(weekday: str) -> int:
    table = {
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
    "sun": 7
    }
    return table[weekday]

def map_month(month: str) -> int:
    table = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12
    }
    return table[month]

def sort_due(due: str) -> datetime:
    """
    Maps a string representation of the due date to its
    analogue in datetime format according to developer defifined
    options. 
    """

    val = due_options[due]
    mapped = map_options[val]
    if mapped == "today":
        return ToDoDate().due_today()
    elif mapped == "tomorrow":
        return ToDoDate().due_tomorrow()
    elif mapped == "day":
        return ToDoDate().due_weekday(map_weekday(val))
    elif mapped == "this_week":
        return ToDoDate().due_weekday(7)
    elif mapped == "month":
        return ToDoDate().due_month(map_month(val))
    elif mapped == "date":
        return ToDoDate().due_date(int(val))
    elif mapped == "this_month":
        return ToDoDate().due_this_month()
    elif mapped == "year":
        return ToDoDate().due_year(int(val))
    elif mapped == "this_year":
        return ToDoDate().due_this_year()
    
    


class ToDoDate():
    date: int = None
    weekday: int = None
    month: int = None
    year: int = None
    def __init__(self, d: datetime = datetime.now()) -> None:
        self.date = int(d.strftime("%d"))
        self.weekday = int(d.strftime("%w"))
        self.month = int(d.strftime("%m"))
        self.year = int(d.strftime("%y"))

    def get_to_day(self):
        return datetime(self.year, self.month, self.date)
    
    def get_to_month(self):
        return datetime(self.year, self.month, 1)

    def due(self, delta: timedelta, day=False, month=False):
        base = datetime(
            2000 + self.year,
            self.month,
            self.date
        )
        if day:
            base = base.replace(day=1)
        if month:
            base = base.replace(month=1)

        return base + delta - timedelta(seconds=1)

    def due_today(self) -> datetime:
        return self.due(timedelta(days=1))

    def due_tomorrow(self) -> datetime:
        return self.due(timedelta(days=2))

    def due_weekday(self, weekday: int):
        if weekday > self.weekday:
            diff = weekday - self.weekday + 1
        else: 
            diff = 7 - (self.weekday - weekday) + 1
        return self.due(timedelta(days=diff))
    
    def due_date(self, date: int) -> datetime:
        if date >= self.date:
            diff = date - self.date + 1
            return self.due(timedelta(days=diff))
        else:
            new_obj = ToDoDate(self.due_this_month())
            return new_obj.due_date(date+1)         

    def due_month(self, month: int):
        if month >= self.month:
            diff = month - self.month + 1
        else: 
            diff = 12 - (self.month - month) + 1
        return self.due(
            relativedelta(months=diff),
            day=True
        )

    def due_this_month(self):
        return self.due_month(month=self.month)

    def due_year(self, year: int):
        diff = year - self.year + 1
        return self.due(
            relativedelta(months=diff),
            day=True,
            month=True
        )

    def due_this_year(self):
        return self.due_year(self.year)


        

