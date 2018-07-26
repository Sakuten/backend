from flask import current_app
import datetime


def mod_time(t, dt):
    """
        Modify the supplied time with timedelta
        Args:
            t(datetime.time|datetime.datetime): The Time to modify
            dt(datetime.timedelta): Difference
        Returns:
            time(datetime.time|datetime.datetime): The modified time
    """
    if isinstance(t, datetime.time):
        t = datetime.datetime.combine(datetime.date(2000, 1, 1), t)
        return (t + dt).time()
    else:
        return t + dt


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
        get the lottery index from the drawing time
        args:
          time(datetime.time|datetime.datetime): the time
        return:
          i(int): the lottery index
        raises:
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
        if en <= time <= mod_time(en, current_app.config['DRAWING_TIME_EXTENSION']):
            return i

    raise OutOfAcceptingHoursError()


def get_draw_time_index(time=None):
    """
        get the lottery index from the time
        args:
          time(datetime.time|datetime.datetime): the time
        return:
          i(int): the lottery index
        raises:
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
