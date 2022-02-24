from Function import Function
from Container import Container

class PM:
  def __init__(self,id,ram,cpu,gpu=0,tpu=0):
    self.id = id
    self.ram = ram
    self.cpu = cpu
    self.gpu = gpu
    self.tpu = tpu

    self.used_ram = 0
    self.used_cpu = 0
    self.used_gpu = 0
    self.used_tpu = 0

    self.functions_queue = []
    self.containers_queue = []

    self.completed_functions=[]
    self.missed_functions=[]
    self.rejected_functions=[]
    self.completed_containers=[]

    self.ram_utilization = 0
    self.cpu_utilization = 0
    self.gpu_utilization = 0
    self.tpu_utilization = 0

    self.ram_unit_price = None
    self.cpu_unit_price = None
    self.gpu_unit_price = None
    self.tpu_unit_price = None

    self.container_warm_time = None
    self.cold_start_delay = None
    self.warm_start_delay = None
    self.steal_warm_delay = None
    self.cpu_over_gpu = None
    self.cpu_over_tpu = None
    self.verbose = False

    self.penalty_coeff = None
    self.cost_coeff = None
    self.conversion_allowed = None
    self.steal_warm_allowed = None

    self.cold_starts = 0
    self.warm_starts = 0

  def __str__(self):
    return f'PM(id={self.id},RAM={self.ram},CPU={self.cpu},GPU={self.gpu},TPU={self.tpu})'

  def __repr__(self):
    return self.__str__()

  def add_function(self,fx: Function):
    self.functions_queue.append(fx)

  def remove_function(self,fx):
    self.functions_queue = [x for x in self.functions_queue if x != fx]



  def get_available_resources(self):
    r = self.ram - self.used_ram
    c = self.cpu - self.used_cpu
    g = self.gpu - self.used_gpu
    t = self.tpu - self.used_tpu

    return r,c,g,t

  def get_functions_to_schedule(self):
    fx_list = []

    available_ram, available_cpu, available_gpu, available_tpu, = self.get_available_resources()
    for fx in self.functions_queue:
      if fx.ram <= available_ram and fx.cpu <= available_cpu and fx.gpu <= available_gpu and fx.tpu <= available_tpu:
        fx_list.append(fx)
        available_ram -= fx.ram
        available_cpu -= fx.cpu
        available_gpu -= fx.gpu
        available_tpu -= fx.tpu
    
    return fx_list

  def get_warm_container(self,fx):
    appropriate_warm_containers = [c for c in self.containers_queue if (c.status == 'WARM' and c.ram >=fx.ram and c.cpu >= fx.cpu and c.gpu >= fx.gpu and c.tpu >= fx.tpu and c.runtime == fx.runtime)]
    if len(appropriate_warm_containers)>0:
      for app in appropriate_warm_containers:
        if app.fx.id == fx.id:
          if self.verbose:
            print('[WARM]')
          self.warm_starts+=1
          return app,self.warm_start_delay
      if self.steal_warm_allowed == True:
        if self.verbose:
          print('[Steal WARM]')

        # Yes, it is cold. not warm
        self.cold_starts+=1
        return appropriate_warm_containers[0], self.steal_warm_delay
      else:
        return None,None
    else:
      return None,None

  def make_container(self, fx):
    if self.can_run(fx):
      c = Container(id=fx.id,ram=fx.ram,cpu=fx.cpu,gpu=fx.gpu,tpu=fx.tpu,runtime=fx.runtime,status='COLD')
      self.containers_queue.append(c)
      if self.verbose:
        print('[COLD]')

      self.cold_starts+=1
      return c,self.cold_start_delay
    else:
      return None,None

  def remove_container(self,c):
    self.functions_queue = [x for x in self.containers_queue if x.id != c.id]

  def convert(self,fx:Function,inplace = False):
    if self.conversion_allowed == False:
      return fx

    execution_time = fx.execution_time
    cpu = fx.cpu
    if fx.gpu>0:
      execution_time = execution_time * self.cpu_over_gpu
      cpu+= fx.gpu
    if fx.tpu>0:
      execution_time = execution_time * self.cpu_over_tpu
      cpu+=fx.tpu
    if inplace:
      fx.execution_time = execution_time
      fx.cpu = cpu
      fx.gpu = 0
      fx.tpu = 0
    else:
      gx = Function(t=fx.t,id=fx.id,execution_time=execution_time,ram=fx.ram,cpu=cpu,gpu=0,tpu=0,runtime=fx.runtime,priority=fx.priority,deadline=fx.deadline)
      return gx

  def can_run(self,fx):
    available_ram, available_cpu, available_gpu, available_tpu, = self.get_available_resources()
    return fx.ram <= available_ram and fx.cpu <= available_cpu and fx.gpu <= available_gpu and fx.tpu <= available_tpu


  def can_accept(self, fx):
    if fx.ram <= self.ram and fx.cpu <= self.cpu and fx.gpu <= self.gpu and fx.tpu <= self.tpu:
      return True
    else:
      return False

  def run(self,clock,c):
    if c.status=='COLD':

      self.used_ram+=c.ram
      self.used_cpu+=c.cpu
      self.used_gpu+=c.gpu
      self.used_tpu+=c.tpu

    if c.status=='WARM' and c.waited_clock!=None:
      c.execution_time += clock - c.waited_clock  
      
    c.status = 'HOT'


    return c.fx.execution_time

  def is_container_in_use(self,c):
    return c.status == 'HOT'


  def container_done(self,clock,event_list, c):
    fx = c.fx
    if c.status == 'HOT':
      # take care of the completed fx. just once!
      c.execution_time += fx.execution_time
      fx.finished_at = clock
      self.completed_functions.append(fx)
    
    if self.container_warm_time == 0 or c.status =='WARM':
      # timeout or no warm_time at all
      if c.waited_clock != None:
        c.execution_time += clock - c.waited_clock
      self.update_metrics(c,clock)
      self.used_ram-=c.ram
      self.used_cpu-=c.cpu
      self.used_gpu-=c.gpu
      self.used_tpu-=c.tpu
      self.completed_containers.append(c)
      self.containers_queue = [x for x in self.containers_queue if x.id!=c.id]
    else:
      c.status= 'WARM'
      # c.fx = None
      c.waited_clock = clock
      event_list [clock+self.container_warm_time] = ('LOCAL_CONTAINER_WARM_TIMEOUT',self,c)


  def show_status(self,clock):
    status = self.get_status(clock)
    print('='*(len(str(self))+4))
    print('|',self,'|')
    print('='*(len(str(self))+4))
    for k,v in status.items():
      print(' ',k,v)


  def get_status(self,clock):
    status=dict()

    running_containers = [c for c in self.containers_queue if c.status=='HOT']
    running_functions =  [c.fx for c in running_containers]
    missed_functions = self.missed_functions
    rejected_functions=self.rejected_functions
    # completed_functions = in-time completed + missed
    completed_functions= self.completed_functions
    completed_containers= self.completed_containers
    
    if clock>0:
      ramutil = self.ram_utilization/clock
      cpuutil = self.cpu_utilization/clock
      gpuutil = self.gpu_utilization/clock
      tpuutil = self.tpu_utilization/clock
      util =  {'RAM':round(ramutil,2),'CPU':round(cpuutil,2),'GPU':round(gpuutil,2),'TPU':round(tpuutil,2)}
      
    price = 0
    total_response_time = 0
    total_waiting_time  = 0
    total_service_time  = 0
    for f in completed_functions:
      price+= self.pricing_model(f)
      # R = W + S
      # W = R - S
      R = f.finished_at - f.t
      S = f.execution_time
      W = R - S
      total_response_time += R
      total_waiting_time +=  W
      total_service_time +=  S
    

    if len(completed_functions)>0:
      average_respone_time = total_response_time/ len(completed_functions)
      average_waiting_time = total_waiting_time / len(completed_functions)
      average_service_time = total_service_time / len(completed_functions)

    else:
      average_respone_time = 0
      average_waiting_time = 0
      average_service_time = 0

    status['average response time']=round(average_respone_time,2)
    status['average waiting time']=round(average_waiting_time,2)
    status['average service time']=round(average_service_time,2)

    status ['throughput'] = round(len(completed_functions)/clock,2)
    status ['in-time throughput'] = round((len(completed_functions)-len(missed_functions))/clock,2)

    status ['completed containers']=completed_containers
    status ['completed functions']=completed_functions
    status ['rejected functions']=rejected_functions
    status ['missed functions']=missed_functions 

    if (len(completed_functions)+len(rejected_functions))>0:
      status['completion ratio']=round(len(completed_functions)  /  (len(completed_functions)+len(rejected_functions))                                  ,2)
      status['in-time completion ratio']=round((len(completed_functions)-len(missed_functions))  /  (len(completed_functions)+len(rejected_functions))  ,2)
      status['rejection ratio']=round(len(rejected_functions)  /  (len(completed_functions)+len(rejected_functions))                                    ,2)
      status['missed ratio']=round(len(missed_functions)  /  (len(completed_functions)+len(rejected_functions))                                         ,2)
    else:
      status['completion ratio']=0
      status['intime completion ratio']=0
      status['rejection ratio']=0
      status['missed ratio']=0

    status['warm starts'] = self.warm_starts
    status['cold starts'] = self.cold_starts
    if self.warm_starts + self.cold_starts >0:
      status['warm start ratio'] = round(self.warm_starts / (self.warm_starts + self.cold_starts),2)
      status['cold start ratio'] = round(self.cold_starts / (self.warm_starts + self.cold_starts),2)
    else:
      status['warm start ratio'] = 0
      status['cold start ratio'] = 0

    status['utilization'] = util

    status['price'] = round(price,2)

    cost = 0
    for c in completed_containers:
      cost+= self.pricing_model(c) * self.cost_coeff
    status['cost'] = round(cost,2)


    penalty = 0
    for f in missed_functions:
        penalty += self.pricing_model(f)* self.penalty_coeff
    for f in rejected_functions:
        penalty += self.pricing_model(f)* self.penalty_coeff
    status['penalty']=round(penalty,2)

    status['loss']=round(cost+penalty-price,2)


    return status


  def update_metrics(self,c,clock):
    if clock > 0:
      
      self.ram_utilization = self.utilization(self.ram_utilization,c.ram,self.ram,c.execution_time)
      self.cpu_utilization = self.utilization(self.cpu_utilization,c.cpu,self.cpu,c.execution_time)
      self.gpu_utilization = self.utilization(self.gpu_utilization,c.gpu,self.gpu,c.execution_time)
      self.tpu_utilization = self.utilization(self.tpu_utilization,c.tpu,self.tpu,c.execution_time)

  def get_current_utilization(self):
    num_resource_type = 0
    total_util = 0
    if self.ram> 0:
      num_resource_type+=1
      ram_util = self.used_ram / self.ram
      total_util+=ram_util

    if self.cpu> 0:
      num_resource_type+=1
      cpu_util = self.used_cpu / self.cpu
      total_util+=cpu_util

    if self.gpu> 0:
      num_resource_type+=1
      gpu_util = self.used_gpu / self.gpu
      total_util+=gpu_util
    
    if self.tpu> 0:
      num_resource_type+=1
      tpu_util = self.used_tpu / self.tpu
      total_util+=tpu_util

    return total_util/num_resource_type

  # Models
  def utilization(self,old_utilization_value,used_amount,total_amount,duration):
    try:
      now_util = used_amount / total_amount
      timed_now_util = now_util * duration
      new_util = old_utilization_value + timed_now_util
      return new_util
    except:
      return 0


  def pricing_model(self,unit):
    ram = unit.ram * unit.execution_time * self.ram_unit_price
    cpu = unit.cpu * unit.execution_time * self.cpu_unit_price
    gpu = unit.gpu * unit.execution_time * self.gpu_unit_price
    tpu = unit.tpu * unit.execution_time * self.tpu_unit_price
    total = ram + cpu + gpu + tpu
    return total



  def local_scheduler(self,clock,event_list):
    if self.verbose:
      print(f'[Scheduling in PM {self.id}]')
    fx_list = self.functions_queue
    for fx in fx_list:
      # Warm start
      c,delay = self.get_warm_container(fx)

      
      if c == None:
      # Cold start
        c,delay = self.make_container(fx)

      if c== None:
        # Try to change the hardware
        gx = self.convert(fx)
        # Warm start
        c,delay = self.get_warm_container(gx)    
        if c == None:
        # Cold start
          c,delay = self.make_container(gx)

        if c!= None:
          if self.verbose:
            print('[Converting...]')
          self.convert(fx,True)
      
      if c == None:
      # Not enough resources
        if self.verbose:
          print('Not enough resources')
        
        if self.can_accept(fx) or self.can_accept(self.convert(fx)):
        # Run later
          first_event_function_done = event_list.first_event('LOCAL_FUNCTION_DONE',self)
          first_event_container_warm_timeout = event_list.first_event('LOCAL_CONTAINER_WARM_TIMEOUT',self)
          if first_event_function_done == None:
            first_event = first_event_container_warm_timeout
          elif first_event_container_warm_timeout == None:
            first_event = first_event_function_done
          else:
            first_event = min(first_event_function_done, first_event_container_warm_timeout)
          
          if self.verbose:
            print(fx,'postponed until',first_event)

          first_event_FUNCTION_SCHEDULE = event_list.first_event('LOCAL_FUNCTION_SCHEDULE',self)
          if first_event_FUNCTION_SCHEDULE == None:
            event_list [first_event] = ('LOCAL_FUNCTION_SCHEDULE',self) 

        else:
          # Reject
          self.remove_function(fx)
          self.rejected_functions.append(fx)
          if self.verbose:
            print("can't accept")

      else:
      # Run now
        c.inject(fx)
        if self.verbose:
          print(fx,'->',c)

        t = self.run(clock,c)
        self.remove_function(fx)
        run_clock = clock+delay+t
        if run_clock> fx.deadline:
          self.missed_functions.append(fx)
        event_list[run_clock] = ('LOCAL_FUNCTION_DONE',self,c)