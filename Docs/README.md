# Sample Usage
a very simple usage includes importing the `Simulator`, followed by specifying the `PM` and `Function` lists. then you only need to run `MFS`. The step by step guide is as follows:

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

# Classes
MFS includes following classes: Controller, PM, Container, Function, and Event_List. short description for each of them is available as follows:

**Controller:** This class is the main class and represents the controller component of Apache Openwhisk. This class has the task of scheduling input functions and executing them on their corresponding machines. The global scheduler is defined in this class. Two strategies of high utilization and load distribution are considered for the scheduling in this class. This class selects physical machines to execute functions according to the selected strategy.

**PM:** This class represents physical machines and is equivalent to the worker nodes in Apache OpenWhisk. Hence, the local scheduler is defined in this class which is responsible for executing the assigned functions locally. This class calculates various metrics (e.g., the average response time) per machine and reports it to the controller. Then, the controller calculates the overall metrics according to the report.

**Container:** This class represents containers. Of course, the management of the containers is the responsibility of the PM class. But, the specifications of the containers, including their statue (i.e., cold or warm) are defined in this class.

**Function:** Functions are defined through this class. Their various specifications are defined in this class, including the submission time, RAM, required processing unit and its amount, runtime (i.e., the language in which the function is written), and deadline

**Event_List:** The event list structure is defined in this class. This class is an extended priority queue that provides more capabilities than a regular priority queue. For example, it is possible to view the next LOCAL_FUNCTION_DONE event in this class.
