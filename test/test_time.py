import datetime
from api.time_management import get_time_index, OutOfHoursError

def test_time_index_lim(client):
    with client.application.app_context():
        def mod_time(t, dt):
            datet = datetime.datetime.combine(datetime.date(2000, 1, 1), t)
            return (datet + dt).time()
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

