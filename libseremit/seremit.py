def shellcall(cmd,silent=False):
  # do a system call with shell = true
  # taken from
  # http://stackoverflow.com/questions/699325/suppress-output-in-python-calls-to-executables
  import os
  import subprocess

  # silent will suppress stdoud and stderr, good for testing!
  if silent:
    fnull = open(os.devnull, 'w')
    # we need shell = true to keep the cwd
    result = subprocess.call(cmd, shell = True, stdout = fnull, stderr = fnull)
    fnull.close()
    return result
  else:
    result = subprocess.call(cmd, shell = True)
    return result

class Endpoint(object):
  """An Endpoint (source or target) for a sync operation"""
  pass
  
class Rules(object):
  """Rules for sync operation"""
  pass

class Logger(object):
  """logs to syslog using the unix logger function"""

  def __init__(self,tag):
    self.tag = tag
  
  def log(self,message):
    command = "logger -t %s %s" % (self.tag,message)
    shellcall(command)
    


  
class Result(object):
  """Results of a sync operation"""
  
  def __init__(self):
    self.log=[]
    
  def append_log(self,obj):
    self.log.append(obj)
  
  

class Seremit(object):
  """
  Can sync between 2 points using rsync
  
  Rsync usage:
  
  A trailing slash is not neccesary, but if you add one to the source path, 
  it avoids directory duplication in the target.
  So both forms result in the same transfer:
  
    rsync -av /src/foo /dest
    rsync -av /src/foo/ /dest/foo
    
  -a  A quick way of saying you want recursion and want to preserve almost everything.
  -v  Verbose   
  -z  Compression
  -b, --backup
    With this option, preexisting destination files are renamed as each file 
    is transferred or deleted.
    (BUT ONLY 1 BACKUP IS KEPT BY DEFAULT !!!)
  --remove-source-files
    This tells rsync to remove from the sending side the files 
    (meaning non-directories) that are a part of the transfer and have been 
    successfully duplicated on the receiving side.
  --skip-compress=gz/jpg/mp[34]/7z/bz2
    The default list of suffixes that will not be compressed is this 
    (several of these are newly added for 3.0.0):
    --skip-compress=gz/zip/z/rpm/deb/iso/bz2/t[gb]z/7z/mp[34]/mov/avi/ogg/jpg/jpeg
  --numeric-ids
    With this option rsync will transfer numeric group and user IDs rather than 
    using user and group names and mapping them at both ends.     
  --timeout=TIMEOUT
    This option allows you to set a maximum I/O timeout in seconds. 
    If no data is transferred for the specified time then rsync will exit. 
    The default is 0, which means no timeout.           
  -h, --human-readable
    Output numbers in a more human-readable format.
  --partial
    Using the --partial option tells rsync to keep the partial file if the transfer
    is interrupted which should make a subsequent transfer of the rest 
    of the file much faster.
  --progress
    This option tells rsync to print information showing the progress of the 
    transfer. This gives a bored user something to watch. Implies --verbose           
    """
  
  def __init__(self,syslog_tag=None,fake_run=False):
    self.result = Result()
    self.fake_run=fake_run
    self.logger=Logger(syslog_tag)
    self.log(("init", "fake_run=%s" % (self.fake_run)))
    
  def construct_command(self):
    from std import STD_PARAMS 
    s = self.construct_endpoint(self.source)
    t = self.construct_endpoint(self.target)
    c = "rsync %s %s %s" % (
        STD_PARAMS,s,t)
    self.command = c
    
  def log(self,tup):
    # log to the result log
    self.result.append_log(tup)
    # log to syslog:
    strings = []
    for t in tup:
      strings.append("\"%s\"" % t) 
    self.logger.log(" - ".join(strings))

  def set_source(self,local=True,user=None,host=None,path=None):
    p = Endpoint()
    p.local=local
    p.user = user
    p.host = host
    p.path = path
    self.source = p
    
    
  def set_target(self,local=True,user=None,host=None,path=None):
    p = Endpoint()
    p.local=local
    p.user = user
    p.host = host
    p.path = path
    self.target = p
  
  def set_rules(self,
    # do not remove files in the source tree after copy:
    source_after_sync_action="keep", 
    # do not remove files from target, if removed from source:
    source_removed_action="keep-target", 
    # if a source file changes, overwrite the target file with the new version:
    source_changed_action="overwrite-target"): 
    r = Rules()
    r.source_after_sync_action=source_after_sync_action
    r.source_removed_action=source_removed_action
    r.source_changed_action=source_changed_action
    self.rules = r
  
  def do_sync(self):
    self.construct_command()
    self.run_command()

  def run_command(self):
    if self.fake_run:
      self.log(("shell","fake_run=True",self.command))
    else:
      result = shellresult=shellcall(self.command)
      self.log(("shell","fake_run=False","result=%s" % result,self.command))
      
  def construct_endpoint(self,endpoint):
    e=endpoint
    if e.local:
      # on local endpoints we need only the path
      return e.path
    if e.user is None:
      # no user, so just return hostname and path
      return "%s:%s" % (e.host,e.path)
    #return user,hostname,path:
    return "%s@%s:%s" % (e.user,e.host,e.path)
            
    

  
  def get_result(self):
    return self.result
