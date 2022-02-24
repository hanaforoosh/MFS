class Function:
  def __init__(self,t,id,execution_time,ram,cpu,gpu=0,tpu=0,runtime='python',priority=1,deadline=None):
    self.t = t
    self.id = id
    self.execution_time = execution_time
    if deadline == None:
      self.deadline = 100 * execution_time
    else:
      self.deadline = deadline
    self.ram = ram
    self.cpu = cpu
    self.gpu = gpu
    self.tpu = tpu
    self.runtime = runtime
    self.priority = priority
    self.finished_at = None

  def __str__(self):
    return f'Function(id={self.id},RAM={self.ram},CPU={self.cpu},GPU={self.gpu},TPU={self.tpu},Entered at {self.t},Finished at {self.finished_at},Execution time={self.execution_time},Deadline={self.deadline},Runtime={self.runtime})'

  def __repr__(self):
    return self.__str__()