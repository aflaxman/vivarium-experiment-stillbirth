# Neonatal Model

Code for neonatal model. 

These models require data from GBD databases. You'll need several internal
IHME packages and access to the IHME cluster. 

To install the extra dependencies create a file called ~/.pip/pip.conf which 
looks like this:

```
[global]
extra-index-url = http://dev-tomflem.ihme.washington.edu/simple
trusted-host = dev-tomflem.ihme.washington.edu
```

To set up a new research environment, open up a terminal on the cluster and run:

```bash
$> conda create --name=neonatal python=3.6
...standard conda install stuff...
$> source activate neonatal
(neonatal) $> conda install redis cython
(neonatal) $> git clone ssh://git@stash.ihme.washington.edu:7999/cste/neonatal.git
...you may need to do username/password stuff here...
(neonatal) $> cd neonatal
(neonatal) $> pip install -e .
```
