# Weekday Module for meshbot
# Provides detailed information about a given date including day of week, day of year, weeks remaining, etc.
# Based on ideas from https://github.com/coding-horror/basic-computer-games/blob/main/95_Weekday/python/weekday.py

import datetime
import calendar
from modules.log import logger

trap_list_weekday = ("weekday", )
help_text_weekday = "weekday - Get info about today or a date: weekday or weekday MM,DD,YYYY"


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    if (year % 4) != 0:
        return False
    return True if (year % 100) != 0 else year % 400 == 0

def get_day_of_week_name(date_obj: datetime.date) -> str:
    """Get the day of week name for a given date."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[date_obj.weekday()]


def get_week_number(date_obj: datetime.date) -> int:
    """Get the ISO week number for a given date."""
    return date_obj.isocalendar()[1]


def is_friday_13th(date_obj: datetime.date) -> bool:
    """Check if the date is Friday the 13th."""
    return date_obj.day == 13 and date_obj.weekday() == 4  # 4 = Friday


def get_day_of_year(date_obj: datetime.date) -> int:
    """Get the day number within the year (1-366)."""
    return date_obj.timetuple().tm_yday


def get_days_left_in_year(date_obj: datetime.date) -> int:
    """Get the number of days remaining in the year after the given date."""
    end_of_year = datetime.date(date_obj.year, 12, 31)
    delta = end_of_year - date_obj
    return delta.days


def get_days_left_in_month(date_obj: datetime.date) -> int:
    """Get the number of days remaining in the month after the given date."""
    # Get the last day of the month
    last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
    end_of_month = datetime.date(date_obj.year, date_obj.month, last_day)
    delta = end_of_month - date_obj
    return delta.days


def is_even_week(date_obj: datetime.date) -> bool:
    """Check if the date falls on an even week number."""
    week_num = get_week_number(date_obj)
    return week_num % 2 == 0


def get_days_till_christmas(date_obj: datetime.date) -> tuple:
    """Calculate days until Christmas.
    
    Returns:
        A tuple of (days_until, christmas_date)
    """
    # Get Christmas of the current year
    christmas = datetime.date(date_obj.year, 12, 25)
    
    # If Christmas has already passed this year, use next year's Christmas
    if date_obj > christmas:
        christmas = datetime.date(date_obj.year + 1, 12, 25)
    
    delta = christmas - date_obj
    return delta.days, christmas


def get_days_ago(date_obj: datetime.date) -> tuple:
    """Calculate how many days and years ago a date was.
    
    Returns:
        A tuple of (days_ago, years_ago) or (0, 0) if date is in the future
    """
    today = datetime.date.today()
    
    if date_obj >= today:
        return 0, 0
    
    delta = today - date_obj
    days_ago = delta.days
    years_ago = days_ago // 365
    
    return days_ago, years_ago


def get_season(date_obj: datetime.date) -> str:
    """Get the season for a given date.
    
    Returns:
        A string with the season (Spring, Summer, Fall, Winter)
    """
    month = date_obj.month
    day = date_obj.day
    
    # Spring: March 20 - June 20
    # Summer: June 21 - September 22
    # Fall: September 23 - December 21
    # Winter: December 22 - March 19
    
    if (month == 3 and day >= 20) or (month in [4, 5]) or (month == 6 and day <= 20):
        return "🌸 Spring"
    elif (month == 6 and day >= 21) or (month in [7, 8]) or (month == 9 and day <= 22):
        return "☀️ Summer"
    elif (month == 9 and day >= 23) or (month in [10, 11]) or (month == 12 and day <= 21):
        return "🍂 Fall"
    else:
        return "❄️ Winter"


def get_business_days_left(date_obj: datetime.date) -> int:
    """Get the number of business days (Mon-Fri) remaining in the year.
    
    Returns:
        An integer of business days left
    """
    end_of_year = datetime.date(date_obj.year, 12, 31)
    business_days = 0
    
    current = date_obj + datetime.timedelta(days=1)  # Start from tomorrow
    while current <= end_of_year:
        if current.weekday() < 5:  # Monday=0, Friday=4
            business_days += 1
        current += datetime.timedelta(days=1)
    
    return business_days


def get_week_of_month(date_obj: datetime.date) -> int:
    """Get which week of the month the date falls on (1-5).
    
    Week 1: Days 1-7
    Week 2: Days 8-14
    etc.
    
    Returns:
        An integer representing the week of month (1-5)
    """
    return (date_obj.day - 1) // 7 + 1

def to_roman_numeral(num: int) -> str:
    """Convert an integer to Roman numerals.
    
    Returns:
        A string with the Roman numeral representation
    """
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    
    for i in range(len(val)):
        count = int(num / val[i])
        roman_num += syms[i] * count
        num -= val[i] * count
    
    return roman_num


def get_days_till_next_holiday(date_obj: datetime.date) -> str:
    """Get the countdown to the next major holiday.
    
    Returns:
        A string with holiday name and days until it
    """
    # holidays is a list of tuples: (holiday_name, month, day)
    holidays = [
        ("New Year's Day", 1, 1),
        ("St. Patrick's Day", 3, 17),
        ("Independence Day", 7, 4),
        ("Christmas", 12, 25),
    ]
    
    today = datetime.date.today()
    next_holiday = None
    min_days = float('inf')
    
    for holiday_name, month, day in holidays:
        if month is None:
            # Skip variable holidays like Easter for simplicity
            continue
        
        # Check this year
        holiday_date = datetime.date(date_obj.year, month, day)
        if holiday_date >= date_obj:
            days_until = (holiday_date - date_obj).days
            if days_until < min_days:
                min_days = days_until
                next_holiday = (holiday_name, days_until)
        
        # Check next year if we don't find one this year
        if next_holiday is None:
            holiday_date = datetime.date(date_obj.year + 1, month, day)
            days_until = (holiday_date - date_obj).days
            if days_until < min_days:
                min_days = days_until
                next_holiday = (holiday_name, days_until)
    
    if next_holiday:
        return f"{next_holiday[0]}: {next_holiday[1]} days"
    return "No holiday found"


def parse_date_input(date_str: str) -> datetime.date | None:
    """Parse a date string in MM,DD,YYYY format.
    
    Returns:
        A datetime.date object or None if parsing fails.
    """
    try:
        parts = date_str.strip().split(',')
        if len(parts) != 3:
            return None
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
        
        # Validate date
        if year < 1901:
            return None
        
        date_obj = datetime.date(year, month, day)
        return date_obj
    except (ValueError, TypeError):
        return None


def get_weekday_info(date_obj: datetime.date = None) -> str:
    """Get comprehensive weekday information for a given date.
    
    Args:
        date_obj: A datetime.date object. If None, uses today's date.
    
    Returns:
        A formatted string with weekday information.
    """
    if date_obj is None:
        date_obj = datetime.date.today()
    
    today = datetime.date.today()
    day_name = get_day_of_week_name(date_obj)
    day_of_year = get_day_of_year(date_obj)
    days_left = get_days_left_in_year(date_obj)
    days_left_month = get_days_left_in_month(date_obj)
    week_number = get_week_number(date_obj)
    is_even = is_even_week(date_obj)
    week_type = "even" if is_even else "odd"
    season = get_season(date_obj)
    leap = "Leap Year 🎯" if is_leap_year(date_obj.year) else ""
    business_days = get_business_days_left(date_obj)
    week_of_month = get_week_of_month(date_obj)
    
    # Build the response message
    msg = f"📅 {date_obj.strftime('%m/%d/%Y')} is a {day_name} of {calendar.month_name[date_obj.month]}"
    
    if is_friday_13th(date_obj):
        msg += " (FRIDAY THE 13TH - BEWARE! 😱)"
    msg += "\n"
    
    msg += f"🧮 Day {day_of_year}, of {date_obj.year}\n"
    msg += f"📊 Week #{week_number} ({week_type} week). Week {week_of_month} of month, in {season}\n"
    msg += f"⏳ {days_left} days remain in {date_obj.year} and {business_days} week days\n"
    msg += f"🗓️ {days_left_month} days left this month\n"
    
    if leap:
        msg += f"🎯 {leap}\n"
    
    msg += f"🎉 {get_days_till_next_holiday(date_obj)}\n"

    # Add past date info
    if date_obj < today:
        days_ago, years_ago = get_days_ago(date_obj)
        msg += f"⏰ That was {years_ago} years and {days_ago % 365} days ago"
    elif date_obj == today:
        pass
    else:
        days_future = (date_obj - today).days
        msg += f"⏰ That's {days_future} days from now"
    
    return msg


def weekdayHandler(message: str, message_from_id: int, deviceID: str) -> str:
    """Handle weekday command with optional date parameter.
    
    Usage:
        weekday           - Show info for today
        weekday MM,DD,YYYY - Show info for a specific date
    
    Args:
        message: The full message including the command
        message_from_id: The ID of the user
        deviceID: The device ID
    
    Returns:
        A formatted string with weekday information or an error message.
    """
    try:
        # Extract the date parameter if provided
        parts = message.split()
        date_obj = None
        
        if len(parts) > 1:
            # User provided a date
            date_str = " ".join(parts[1:])
            date_obj = parse_date_input(date_str)
            
            if date_obj is None:
                return "❌ Invalid date format. Use: weekday MM,DD,YYYY\nExample: weekday 03,24,1979"
        
        return get_weekday_info(date_obj)
    
    except Exception as e:
        logger.error(f"Error in weekdayHandler: {e}")
        return f"❌ Error processing weekday command: {str(e)}"
