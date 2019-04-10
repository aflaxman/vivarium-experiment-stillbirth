import numpy as np
import pandas as pd
import pytest

from neonatal.components import LBWSGRisk

CATS = pd.DataFrame({'cat': ['cat1', 'cat100', 'cat12', 'cat57', 'cat28', 'cat52', 'cat2'],
                     'bw_left': [5, 1, 10, 20, 25, 30, 26],
                     'bw_right': [10, 5, 20, 25, 26, 31, 30],
                     'gt_left': [24, 32, 30, 37, 40, 48, 42],
                     'gt_right': [30, 37, 32, 40, 42, 48, 48]})

intervals_by_category = pd.DataFrame(
    {'birth_weight': [pd.Interval(x['bw_left'], x['bw_right'], closed='left') for _, x in CATS.iterrows()],
     'gestation_time': [pd.Interval(x['gt_left'], x['gt_right'], closed='left') for _, x in CATS.iterrows()]},
    index=CATS.cat)


@pytest.mark.parametrize('size', [10, 100, 1000])
def test_convert_category_intervals_to_values(size):
    idx = list(range(size))
    np.random.shuffle(idx)

    sim_data = CATS.sample(size, replace=True)
    sim_data['bw_draw'] = np.random.uniform(low=0, high=1, size=(size,))
    sim_data['gt_draw'] = np.random.uniform(low=0, high=1, size=(size,))
    sim_data.index = idx

    draws = {'birth_weight': sim_data.bw_draw, 'gestation_time': sim_data.gt_draw}

    converted_values = LBWSGRisk.convert_category_intervals_to_values(sim_data.cat, draws, intervals_by_category)

    sim_data['birth_weight'] = sim_data.bw_left + (sim_data.bw_right - sim_data.bw_left) * sim_data.bw_draw
    sim_data['gestation_time'] = sim_data.gt_left + (sim_data.gt_right - sim_data.gt_left) * sim_data.gt_draw

    assert np.all(converted_values.index == sim_data.index)
    assert list(converted_values.columns) == ['birth_weight', 'gestation_time']
    assert np.allclose(converted_values['birth_weight'], sim_data['birth_weight'])
    assert np.allclose(converted_values['gestation_time'], sim_data['gestation_time'])