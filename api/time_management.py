from flask import current_app
import datetime


class OutOfHoursError(Exception):
    """
        The Exception that indicates the time was out of festival
    """
    pass


def get_time_index(time):
    """
        Get the lottery index from the time
        Args:
          time(datetime.time|datetime.datetime): The Time
        Return:
          i(int): The lottery index
    """
    if isinstance(time, datetime.datetime):
        start = current_app.config['START_DATETIME']
        end = current_app.config['END_DATETIME']
        if not (start < time < end):
            raise OutOfHourError()
        # extract datetime.time instance from datetime.datetime
        time = time.time()

    for i, (st, en) in enumerate(current_app.config['TIMEPOINTS']):
        if st < time < en:
            return i
