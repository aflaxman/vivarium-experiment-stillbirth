import subprocess

"""
Locations:
    India
    Ethiopia
    
    Uttar Pradesh
    Kerala
    Bihar
    
    Sub-saharan Africa Super-region
    South Asia Region
    Low SDI
    Low-middle SDI
    Middle SDI
    High-middle SDI
    High SDI
"""


def run(locations, level):
    """Generates specs for different locations and builds artifacts with them."""
    for loc in locations:
        name = loc
        fname = loc.replace(' ', '_')

        with open("template.yaml") as f:
            template_spec = f.read()

        template_spec = template_spec.format(name=name, fname=fname)

        with open(f"{fname}_{level}.yaml", 'w') as f:
            f.write(template_spec)

        subprocess.call(["build_artifact", "-v", '-o', './', f"{fname}_{level}.yaml"])


def nat():
    locations = ['Ethiopia', 'India']
    run(locations, 'nat')


def supernat():
    locations = ['Sub-Saharan Africa', 'South Asia',
                 'Low SDI', 'Low-middle SDI', 'Middle SDI', 'High-middle SDI', 'High SDI']
    run(locations, 'supernat')


def subnat():
    locations = ['Uttar Pradesh, Rural', 'Uttar Pradesh, Urban', 'Kerala, Rural', 'Kerala, Urban', 'Bihar, Rural',
                 'Bihar, Urban']
    run(locations, 'subnat')


if __name__ == "__main__":
    import sys
    if sys.argv[1] == 'subnat':
        subnat()
    elif sys.argv[1] == 'supernat':
        supernat()
    else:
        nat()
