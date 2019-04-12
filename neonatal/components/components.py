import pandas as pd

from vivarium_public_health.utilities import EntityString
from vivarium_public_health.risks.data_transformations import get_exposure_data
from vivarium_public_health.disease import RiskAttributableDisease


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

    configuration_defaults = {
        'low_birth_weight_and_short_gestation': {
            'exposure': 'data',
            'rebinned_exposed': []
        }
    }

    def __init__(self):
        self.risk = EntityString('risk_factor.low_birth_weight_and_short_gestation')

    def setup(self, builder):
        self.categories_by_interval = self.parse_lbwsg_categories(builder.data.load(f'{self.risk}.categories'))
        self.intervals_by_category = self.categories_by_interval.reset_index().set_index('cat')
        self.randomness = builder.randomness.get_stream(f'{self.risk.name}.exposure')

        self.exposure_parameters = builder.lookup.build_table(get_exposure_data(builder, self.risk))

        self._bw_and_gt = pd.DataFrame(columns=['birth_weight', 'gestation_time'])

        self.exposure = builder.value.register_value_producer(
            f'{self.risk.name}.exposure',
            source=self.get_current_exposure,
            preferred_post_processor=self.get_lbwsg_post_processor()
        )

        builder.population.initializes_simulants(self.on_initialize_simulants)

    def get_current_exposure(self, index):
        return self._bw_and_gt.loc[index]

    def get_lbwsg_post_processor(self):
        cats = self.categories_by_interval

        def post_processor(exposure, _):
            idx = exposure.index
            exposure_bw_gt_index = exposure.set_index(['gestation_time', 'birth_weight']).index
            categorical_exposure = cats.iloc[cats.index.get_indexer(exposure_bw_gt_index, method=None)]
            categorical_exposure.index = idx
            return categorical_exposure

        return post_processor

    def on_initialize_simulants(self, pop_data):
        # assign each sim a lbwsg category
        category_draw = self.randomness.get_draw(pop_data.index, additional_key='category')
        exposure = self.exposure_parameters(pop_data.index)[self.categories_by_interval.values]
        exposure_sum = exposure.cumsum(axis='columns')
        category_index = (exposure_sum.T < category_draw).T.sum('columns')
        simulant_categories = pd.Series(self.categories_by_interval.values[category_index],
                                        index=pop_data.index, name='cat')

        # assign each sim a birth weight and gestation time within their category
        draws = {'birth_weight': self.randomness.get_draw(pop_data.index, additional_key='birth_weight'),
                 'gestation_time': self.randomness.get_draw(pop_data.index, additional_key='gestation_time')}

        self._bw_and_gt = self._bw_and_gt.append(self.convert_category_intervals_to_values(simulant_categories,
                                                                         draws, self.intervals_by_category))

    @staticmethod
    def convert_category_intervals_to_values(simulant_categories, draws, intervals_by_category):
        def single_values_from_category(row):
            idx = row['index']
            bw_draw = draws['birth_weight'][idx]
            gt_draw = draws['gestation_time'][idx]
            intervals = intervals_by_category.loc[row['cat']]

            return (intervals.birth_weight.left + (intervals.birth_weight.right - intervals.birth_weight.left) * bw_draw,
                    intervals.gestation_time.left + (intervals.gestation_time.right - intervals.gestation_time.left) * gt_draw)

        values = simulant_categories.reset_index().apply(single_values_from_category, axis=1)
        return pd.DataFrame(list(values), index=simulant_categories.index, columns=['birth_weight', 'gestation_time'])

    @staticmethod
    def parse_lbwsg_categories(category_dict):
        cats = (pd.DataFrame.from_dict(category_dict, orient='index')
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
                                        names=['gestation_time', 'birth_weight'])

        cats = cats['cat']
        cats.index = idx
        return cats


class NeonatalPreterm(RiskAttributableDisease):

    def __init__(self):
        super().__init__('cause.neonatal_preterm_birth', 'risk_factor.low_birth_weight_and_short_gestation')

    def get_exposure_filter(self, distribution, exposure_pipeline, threshold):
        max_weeks_for_preterm = 38

        def exposure_filter(index):
            exposure = exposure_pipeline(index, skip_post_processor=True)
            return exposure.gestation_time <= max_weeks_for_preterm
        return exposure_filter

