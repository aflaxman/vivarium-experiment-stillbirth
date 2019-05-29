import gbd_mapping
from vivarium_inputs.globals import DataDoesNotExistError
from vivarium_public_health.utilities import EntityString

"""
[x] population
[x] all cause mortality
[x] live births by sex
[x] theoretical min risk LE
[x] enceph / BA + NN preterm
        prev
        birth prev
        CSMR
        excess mort
        incidence (?)
        disability weights
        sequelae
            incidence (?)
            prev
            birth prev
            disability weights
"""


class ResearcherRequestComponent:
    """A one-off component to explicitly load data requested by an outside researcher/Abie"""

    def __init__(self):
        self.causes = [gbd_mapping.causes.neonatal_encephalopathy_due_to_birth_asphyxia_and_trauma,
                       gbd_mapping.causes.neonatal_preterm_birth]

    def setup(self, builder):

        # Top-level things
        keys = [
            "population.structure",
            "population.theoretical_minimum_risk_life_expectancy",
            "cause.all_causes.cause_specific_mortality",
            "covariate.live_births_by_sex.estimate"
        ]
        for key in keys:
            try:
                builder.data.load(key)
            except DataDoesNotExistError:
                pass

        # Cause-level things
        for cause in self.causes:
            keys = [
                f"cause.{cause.name}.prevalence",
                f"cause.{cause.name}.birth_prevalence",
                f"cause.{cause.name}.cause_specific_mortality",
                f"cause.{cause.name}.excess_mortality",
                f"cause.{cause.name}.incidence",
                f"cause.{cause.name}.disability_weight",
            ]

            for key in keys:
                try:
                    builder.data.load(key)
                except DataDoesNotExistError:
                    pass

            for seq in cause.sequelae:
                keys = [
                    f"sequela.{seq.name}.prevalence",
                    f"sequela.{seq.name}.birth_prevalence",
                    f"sequela.{seq.name}.incidence",
                    f"sequela.{seq.name}.disability_weight",
                ]

                for key in keys:
                    try:
                        builder.data.load(key)
                    except DataDoesNotExistError:
                        pass

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
