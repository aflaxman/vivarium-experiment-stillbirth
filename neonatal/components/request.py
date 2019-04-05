import gbd_mapping
from vivarium_inputs.globals import DataDoesNotExistError

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
        builder.data.load("population.structure")
        builder.data.load("population.theoretical_minimum_risk_life_expectancy")
        builder.data.load("cause.all_causes.cause_specific_mortality")
        builder.data.load("covariate.live_births_by_sex.estimate")

        # Cause-level things
        for cause in self.causes:
            builder.data.load(f"cause.{cause.name}.prevalence")
            builder.data.load(f"cause.{cause.name}.birth_prevalence")
            builder.data.load(f"cause.{cause.name}.cause_specific_mortality")
            builder.data.load(f"cause.{cause.name}.excess_mortality")
            try:
                builder.data.load(f"cause.{cause.name}.incidence")
            except DataDoesNotExistError:
                pass
            builder.data.load(f"cause.{cause.name}.disability_weight")
            for seq in cause.sequelae:
                builder.data.load(f"sequela.{seq.name}.prevalence")
                builder.data.load(f"sequela.{seq.name}.birth_prevalence")
                try:
                    builder.data.load(f"sequela.{seq.name}.incidence")
                except DataDoesNotExistError:
                    pass
                builder.data.load(f"sequela.{seq.name}.disability_weight")
