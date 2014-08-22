


import os

import os.path
import subprocess

from couchbase import Couchbase

PATH = '/tmp/test.ini'


while True:
    
    if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
        
        p1 = subprocess.Popen (r'sudo mv /tmp/test.ini /tmp/test_processing.ini', shell =True)
        
        p1.wait()
        
        cb = Couchbase.connect (bucket = "default", host = "localhost")
        
        
        
        substr = "Can't establish SSH session"
        op = "Can't establish SSH session"
        print op.find(substr)
        while  op.find(substr) != -1 :
             p2 = subprocess.Popen(r'sudo -s python scripts/install.py -i /tmp/test_processing.ini -p product=cb,version=3.0.0-966-rel,amazon=true',
                          cwd = r'/auth/testrunner', shell =True, stdout = subprocess.PIPE)

             output = p2.communicate()[0]
             print "Pisu"
             print output
             op = "{0}".format(output)
             print op
             p2.wait()
             
        obj = {}
        
        obj['filename'] = 'test.ini'
        obj['status'] = 'PU'
        cb.set("requesttable",obj)
        
        p3 = subprocess.Popen (r'sudo mv /tmp/test_processing.ini /tmp/test_processed.ini', shell =True)
        p3.wait()

        cmd = "python testrunner.py  -i /tmp/test_processed.ini -t rebalance.rebalancein.RebalanceInTests.rebalance_in_after_ops -p nodes_in=1,nodes_init=3,replicas=1,items=100000"
        p4 = subprocess.Popen(r'sudo python testrunner.py  -i /tmp/test_processed.ini -t rebalance.rebalancein.RebalanceInTests.rebalance_in_after_ops -p nodes_in=1,nodes_init=3,replicas=1,items=100000',
                              cwd = r'/auth/testrunner', shell =True)
        p4.wait()
        
        obj['filename'] = 'test.ini'
        obj['status'] = 'CO'
        cb.set("requesttable",obj)
        
