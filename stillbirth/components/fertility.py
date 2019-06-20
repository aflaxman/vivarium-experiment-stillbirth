"""Adapted from vivarium_public_health.population.add_new_birth_cohort.py"""
import pandas as pd
import numpy as np
from vivarium_public_health.population.data_transformations import get_live_births_per_year
def get_still_births_per_year(builder):  # TODO: get real data into appropriate place
    return .1*get_live_births_per_year(builder)

SECONDS_PER_YEAR = 365.25*24*60*60


class FertilityWStillbirthDeterministic:
    """Deterministic model of births that include stillbirths."""

    configuration_defaults = {
        'fertility': {
            'number_of_live_births_each_year': 1000,
            'number_of_stillbirths_each_year': 10,
        },
    }

    @property
    def name(self):
        return "deterministic_fertility_w_stillbirth"

    def setup(self, builder):
        self.live_births_per_year = builder.configuration.fertility.number_of_live_births_each_year
        self.stillbirths_per_year = builder.configuration.fertility.number_of_stillbirths_each_year

        # initialize counters for getting integers to add up to a specified total
        self.fractional_live_births = 0
        self.fractional_stillbirths = 0

        self.simulant_creator = builder.population.get_simulant_creator()

        self.population_view = builder.population.get_view(['alive'])
        builder.population.initializes_simulants(self.on_initialize_simulants)

        builder.event.register_listener('time_step', self.on_time_step)


    def on_initialize_simulants(self, pop_data):
        if 'alive' in pop_data.user_data:
            pop = pd.DataFrame(index=pop_data.index)
            pop['alive'] = pop_data.user_data['alive']
            self.population_view.update(pop)


    def on_time_step(self, event):
        """Adds a set number of simulants to the population each time step.

        Parameters
        ----------
        event
            The event that triggered the function call.
        """
        # Assume births are uniformly distributed throughout the year.
        step_size = event.step_size/pd.Timedelta(seconds=SECONDS_PER_YEAR)
        live_births = self.live_births_per_year*step_size + self.fractional_live_births
        stillbirths = self.stillbirths_per_year*step_size + self.fractional_stillbirths

        live_births, self.fractional_live_births = int(live_births), live_births % 1
        stillbirths, self.fractional_stillbirths = int(stillbirths), stillbirths % 1

        simulants_to_add = live_births + stillbirths
        if simulants_to_add > 0:
            vital_status = ['alive'] * live_births + ['stillborn'] * stillbirths

            self.simulant_creator(simulants_to_add,
                                  population_configuration={
                                      'age_start': 0,
                                      'age_end': 0,
                                      'alive': vital_status,  # store this in the user_data dictionary
                                                              # for use in the on_initialize_simulants method
                                      'sim_state': 'time_step',
                                  })

class FertilityWStillbirthCrudeBirthRate:
    """Population-level model of births that include stillbirths.

    The number of births added each time step is calculated as
    
    new_births = sim_pop_size_t0 * live_births / true_pop_size * step_size
    
    Where
    
    sim_pop_size_t0 = the initial simulation population size
    live_births = annual number of live births in the true population
    true_pop_size = the true population size
    
    This component has configuration flags that determine whether the
    live births and the true population size should vary with time.

    """

    configuration_defaults = {
        'fertility': {
            'time_dependent_live_births': True,
            'time_dependent_population_fraction': False,
        },
    }

    @property
    def name(self):
        return "crude_birth_rate_fertility_w_stillbirth"

    def setup(self, builder):
        self.clock = builder.time.clock()

        self.live_birth_rate = get_live_births_per_year(builder)
        self.still_birth_rate = get_still_births_per_year(builder)

        self.randomness = builder.randomness.get_stream('crude_birth_rate')

        self.simulant_creator = builder.population.get_simulant_creator()

        self.population_view = builder.population.get_view(['alive'])
        builder.population.initializes_simulants(self.on_initialize_simulants)

        builder.event.register_listener('time_step', self.on_time_step)


    def on_time_step(self, event):
        """Adds new simulants every time step based on the Crude Birth Rate
        and an assumption that birth is a Poisson process

        Parameters
        ----------
        event
            The event that triggered the function call.
        """
        live_birth_rate = self.live_birth_rate.at[self.clock().year]
        still_birth_rate = self.still_birth_rate.at[self.clock().year]

        step_size = event.step_size / pd.Timedelta(seconds=SECONDS_PER_YEAR)

        mean_births = (live_birth_rate + still_birth_rate) * step_size
        # Assume births occur as a Poisson process
        r = np.random.RandomState(seed=self.randomness.get_seed())  # does this always seed the PRNG with the same seed?
        live_births = r.poisson(live_birth_rate * step_size)
        stillbirths = r.poisson(still_birth_rate * step_size)
        print(live_births, stillbirths)
        simulants_to_add = live_births + stillbirths
        if simulants_to_add > 0:
            vital_status = ['alive'] * live_births + ['stillborn'] * stillbirths

            self.simulant_creator(simulants_to_add,
                                  population_configuration={
                                      'age_start': 0,
                                      'age_end': 0,
                                      'alive': vital_status,  # store this in the user_data dictionary
                                                              # for use in the on_initialize_simulants method
                                      'sim_state': 'time_step',
                                  })


    def on_initialize_simulants(self, pop_data):
        if 'alive' in pop_data.user_data:
            pop = pd.DataFrame(index=pop_data.index)
            pop['alive'] = pop_data.user_data['alive']
            self.population_view.update(pop)


