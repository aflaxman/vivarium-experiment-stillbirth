import pandas as pd

from gbd_mapping import risk_factors
from vivarium_public_health.utilities import EntityString


class NeonatalPretermDataLoader:

    def __init__(self):
        self.name = 'neonatal_preterm_data_loader'
        self.cause = EntityString('cause.neonatal_preterm_birth')
        self.risk = EntityString('risk_factor.low_birth_weight_and_short_gestation')

    def setup(self, builder):
        builder.data.load(f'cause.{self.cause.name}.cause_specific_mortality')
        builder.data.load(f'{self.cause}.excess_mortality')

        builder.data.load(f'{self.cause}.disability_weight')
        builder.data.load(f'{self.risk}.distribution')


class LBWSGRisk:

    def __init__(self):
        self.name = 'low_birth_weight_and_short_gestation'
        self.lbwsg_categories = self.parse_lbwsg_categories()

    def setup(self, builder):
        self.randomness = builder.randomness.get_stream(f'lbwsg')

        self.exposure_parameters = builder.lookup.build_table(
            builder.data.load('risk_factor.low_birth_weight_and_short_gestation.exposure'))

        self._bw_and_gt = pd.DataFrame(columns=['birth_weight', 'gestation_time'])

        self.exposure = builder.value.register_value_producer(
            'low_birth_weight_and_short_gestation.exposure',
            source=self.get_current_exposure,
            preferred_post_processer=self.get_lbwsg_post_processor()
        )

        builder.population.initializes_simulants(self.on_initialize_simulants)

    def get_current_exposure(self, index):
        return self._bw_and_gt.iloc[index]

    def get_lbwsg_post_processor(self):


    def on_initialize_simulants(self, pop_data):
        # assign each sim a lbwsg category
        category_draw = self.randomness.get_draw(pop_data.index)
        exposure = self.exposure_parameters(pop_data.index)[self.lbwsg_categories.values]
        exposure_sum = exposure.cumsum(axis='columns')
        category_index = (exposure_sum.T < category_draw).T.sum('columns')
        simulant_categories = pd.Series(self.lbwsg_categories.categories.values[category_index], index=pop_data.index)

        # assign each sim a birth weight and gestation time within their category
        bw_draw = self.randomness.get_draw(pop_data.index)
        gt_draw = self.randomness.get_draw(pop_data.index)




    def parse_lbwsg_categories(self):
        risk = risk_factors.low_birth_weight_and_short_gestation

        cats = (pd.DataFrame.from_dict(risk.categories.to_dict(), orient='index')
                .reset_index()
                .rename(columns={'index': 'cat', 0: 'name'}))

        def get_intervals_from_name(name):
            numbers_only = name.replace('Birth prevalence - [', '') \
                .replace(',', '') \
                .replace(') wks [', ' ') \
                .replace(') g', '')
            numbers_only = [int(n) for n in numbers_only.split()]
            return (pd.Interval(numbers_only[0], numbers_only[1], closed='left'),
                    pd.Interval(numbers_only[2], numbers_only[3], closed='left'))

        idx = pd.MultiIndex.from_tuples(cats.name.apply(get_intervals_from_name),
                                        names=['birth_weight', 'gestation_time'])

        cats = cats['cat']
        cats.index = idx
        return cats

