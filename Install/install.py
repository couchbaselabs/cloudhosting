
import sys

import os

import os.path
import subprocess

from couchbase import Couchbase

import ConfigParser
PATH = '/tmp/test.ini'

cb = Couchbase.connect (bucket = "default", host = "localhost")

def handleNewDeployment(result,depReq):            
        substr = "Can't establish SSH session"
        op = "Can't establish SSH session"
        print op.find(substr)
        
        while  op.find(substr) != -1 :
             p2 = subprocess.Popen(r'sudo -s python scripts/install.py -i {0} -p product=cb,version=3.0.0-1156-rel'.format(result['testmkfile']),
                          cwd = r'/auth/testrunner', shell =True, stdout = subprocess.PIPE)

             output = p2.communicate()[0]
             print "Pisu"
             print output
             op = "{0}".format(output)
             print op
             p2.wait()
           
        result['status'] = 'IN'
        cb.set(depReq,result)
        
        username = result['username']
        depname = result['depname']
        
        getVal = cb.get("user::{0}".format(username)).value
        
        vm = []
        tempip=''
        for iter in getVal['deploy']:
            if iter['request']['depname'] == depname:
                vm = iter['vm']
                break
                
         
        tempip = vm[0]['ip']
        ip = "{0}:8091".format(tempip)       
                
        cpu = int(result['cpus']) - 1 
        
        count = 0
        
        for v in vm:
            if result['provider'] == "GCE":
                cmd = 'sudo ./couchbase-cli rebalance -c {0} --server-add={1}  --server-add-username=Administrator   --server-add-password=password   -u Administrator -p password'.format(ip,v['pip'])
            else:
               cmd = 'sudo ./couchbase-cli rebalance -c {0} --server-add={1}  --server-add-username=Administrator   --server-add-password=password   -u Administrator -p password'.format(ip,v['dns']) 
            
            if count > 0:
                p4 = subprocess.Popen(r'{0}'.format(cmd),
                              cwd = r'/root/opt/couchbase/bin', shell =True)
                p4.wait()
            count = count + 1
        
        print cmd
        cmd = "sudo ./couchbase-cli cluster-edit -c {0} --cluster-ramsize={1} -u Administrator -p password".format(ip,result['ramquota'])
        p5 = subprocess.Popen(r'{0}'.format(cmd),cwd =r'/root/opt/couchbase/bin', shell =True)
        p5.wait()
        
        '''
        
        if result['bucketname'] == "default":
            port = 11211
        else:
            port = 11224 
        #cmd = "sudo python testrunner.py -i /tmp/test.ini -t clitest.couchbase_clitest.CouchbaseCliTest.testBucketCreation  -p bucket={0},bucket_type=couchbase,bucket_port=11222,bucket_replica={1},bucket_ramsize={2},skip_cleanup=True".format(result['bucketname'], result['replica'], result['bucket_size'])
        cmd = "sudo ./couchbase-cli bucket-create -c {0}  --bucket={1}  --bucket-type=couchbase --bucket-port={2} --bucket-ramsize={3} --bucket-replica={4} --bucket-priority=low --wait -u Administrator -p password ".format(ip,
                                                                                                                                                                    result['bucketname'], port,result['bucket_size'], result['replica'])        
        p6 = subprocess.Popen(r'{0}'.format(cmd),cwd =r'/root/opt/couchbase/bin', shell =True)
        p6.wait()
         ''' 
        result['status'] = 'F'
        cb.set(depReq,result)


def handleNewInstance(result, depReq):
    substr = "Can't establish SSH session"
    op = "Can't establish SSH session"
    print op.find(substr)
    
    while  op.find(substr) != -1 :
         p2 = subprocess.Popen(r'sudo -s python scripts/install.py -i {0} -p product=cb,version=3.0.0-966-rel,amazon=true'.format(result['testmkfile']),
                      cwd = r'/auth/testrunner', shell =True, stdout = subprocess.PIPE)

         output = p2.communicate()[0]
         print "Pisu"
         print output
         op = "{0}".format(output)
         print op
         p2.wait()
       
    result['status'] = 'IN'
    cb.set(depReq,result)
    
    dns = result['vmprimary']['dns']
    
    
    username = result['username']
    depname = result['depname']
    
    depIndex = result['deploymentIndex']
    
    res = cb.get("user::{0}".format(username)).value
    
    vms = res['deploy'][depIndex]['newvm']
    
    
    for vm in vms:
        if (vm ['dns'] != dns):
            
            if  result['provider'] != "GCE":
                cmd='sudo ./couchbase-cli server-add -c {0}  --server-add={1}  --server-add-username=Administrator   --server-add-password=password   -u Administrator -p password'.format(dns,vm['dns'])
                print cmd
                p4 = subprocess.Popen(r'sudo ./couchbase-cli server-add -c {0}  --server-add={1}  --server-add-username=Administrator   --server-add-password=password   -u Administrator -p password'.format(dns,vm['dns']),
                                  cwd = r'/root/opt/couchbase/bin', shell =True)
            else:
                dn = "{0}:8091".format(dns)
                cmd='sudo ./couchbase-cli server-add -c {0}  --server-add={1}  --server-add-username=Administrator   --server-add-password=password   -u Administrator -p password'.format(dn,vm['pip'])
                print cmd
                p4 = subprocess.Popen(r'sudo ./couchbase-cli server-add -c {0}  --server-add={1}  --server-add-username=Administrator   --server-add-password=password   -u Administrator -p password'.format(dns,vm['pip']),
                                  cwd = r'/root/opt/couchbase/bin', shell =True)
            p4.wait()
     
    if  result['provider'] == "AWS":
            
            p4 = subprocess.Popen(r'sudo ./couchbase-cli rebalance -c {0}  -u Administrator -p password'.format(dns),
                              cwd = r'/root/opt/couchbase/bin', shell =True)
    else:
            dn = "{0}:8091".format(dns)
           
            p4 = subprocess.Popen(r'sudo ./couchbase-cli rebalance -c {0}     -u Administrator -p password'.format(dns),
                              cwd = r'/root/opt/couchbase/bin', shell =True)       
    result['status'] = 'F'
    cb.set(depReq,result)
            
#def handleRemoveNode(result):
    
    
      
#def handleBucketCreate(result):
    
    
def main(argv):
     
    depReq = "{0}".format(argv[0])       
   
    result = cb.get(depReq).value
   
    
    if result['status'] == "IHDE":  
        result['status'] = "INUSERDE"  
        cb.set(depReq, result)    
        handleNewDeployment(result,depReq)
       
    elif result['status'] == "IHAD":
        result['status'] = "INUSERAD"  
        cb.set(depReq, result)
        handleNewInstance(result,depReq)
        
        
    ''''    
    elif result['status'] == "IHRM":
        handleRemoveNode(result)
    else : 
        result['status'] == "IHBC"
        handleBucketCreate(result)
        '''
                
if __name__ == "__main__":
    main(sys.argv[1:])