from copy import deepcopy
from PM import PM
from Function import Function
from Event_List import Event_List

class Controller:
  def __init__(self,physical_machines:list,functions):
    # Parameters
    self.tmp_p = physical_machines
    self.tmp_f = functions
    self.f_counter = 0

  def function_arrival(self,next_event,clock,event_list):
    # Global Scheduler
    p = self.p
    verbose = self.verbose
    global_scheduling_strategy = self.global_scheduling_strategy

    fx = next_event[1]
    if global_scheduling_strategy == 'loadbalancing':
      pm_index = self.f_counter % len(p)
      self.f_counter +=1
      pm = p[pm_index]
    elif global_scheduling_strategy == 'utilization':
      pm = p [0]
      utilized_pms = [pm for pm in p]
      utilized_pms = sorted(utilized_pms,key= lambda x:x.get_current_utilization(),reverse=True)

      for pmx in utilized_pms:
        if pmx.can_accept(fx) or pmx.can_accept(pmx.convert(fx)):
          pm = pmx
          break
    else:
      raise Exception('Invalid strategy!')

    if verbose:
      print(pm)
    
    pm.add_function(fx)
    pm.local_scheduler(clock,event_list)

  def local_function_schedule(self,next_event,clock,event_list):
    p = self.p
    verbose = self.verbose

    pm = next_event[1]
    if verbose:
      print(pm)

    pm.local_scheduler(clock,event_list)
    
  def local_function_done(self,next_event,clock,event_list):
    p = self.p
    verbose = self.verbose

    pm = next_event[1]
    if verbose:
      print(pm)

    container = next_event[2]
    pm.container_done(clock,event_list,container)

  def local_container_warm_timeout(self,next_event,clock,event_list):
    p = self.p
    verbose = self.verbose

    pm = next_event[1]
    if verbose:
      print(pm)
    container = next_event[2]

    if not pm.is_container_in_use(container):
      pm.container_done(clock,event_list,container)
      if verbose:
        print('container removed')
    else:
      if verbose:
        print('The container is in use. ignoring TIMEOUT...')


  def show_statistics(self,verbose = True):
    parameters = self.parameters
    print('Experiment parameters:')
    for k,v in parameters.items():
      print('{:<30}  {:>30}'.format(k, v))

    print('_'*62)
    result = self.get_statistics()
    for k,v in result.items():
      if type(k)==PM:
        if verbose:
          print('='*(len(str(k))+4))
          print('|',k,'|')
          print('='*(len(str(k))+4))

          for kp,vp in v.items():
            print(' ',kp,vp)
          print('_'*62)
      elif type(v)==dict:
        print(k)
        for kp,vp in v.items():
          print('  {:<28}  {:>30}'.format(kp, vp))
      else:
        print('{:<30}  {:>30}'.format(k, v))

  def get_statistics(self):
    result =dict()
    total_functions = len(self.f)

    total_cold_starts = 0
    total_warm_starts = 0

    total_response_time = 0
    total_waiting_time  = 0
    total_service_time  = 0

    len_completed = 0
    len_missed =0
    len_rejected=0

    price = 0
    cost = 0
    penalty =0
    ram_util = 0
    cpu_util = 0
    gpu_util = 0
    tpu_util = 0
    for pm in self.p:
      status = pm.get_status(self.clock)
      result[pm]=status

      cold_starts = status ['cold starts']
      warm_starts = status ['warm starts']

      total_cold_starts += cold_starts
      total_warm_starts += warm_starts

      completed_containers=status['completed containers']
      completed_functions = status['completed functions']
      len_completed+=len(completed_functions)
      len_missed+=len(status['missed functions'])
      len_rejected+=len(status['rejected functions'])
      

      total_response_time+=status['average response time']*len(completed_functions)
      total_waiting_time +=status['average waiting time']*len(completed_functions)
      total_service_time +=status['average service time']*len(completed_functions)

      price += status['price']
      cost += status['cost']
      penalty+=status['penalty']

      if 'utilization' in status:
        util = status['utilization']
        ram_util += util['RAM']
        cpu_util += util['CPU']
        gpu_util += util['GPU']
        tpu_util += util['TPU']

    result['total time'] = self.clock
    if len_completed>0:
      result['average response time'] = round(total_response_time/len_completed,2)
      result['average waiting time'] = round(total_waiting_time/len_completed,2)
      result['average service time'] = round(total_service_time/len_completed,2)

    else:
      result['average response time'] = 0
      result['average response time'] = 0
      result['average response time'] = 0

    result['throughput'] = round(len_completed / self.clock,2)
    result['in-time throughput']=round((len_completed-len_missed) / self.clock,2)

    if total_functions>0:
      result['completion ratio']=round(len_completed  /  total_functions                        ,2)
      result['in-time completion ratio']=round((len_completed-len_missed)  /  total_functions   ,2)
      result['rejection ratio']=round(len_rejected  /  total_functions                          ,2)
      result['missed ratio']=round(len_missed  /  total_functions                               ,2)
    else:
      result['completion ratio']=0
      result['intime completion ratio']=0
      result['rejection ratio']=0
      result['missed ratio']=0

    if total_cold_starts + total_warm_starts >0:
      result['warm start ratio'] = round(total_warm_starts / (total_cold_starts + total_warm_starts),2)
      result['cold start ratio'] = round(total_cold_starts / (total_cold_starts + total_warm_starts),2)
    else:
      result['warm start ratio'] = 0
      result['cold start ratio'] = 0

    util = dict()
    util['RAM']=round(ram_util/len(self.p),2)
    util['CPU']=round(cpu_util/len(self.p),2)
    util['GPU']=round(gpu_util/len(self.p),2)
    util['TPU']=round(tpu_util/len(self.p),2)
    result['utilization'] = util

    result['price']=round(price,2)
    result['cost']=round(cost,2)
    result['penalty']=round(penalty,2)
    result['loss']=round(cost+penalty-price,2)

    return result

  def run(self,container_warm_time = 2, cold_start_delay=2,warm_start_delay=0, steal_warm_delay=1,
              steal_warm_allowed = False, conversion_allowed=False, 
              cpu_over_gpu=2,cpu_over_tpu=4, ram_unit_price = 21, cpu_unit_price = 0, gpu_unit_price = 0, tpu_unit_price = 0,
              global_scheduling_strategy ='utilization',cost_coeff = 0.8,penalty_coeff = 4 , verbose=False):
    
    self.p = deepcopy(self.tmp_p)
    self.f = deepcopy(self.tmp_f)
    
    parameters = dict()
    parameters['container warm time'] = container_warm_time
    parameters['cold start delay'] = cold_start_delay
    parameters['warm start delay'] = warm_start_delay
    parameters['steal warm delay'] = steal_warm_delay

    parameters['conversion allowed'] = conversion_allowed
    parameters['steal warm allowed'] = steal_warm_allowed

    parameters['cpu over gpu'] = cpu_over_gpu
    parameters['cpu over tpu'] = cpu_over_tpu
    parameters['ram unit price'] = ram_unit_price
    parameters['cpu unit price'] = cpu_unit_price
    parameters['gpu unit price'] = gpu_unit_price
    parameters['tpu unit price'] = tpu_unit_price

    parameters['global scheduling strategy'] = global_scheduling_strategy
    parameters['cost coeff'] = cost_coeff
    parameters['penalty coeff'] = penalty_coeff
    parameters['verbose'] = verbose
    
    self.parameters = parameters

    self.event_list = Event_List()
    
    for item in self.f:
      i = item.t
      self.event_list[i]=('FUNCTION_ARRIVAL',item)

    self.clock = 0
    self.container_warm_time = container_warm_time
    self.cold_start_delay = cold_start_delay
    self.warm_start_delay = warm_start_delay
    self.steal_warm_delay = steal_warm_delay

    self.cpu_over_gpu = cpu_over_gpu
    self.cpu_over_tpu = cpu_over_tpu
    self.ram_unit_price=ram_unit_price
    self.cpu_unit_price=cpu_unit_price
    self.gpu_unit_price=gpu_unit_price

    self.tpu_unit_price = tpu_unit_price
    self.global_scheduling_strategy = global_scheduling_strategy
    self.verbose = verbose

    for pm in self.p:
      pm.t = 0
      pm.container_warm_time = container_warm_time
      pm.cold_start_delay = cold_start_delay
      pm.warm_start_delay = warm_start_delay
      pm.steal_warm_delay = steal_warm_delay
      pm.cpu_over_gpu = cpu_over_gpu
      pm.cpu_over_tpu = cpu_over_tpu    

      pm.ram_unit_price = ram_unit_price
      pm.cpu_unit_price = cpu_unit_price
      pm.gpu_unit_price = gpu_unit_price
      pm.tpu_unit_price = tpu_unit_price
      pm.cost_coeff = cost_coeff
      pm.penalty_coeff = penalty_coeff
      pm.conversion_allowed = conversion_allowed
      pm.steal_warm_allowed = steal_warm_allowed
      pm.verbose = verbose

    event_list = self.event_list


    
    while not event_list.is_empty():
      if self.verbose:
        print('------------------------------')
      clock,next_event = event_list.pop()
      self.clock = clock
      
      if self.verbose:
        print('Clock =',clock)
        print('Event =',next_event)
      
      e_type = next_event[0]
      if e_type =='FUNCTION_ARRIVAL':
        self.function_arrival(next_event,clock,event_list)

      elif e_type =='LOCAL_FUNCTION_SCHEDULE':
        self.local_function_schedule(next_event,clock,event_list)

      elif e_type=='LOCAL_FUNCTION_DONE':
        self.local_function_done(next_event,clock,event_list)

      elif e_type=='LOCAL_CONTAINER_WARM_TIMEOUT':
        self.local_container_warm_timeout(next_event,clock,event_list)