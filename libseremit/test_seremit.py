#!/usr/bin/python
import unittest as unittest

import seremit

import os
opj = os.path.join

# a = archiv mdoe, keep attributes
# v = a little verbose
# z = compress
# stats = output little summary at the end

STD_PARAMS = "-avz --stats" + \
  " --timeout=320" + \
  " --numeric-ids" + \
  " --partial" 

class TestSeremit(unittest.TestCase):
      
  def testSeremit1(self):
    s=self.s
    self.assertEqual(s.get_result().log,[("init","fake_run=True")])

  def testRsync1(self):
    s=self.s
    s.set_source(local=False,user="seremit",host="remote.example.com",path="/mnt/backup/src1/")
    s.set_target(local=True,path="/mnt/archive/example-com/")
    self.s.do_sync()
    self.assertEqual(s.get_result().log,[
      ("init","fake_run=True"),
      ("shell","fake_run=True","rsync %s seremit@remote.example.com:/mnt/backup/src1/ /mnt/archive/example-com/" % STD_PARAMS),
    ])
   
  def testRsync2(self):
    # no user this time
    s=self.s
    s.set_source(local=False,host="remote.example.com",path="/mnt/backup/src1/")
    s.set_target(local=True,path="/mnt/archive/example-com/")
    s.option_progress()
    self.s.do_sync()
    self.assertEqual(s.get_result().log,[
      ("init","fake_run=True"),
      ("shell","fake_run=True","rsync %s %s remote.example.com:/mnt/backup/src1/ /mnt/archive/example-com/" % (STD_PARAMS,"--progress")),
    ])
   
  def testRsync3(self):
    # 2 remote endpoints
    s=self.s
    s.set_source(local=False,user="user1",host="remote1.example.com",path="/mnt/backup/src1/")
    s.set_target(local=False,user="user2",host="remote2.example.com",path="/mnt/backup/target1/")
    self.s.do_sync()
    self.assertEqual(s.get_result().log,[
      ("init","fake_run=True"),
      ("shell","fake_run=True","rsync %s user1@remote1.example.com:/mnt/backup/src1/ user2@remote2.example.com:/mnt/backup/target1/" % STD_PARAMS),
    ])
   
  def testRsync4(self):
    # 2 local endpoints
    s=self.s
    s.set_source(local=True,path="/mnt/backup/")
    s.set_target(local=True,path="/mnt/archive/")
    self.s.do_sync()
    self.assertEqual(s.get_result().log,[
      ("init","fake_run=True"),
      ("shell","fake_run=True","rsync %s /mnt/backup/ /mnt/archive/" % STD_PARAMS),
    ])
   

  def disabled_testSeremitX(self):
    s=self.s
    s.set_source(local=False,user="seremit",host="remote.example.com",path="/mnt/backup/src1/")
    s.set_target(local=True,path="/mnt/archive/example-com/")
    self.s.do_sync()
    print self.s.get_result()
      
    self.s = s
    self.assertTrue(True)

  ######## setUp and tearDown ########

  def setUp(self):
    s = seremit.Seremit(syslog_tag="SEREMIT-TESTING",fake_run=True) 
    # seremit will log to local syslog with this tag
    # fake_run will not do any syncing but only log to syslog and result log  
    self.s = s
  
  def tearDown(self):
    pass     

## run the tests:  
  
if __name__ == "__main__":
    unittest.main()
