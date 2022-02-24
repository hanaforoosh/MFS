class Event_List:
  def __init__(self):
    self.event = {}

  def __setitem__(self, key, value):
    if key in self.event.keys():
      self.event[key].append(value)
    else:
      self.event[key]=[value]

  def __getitem__(self, key):
    e_list = [v for k,v in sorted(self.event.items(),key = lambda x:x[0])]
    e_list = [item for sublist in e_list for item in sublist]
    return e_list[key]

  def pop(self,key=0):
    if self.is_empty():
      return None

    e_list = [(k,v) for k,v in sorted(self.event.items(),key = lambda x:x[0])]
    e_list = [(sublist[0],item) for sublist in e_list for item in sublist[1]]

    target = e_list[key]
    del self[key]
    return target

  def top(self,key=0):
    if self.is_empty():
      return None

    e_list = [(k,v) for k,v in sorted(self.event.items(),key = lambda x:x[0])]
    e_list = [(sublist[0],item) for sublist in e_list for item in sublist[1]]

    target = e_list[key]
    return target

  def __delitem__(self, key):
    e_list = [(k,v) for k,v in sorted(self.event.items(),key = lambda x:x[0])]
    e_list = [sublist[0] for sublist in e_list for item in sublist[1]]
    target = e_list[key]
    tmp = [ i for i,n in enumerate(e_list) if n==target]
    oc = tmp.index(key)
    self.event[target].pop(oc)
    if len(self.event[target])==0:
      self.event.pop(target)

  def __str__(self):
    e_list = [(k,v) for k,v in sorted(self.event.items(),key = lambda x:x[0])]
    return e_list.__str__()

  def is_empty(self):
    return len(self.event) == 0


  def first_event(self,event,pm_id):
    e_list = [(k,v) for k,v in sorted(self.event.items(),key = lambda x:x[0])]
    e_list = [(sublist[0],item) for sublist in e_list for item in sublist[1]]
    for k,v in e_list:
      if v[0]==event and v[1] == pm_id:
        return k