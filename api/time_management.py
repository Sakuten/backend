from flask import current_app
import datetime


class OutOfHoursError(Exception):
    """
        The Exception that indicates the time was out of festival
    """
    pass


class OutOfAcceptingHoursError(Exception):
    """
        The Exception that indicates the time is in festival,
        but not in accepting time
    """
    pass


def get_current_datetime():
    """
        Get the current datetime.
        Note: This function is intended to be mocked in testing
        Return:
          time(datetime.datetime): current datetime
    """
    return datetime.datetime.now()


def get_time_index(time=None):
    """
        Get the lottery index from the time
        Args:
          time(datetime.time|datetime.datetime): The Time
        Return:
          i(int): The lottery index
        Raises:
          OutOfHoursError, OutOfAcceptingHoursError
    """
    if time is None:
        time = get_current_datetime()

    if isinstance(time, datetime.datetime):
        start = current_app.config['START_DATETIME']
        end = current_app.config['END_DATETIME']
        if not (start <= time <= end):
            raise OutOfHoursError()
        # extract datetime.time instance from datetime.datetime
        time = time.time()

    for i, (st, en) in enumerate(current_app.config['TIMEPOINTS']):
        if st <= time <= en:
            return i

    raise OutOfAcceptingHoursError()
