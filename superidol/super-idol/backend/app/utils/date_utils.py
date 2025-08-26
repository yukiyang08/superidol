"""
Date utility functions.
"""

import datetime

def get_week_dates(week=None, year=None):
    """
    Get the start and end dates for a specific week.
    
    Args:
        week (int, optional): Week number. Defaults to current week.
        year (int, optional): Year. Defaults to current year.
        
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    if week is None or year is None:
        # Get the current week if not specified
        today = datetime.datetime.now()
        year = today.year if year is None else year
        week = today.isocalendar()[1] if week is None else week
        
    # The first day of the week (Monday)
    first_day = datetime.datetime.strptime(f'{year}-{week}-1', "%Y-%W-%w")
    
    # The last day of the week (Sunday)
    last_day = first_day + datetime.timedelta(days=6)
    
    return first_day, last_day

def format_date(date_obj):
    """
    Format a datetime object to YYYY-MM-DD.
    
    Args:
        date_obj (datetime): Date to format
        
    Returns:
        str: Formatted date
    """
    return date_obj.strftime('%Y-%m-%d')

def parse_date(date_str):
    """
    Parse a date string in YYYY-MM-DD format.
    
    Args:
        date_str (str): Date string
        
    Returns:
        datetime: Parsed date
    """
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')

def get_today():
    """
    Get today's date.
    
    Returns:
        str: Today's date in YYYY-MM-DD format
    """
    return format_date(datetime.datetime.now()) 