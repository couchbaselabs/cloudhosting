from couchbase import Couchbase
import time

import sys
import subprocess

def main(argv):
    
    
    
    cb = Couchbase.connect (bucket = 'default', host ="localhost")
    while True:
           
        rows = cb.query("dev_CB","status",stale="false", limit =5)
        
        for row in rows:
        
           print row.key 
           if row.key == "RDDE" or row.key == "RDAD" or row.key == "RDDEL":
                print row.docid
                p1 = subprocess.Popen(r'sudo python InstanceHadler.py {0}'.format(row.docid),
                                  cwd = r'/Users/piush/Desktop/CouchbaseCloud/Install', shell =True)
                p1.wait()
           if row.key == "IHDE" or row.key == "IHAD":
                print row.key
                p2 = subprocess.Popen(r'sudo python install.py {0}'.format(row.docid),
                                  cwd = r'/Users/piush/Desktop/CouchbaseCloud/Install', shell =True)
                p2.wait()
               
           
    
    
if __name__ == "__main__":
   main(sys.argv[1:])
