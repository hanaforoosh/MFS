import sys
sys.path.insert(0, 'Simulator')
from Controller import *

p = [
     PM(id=0,ram=1,cpu=1)
]
f = [
      Function(id=0,t=i,execution_time=5,ram=1,cpu=1,gpu=0,tpu=0,deadline=300) for i in range(0,10)
  ]

s = Controller(physical_machines=p,functions=f)
s.run(conversion_allowed=False,verbose=False,global_scheduling_strategy='loadbalancing',steal_warm_allowed=False,warm_start_delay = 1,steal_warm_delay=2,cold_start_delay=3)
s.show_statistics(verbose=True)