# MFS: a Serverless FaaS Simulator
![version](https://img.shields.io/static/v1?label=Version&message=1.0.0&color=informational&style=for-the-badge)

MFS is a FaaS simulator designed to be easy and accurate. it supports many metrics such as:
* average respone time
* average waiting time
* average service time
* rejection ratio
* missed ratio
* throughput
* different resource utilizations
* etc

# Sample Usage:
1. first you should add `Simulator` directory to the `Sys.path`. then you need to import the controller as follows:
```python
import sys
sys.path.insert(0, 'Simulator')
from Controller import *
```
2. then you should specify `PM` and `Function` lists, followed by a run statement:

```python
p = [
     PM(id=0,ram=1,cpu=1)
]
f = [
      Function(id=0,t=i,execution_time=5,ram=1,cpu=1,gpu=0,tpu=0,deadline=300) for i in range(0,10)
  ]

s = Controller(physical_machines=p,functions=f)
s.run()
```

# Citation
To cite MFS please use the following format:
```
M. Hanaforoosh, M. Ashtiani and M. A. Azgomi, "MFS: A Serverless FaaS Simulator," 2023 9th International Conference on Web Research (ICWR), Tehran, Iran, Islamic Republic of, 2023, pp. 81-86, doi: 10.1109/ICWR57742.2023.10139045.
```
