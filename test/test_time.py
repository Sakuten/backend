import pytest

import datetime
from api.time_management import (
    mod_time,
    get_draw_time_index,
    get_time_index,
    get_prev_time_index,
    OutOfHoursError,
    OutOfAcceptingHoursError
)


def test_draw_time_index_ooh(client):
    with client.application.app_context():
        start = client.application.config['START_DATETIME']
        end = client.application.config['END_DATETIME']
        res = datetime.timedelta.resolution
        with pytest.raises(OutOfHoursError):
            get_draw_time_index(mod_time(start, -res))
        with pytest.raises(OutOfHoursError):
            get_draw_time_index(mod_time(end, +res))


def test_draw_time_index_ooa(client):
    with client.application.app_context():
        timepoints = client.application.config['TIMEPOINTS']
        ext = client.application.config['DRAWING_TIME_EXTENSION']
        for i, (_, en) in enumerate(timepoints):
            res = datetime.timedelta.resolution
            with pytest.raises(OutOfAcceptingHoursError):
                get_draw_time_index(mod_time(en, -res))
            with pytest.raises(OutOfAcceptingHoursError):
                get_draw_time_index(mod_time(en, +ext+res))


def test_draw_time_index_lim(client):
    with client.application.app_context():
        timepoints = client.application.config['TIMEPOINTS']
        ext = client.application.config['DRAWING_TIME_EXTENSION']
        en_margin = client.application.config['TIMEPOINT_END_MARGIN']
        for i, (_, en) in enumerate(timepoints):
            en_with_margin = mod_time(en, en_margin)
            res = datetime.timedelta.resolution
            idx_l = get_draw_time_index(mod_time(en_with_margin, +res))
            assert i == idx_l
            idx_r = get_draw_time_index(mod_time(en, +ext-res))
            assert i == idx_r


def test_draw_time_index_same(client):
    with client.application.app_context():
        timepoints = client.application.config['TIMEPOINTS']
        ext = client.application.config['DRAWING_TIME_EXTENSION']
        en_margin = client.application.config['TIMEPOINT_END_MARGIN']
        for i, (_, en) in enumerate(timepoints):
            idx_l = get_draw_time_index(mod_time(en, en_margin))
            assert i == idx_l
            idx_r = get_draw_time_index(mod_time(en, +ext))
            assert i == idx_r


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
        res = datetime.timedelta.resolution
        en_margin = client.application.config['TIMEPOINT_END_MARGIN']
        for i, point in enumerate(timepoints):
            with pytest.raises(OutOfAcceptingHoursError):
                get_time_index(mod_time(point[0], -res))
            with pytest.raises(OutOfAcceptingHoursError):
                get_time_index(mod_time(point[1], +res+en_margin))


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


def test_prev_time_index_ooa(client):
    with client.application.app_context():
        start_of_first_index = client.application.config['TIMEPOINTS'][0][0]
        end_of_last_index = client.application.config['TIMEPOINTS'][-1][1]
        en_margin = client.application.config['TIMEPOINT_END_MARGIN']
        res = mod_time(datetime.timedelta.resolution, en_margin)
        with pytest.raises(OutOfAcceptingHoursError):
            get_prev_time_index(mod_time(start_of_first_index, res))
        with pytest.raises(OutOfAcceptingHoursError):
            get_prev_time_index(mod_time(end_of_last_index, res))
