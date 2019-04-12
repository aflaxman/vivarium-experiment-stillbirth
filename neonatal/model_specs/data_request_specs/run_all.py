import shutil
import os
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


def run(loc, level):
    """Generates specs for a location and build artifacts with them."""
    name = loc
    fname = loc.replace(' ', '_')

    with open("template.yaml") as f:
        template_spec = f.read()

    template_spec = template_spec.format(name=name, fname=fname)

    with open(f"{fname}_{level}.yaml", 'w') as f:
        f.write(template_spec)

    subprocess.call(["build_artifact", "-v", '-o', './', f"{fname}_{level}.yaml"])


# def nat():
#     locations = ['Ethiopia', 'India']
#     run(locations, 'nat')
#
#
# def supernat():
#     locations = ['Sub-Saharan Africa', 'South Asia',
#                  'Low SDI', 'Low-middle SDI', 'Middle SDI', 'High-middle SDI', 'High SDI']
#     run(locations, 'supernat')
#
#
# def subnat():
#     locations = ['Uttar Pradesh, Rural', 'Uttar Pradesh, Urban', 'Kerala, Rural', 'Kerala, Urban', 'Bihar, Rural',
#                  'Bihar, Urban']
#     run(locations, 'subnat')


def launch():
    import drmaa
    locations = {'national': ['Ethiopia', 'India'],
                 'supernational': ['Sub-Saharan Africa', 'South Asia', 'Low SDI', 'Low-middle SDI', 'Middle SDI',
                                   'High-middle SDI', 'High SDI'],
                 'subnational': ['Uttar Pradesh, Rural', 'Uttar Pradesh, Urban', 'Kerala, Rural', 'Kerala, Urban',
                                 'Bihar, Rural', 'Bihar, Urban']}

    with drmaa.Session() as s:
        jt = s.createJobTemplate()
        jt.workingDirectory = os.getcwd()
        jt.remoteCommand = shutil.which('python')
        for level, sub_locations in locations.items():
            for loc in sub_locations:
                loc = loc.replace(' ', '_')  # worried about spaces ruining things
                jt.nativeSpecification = f'-V -w n -q all.q -l m_mem_free=20G -N {loc} -l fthread=1 -P proj_cost_effect'
                jt.args = ['run_all.py', loc, level]
                s.runJob(jt)
        s.deleteJobTemplate(jt)


if __name__ == "__main__":
    import sys
    loc = sys.argv[1]
    loc = loc.replace('_', ' ')
    level = sys.argv[2]
    run(loc, level)
