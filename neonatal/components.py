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