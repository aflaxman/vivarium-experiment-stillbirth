import pandas as pd


class NeonatalIntervention:

    configuration_defaults = {
        'neonatal_intervention': {
            'proportion': 1.0
        }
    }

    def __init__(self):
        self.name = 'neonatal_intervention'

    def setup(self, builder):
        self.config = builder.configuration['neonatal_intervention']
        if self.config.proportion < 0 or self.config.proportion > 1:
            raise ValueError(f'The proportion for neonatal intervention must be between 0 and 1.'
                             f'You specified {self.config.proportion}.')

        self.randomness = builder.randomness.get_stream('neonatal_intervention_enrollment')

        columns_created = ['neonatal_treatment_status']
        self.population_view = builder.population.get_view(columns_created)
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=columns_created)

    def on_initialize_simulants(self, pop_data):
        pop = pd.DataFrame({'neonatal_treatment_status': 'not_treated'}, index=pop_data.index)
        treatment_probability = self.config.proportion
        treated = self.randomness.filter_for_probability(pop.index, treatment_probability)
        pop.loc[treated, 'neonatal_treatment_status'] = 'treated'

        self.population_view.update(pop)
