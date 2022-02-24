class Container:
  def __init__(self,id,ram,cpu,gpu,tpu,runtime='python',status='COLD',fx=None):
    self.id = id
    self.execution_time = 0
    self.ram = ram
    self.cpu = cpu
    self.gpu = gpu
    self.tpu = tpu
    self.status = status
    self.runtime = runtime
    self.fx = fx

    self.waited_clock = None

  def inject(self,fx):
    self.fx = fx

  def __str__(self):
    if self.fx == None:
      return f'Container(id={self.id},RAM={self.ram},CPU={self.cpu},GPU={self.gpu},TPU={self.tpu},Execution time={self.execution_time})'
    else:
      return f'Container(id={self.id},RAM={self.ram},CPU={self.cpu},GPU={self.gpu},TPU={self.tpu},Execution time={self.execution_time},{self.fx})'

  def __repr__(self):
    return self.__str__()