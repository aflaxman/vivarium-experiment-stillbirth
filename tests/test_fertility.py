import pytest
import numpy as np
import pandas as pd

from vivarium.testing_utilities import TestPopulation, metadata, build_table
from vivarium.interface.interactive import setup_simulation, initialize_simulation

from neonatal.components.fertility import FertilityWStillbirthDeterministic


@pytest.fixture()
def config(base_config):
    base_config.update({
        'population': {
            'population_size': 10000,
            'age_start': 0,
            'age_end': 125,
        },
        'time': {
            'step_size': 10,
            }
        }, **metadata(__file__))
    return base_config


def test_FertilityWStillbirthDeterministic(config):
    pop_size = config.population.population_size
    annual_live_births = 1000
    annual_stillbirths = 10
    step_size = config.time.step_size
    num_days = 100

    config.update({
        'fertility': {
            'number_of_live_births_each_year': annual_live_births,
            'number_of_stillbirths_each_year': annual_stillbirths,
        }
    }, **metadata(__file__))

    components = [TestPopulation(), FertilityWStillbirthDeterministic()]
    simulation = setup_simulation(components, config)
    num_steps = simulation.run_for(duration=pd.Timedelta(days=num_days))
    pop = simulation.get_population()

    assert num_steps == num_days // step_size

    # imprecise tests
    assert not np.all(pop.alive == 'alive')
    assert np.any(pop.alive == 'stillborn')

    # more precise tests
    assert int(num_days * annual_live_births / 365) == sum(pop.alive != 'stillborn') - pop_size
    assert int(num_days * annual_stillbirths / 365) == sum(pop.alive == 'stillborn')

