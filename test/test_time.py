import pytest

import datetime
from api.time_management import get_time_index, OutOfHoursError, OutOfAcceptingHoursError

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

def test_time_index_ooh(client):
    with client.application.app_context():
        start = client.application.config['START_DATETIME']
        end = client.application.config['END_DATETIME']
        res = datetime.timedelta.resolution
        with pytest.raises(OutOfHoursError):
            get_time_index(mod_time(start, -res))
        with pytest.raises(OutOfHoursError):
            get_time_index(mod_time(end, +res))

def test_time_index_ooa(client):
    with client.application.app_context():
        timepoints = client.application.config['TIMEPOINTS']
        for i, point in enumerate(timepoints):
            res = datetime.timedelta.resolution
            with pytest.raises(OutOfAcceptingHoursError):
                get_time_index(mod_time(point[0], -res))
            with pytest.raises(OutOfAcceptingHoursError):
                get_time_index(mod_time(point[1], +res))

def test_time_index_lim(client):
    with client.application.app_context():
        timepoints = client.application.config['TIMEPOINTS']
        for i, point in enumerate(timepoints):
            res = datetime.timedelta.resolution
            idx_l = get_time_index(mod_time(point[0], +res))
            assert i == idx_l
            idx_r = get_time_index(mod_time(point[1], -res))
            assert i == idx_r

def test_time_index_same(client):
    with client.application.app_context():
        timepoints = client.application.config['TIMEPOINTS']
        for i, point in enumerate(timepoints):
            idx_l = get_time_index(point[0])
            assert i == idx_l
            idx_r = get_time_index(point[1])
            assert i == idx_r

