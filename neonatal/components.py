import pandas as pd


class LBWSGRisk:

    def __init__(self):
        self.name = 'low_birth_weight_and_short_gestation'

    def setup(self, builder):
        self.randomness = builder.randomness.get_stream(f'lbwsg')

        self._bw_and_gt = pd.DataFrame(columns=['birth_weight', 'gestation_time'])

        self.exposure = builder.value.register_value_producer(
            'low_birth_weight_and_short_gestation.exposure',
            source=self.get_current_exposure,
            preferred_post_processer=self.get_lbwsg_post_processor()
        )

    def get_current_exposure(self, index):
        return self._bw_and_gt.iloc[index]

    def get_lbwsg_post_processor(self):
