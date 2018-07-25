from flask import current_app
import datetime


class OutOfHourError(Exception):
    pass


def get_time_index(time):
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
