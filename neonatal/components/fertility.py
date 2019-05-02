"""Adapted from vivarium_public_health.population.add_new_birth_cohort.py"""
import pandas as pd
import numpy as np
from vivarium_public_health.population.data_transformations import get_live_births_per_year
#def get_still_births_per_year():  # TODO: get real data into appropriate place
#    return 0

SECONDS_PER_YEAR = 365.25*24*60*60


class FertilityWStillbirthDeterministic:
    """Deterministic model of births that include stillbirths."""

    configuration_defaults = {
        'fertility': {
            'number_of_live_births_each_year': 1000,
            'number_of_stillbirths_each_year': 10,
        },
    }

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
                                      'alive': vital_status,  # store this in the user_data dictionary for use in the on_initialize_simulants method
                                      'sim_state': 'time_step',
                                  })

