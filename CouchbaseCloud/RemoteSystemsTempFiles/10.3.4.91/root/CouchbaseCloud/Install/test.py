from couchbase import Couchbase
import time

import sys
import subprocess

def main(argv):
    
    cb = Couchbase.connect (bucket = 'default', host ="localhost")
    
    while True:
        rows = cb.query("dev_CB","status",stale="false")
        
        for row in rows:
           if row.key == "RDDE":
               p1 = subprocess.Popen(r'sudo python InstanceHadler.py {0}'.format(row.docid),
                                  cwd = r'/root/opt/couchbase/bin', shell =True)
               p2 = subprocess.Popen(r'sudo python InstanceHadler.py {0}'.format(row.docid),
                                  cwd = r'/root/opt/couchbase/bin', shell =True)
               
                  
        result['status'] = "DDE"
        cb.set("DeploymentRequest",result) 
    
if __name__ == "__main__":
   main(sys.argv[1:])
