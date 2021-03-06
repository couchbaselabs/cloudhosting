
# Create your views here.


from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import json

from couchbase import Couchbase
from couchbase import *

import subprocess
import os
import time

import ConfigParser
from time import sleep

import sys

import copy

from pprint import pprint

import az



def timestamp():
   now = time.time()
   localtime = time.localtime(now)
   milliseconds = '%03d' % int((now - int(now)) * 1000)
   return time.strftime('%Y%m%d%H%M%S', localtime) + milliseconds


def _create_node_AWS(request):
    location = request['loc']
        
    if  location == 'East':
        cls = get_driver(Provider.EC2_US_EAST)
        
    AWS_EC2_ACCESS_ID = request['ackey']
    AWS_EC2_SECRET_KEY = request['seckey']
    
    driver = cls(AWS_EC2_ACCESS_ID, AWS_EC2_SECRET_KEY)
    
    ACCESS_KEY_NAME = request['keyname']
    
    
    sizes = driver.list_sizes()
    
    for size in sizes:
        print size
    
    MY_SIZE = request['machine']
    MY_IMAGE = 'ami-76817c1e'
    
    
    size = [s for s in sizes if s.id == MY_SIZE][0]
    
    image = driver.get_image(MY_IMAGE)
    
    print image
    print size
    
    y = request['cpus']
    a=0
    
    n = int(y)
    nodes = list()
    while a < n :
        tm = timestamp()
        nodename = "{0}_".format(request['depname']) + "{0}".format(tm)
        node = driver.create_node(name=nodename, image=image, size=size, ex_keyname=ACCESS_KEY_NAME)
        nodes.append(node)
        a = a+1;  
    
    nodesup = list()    
    for node in nodes :
        while node.state != 0 :
            regionNodes = driver.list_nodes() 
            node = [val for val in regionNodes if val.id == node.id][0]
            continue
        nodesup.append(node)
    
    for node in nodesup:
        print node.__dict__
        
    return nodesup
        
def _create_node_GCE(request):
    
    Driver = get_driver(Provider.GCE)
    print request['email']
    print request['loc']
    print request['projid']
    
    
    gce = Driver('{0}'.format(request['email']), "./PRIV.pem",
                datacenter='{0}'.format(request['loc']),
    
    sizes = gce.list_sizes()

    for size in sizes:
            print size
            
    images = gce.list_images()

    for image in images:
        print image
        
    location = request['loc']
    
    fp = open("/tmp/id_rsa.pub", 'r')
    key = fp.read()
    fp.close()
    
    metadata = {'sshKeys': 'couchbase:%s' %key}
    y = request['cpus']
    a=0
    
    n = int(y)
    nodes = list()
    
    while a < n :
        tm = timestamp()
        nodename = "{0}".format(request['depname']) + "{0}".format(tm)
        node = gce.create_node(name=nodename, image='centos-6', size=request['machine'], ex_metadata= metadata)
        nodes.append(node)
        a = a+1;  
    
    nodesup = list()    
    for node in nodes :
        while node.state != 0 :
            regionNodes = gce.list_nodes() 
            node = [val for val in regionNodes if val.id == node.id][0]
            continue
        nodesup.append(node)
    
    for node in nodesup:
        print node.__dict__
     
    return nodesup

def _create_node_RackSpace(request):
    
    cls = get_driver(Provider.RACKSPACE)
    
    driver = cls(request['rkusername'],request['apikey'])
    
    pprint(driver.list_sizes())
    pprint(driver.list_nodes())

    images = driver.list_images()
    
    sizes = driver.list_sizes()

    for image in images:
       if image.id == "3a6e29eb-3e17-40ed-9f1e-c6c0fb8fcb76":
           os_image = image
           break
       
    y = request['cpus']
    a=0
    
    n = int(y)
    nodes = list()
    
    while a < n :
        tm = timestamp()
        nodename = "{0}".format(request['depname']) + "{0}".format(tm)
        node = driver.create_node(name=nodename, image=os_image, size=sizes[4], ex_keyname=request['keyname'])
        nodes.append(node)
        a = a+1;  
    
    nodesup = list()    
    for node in nodes :
        while node.state != 0 :
            regionNodes = driver.list_nodes() 
            node = [val for val in regionNodes if val.id == node.id][0]
            continue
        nodesup.append(node)
    
    for node in nodesup:
        print node.__dict__
       
    return nodesup

def create_instance(request):
    
    
    if request['provider'] == "AWS":
       nodes =  _create_node_AWS(request)
    elif request['provider'] == "GCE":
        nodes = _create_node_GCE(request)
    elif request['provider'] == "RackSpace":
        nodes = _create_node_RackSpace(request)
    elif request['provider'] == "Azure":
        nodes = az.AzureHandler(request)
    
    return nodes
    
def handleNewDeployment(request,cb,depReq):
    
    nodesup = create_instance(request)
    
    bucket =[]
    vms = []
    
    if (request['provider'] == "AWS"):
        for node in nodesup :
            vms.append({'ip' : convert_node_ip_string(node.public_ips), 'nodeid':node.id,
                        'dns': convert_node_ip_string(node.__dict__['extra']['dns_name'])})
    elif (request['provider'] == "GCE"):
        for node in nodesup :
            vms.append({'ip' : convert_node_ip_string(node.public_ips), 'nodeid':node.id,
                        'pip': convert_node_ip_string(node.private_ips), 'dns':convert_node_ip_string(node.public_ips)})  
    elif (request['provider'] == "RackSpace"):
        for node in nodesup :
            vms.append({'ip' : convert_node_ip_string(node.public_ips[0]), 'nodeid':node.id,
                        'pip': convert_node_ip_string(node.private_ips), 'dns':convert_node_ip_string(node.public_ips[0])}) 
            
    bucket.append ({ 'bucketname' : request['bucketname'], 'bucketsize':request['bucket_size']});
    
    result = cb.get("user::{0}".format(request['username'])).value
    
    print "hehhr" 
    print result
    
    
    try :
        store = result
        result = json.loads(result)
    except:
        result = store
    
    request['status'] = "IHDE"        
    
    if result['deploy'] == None:
        print "1"
        result['deploy'] = [{'request':request, 
                             'bucket': bucket,
                             'vm':vms}]
    else :
        print "2"
        result['deploy'].append({'request':request, 'bucket' : bucket, 'vm':vms})
    
    
    print result       
    
    cb.set(depReq,request)
    cb.set("user::{0}".format(request['username']), result)
    
    if (request['provider'] == "AWS"):
        aws_mkfile(nodesup,depReq)
    elif(request['provider'] == "GCE"):
        gce_mkfile(nodesup,depReq)
        gce_mkfile_cluster(nodesup,depReq)
    elif(request['provider'] == "RackSpace"):
        rackspace_mkfile(nodesup,depReq)

def handleNewInstances(request,cb,depReq):
    
    nodesup = create_instance(request)
    
    resultSession = cb.get("SessionDetails::{0}".format(request['username'])).value
    
    depIndex = request['deploymentIndex']
    
    result = cb.get("user::{0}".format(request['username'])).value
    
    try :
        store = result
        result = json.loads(result)
    except:
        result = store
    
    
    vms = result['deploy'][depIndex]['vm']
    
    newVM= []
    mainVm = vms[0]
    newVM.append(mainVm)
    
    for node in nodesup :
        if request['provider'] == "AWS":
            vms.append({'ip' : convert_node_ip_string(node.public_ips), 'nodeid':node.id,
                        'dns':node.__dict__['extra']['dns_name']})
            newVM.append({'ip' : convert_node_ip_string(node.public_ips), 'nodeid':node.id,
                        'dns':node.__dict__['extra']['dns_name']})
        elif request['provider'] == "GCE":
            vms.append({'ip' : convert_node_ip_string(node.public_ips), 'nodeid':node.id,
                        'dns':convert_node_ip_string(node.public_ips), 'pip':convert_node_ip_string(node.private_ips)})
            newVM.append({'ip' : convert_node_ip_string(node.public_ips), 'nodeid':node.id,
                        'dns':convert_node_ip_string(node.public_ips), 'pip':convert_node_ip_string(node.private_ips)})
        elif request['provider'] == "RackSpace":
            vms.append({'ip' : convert_node_ip_string(node.public_ips[0]), 'nodeid':node.id,
                        'dns':convert_node_ip_string(node.public_ips[0]), 'pip':convert_node_ip_string(node.private_ips)})
            newVM.append({'ip' : convert_node_ip_string(node.public_ips[0]), 'nodeid':node.id,
                        'dns':convert_node_ip_string(node.public_ips[0]), 'pip':convert_node_ip_string(node.private_ips)})
         
    
    result['deploy'][depIndex]['newvm'] = newVM   
    result['deploy'][depIndex]['vm'] = vms 
    cpu = result['deploy'][depIndex]['request']['cpus'] 
    result['deploy'][depIndex]['request']['cpus']  = int (cpu) +1 
    
    cb.set("user::{0}".format(request['username']),result)
    
    print result
    
    request["status"] = "IHAD"
    request['vmprimary'] = mainVm
    cb.set(depReq,request)
     
    if request['provider'] == "AWS":  
        aws_mkfile(nodesup,depReq)
    elif request['provider'] == "GCE":
        gce_mkfile(nodesup,depReq)
    else:
        rackspace_mkfile(nodesup,depReq)
    

def del_aws_ins(request, listIns):
    
    location = request['loc']
    
    if  location == 'East':
        cls = get_driver(Provider.EC2_US_EAST)
    
    AWS_EC2_ACCESS_ID = request['ackey']
    AWS_EC2_SECRET_KEY = request['seckey']
    
    driver = cls(AWS_EC2_ACCESS_ID, AWS_EC2_SECRET_KEY)
    
    ACCESS_KEY_NAME = request['keyname']
    
    
    sizes = driver.list_sizes()
    
    
    MY_SIZE = request['machine']
    MY_IMAGE = 'ami-76817c1e'
    
    
    size = [s for s in sizes if s.id == MY_SIZE][0]
    
    image = driver.get_image(MY_IMAGE)
    
    nodes = driver.list_nodes()
    
    for node in nodes :
        if (node.id in listIns):
            driver.destroy_node(node)
            
def del_inst(request, listIns):
    
    Driver = get_driver(Provider.GCE)
    print request['email']
    print request['loc']
    print request['projid']
    
    '''
    gce = Driver('{0}'.format(request['email']), "./PRIV.pem",
                datacenter='{0}'.format(request['loc']),
             project='{0}'.format(request['projid']))
    '''
    
    gce = Driver('265882800008-3blh6m3ocdfhkm6kl2ihhfsls0a44nd6@developer.gserviceaccount.com', './PRIV.pem',
             datacenter='us-central1-a',
             project='poised-resource-658')
    
    nodes = gce.list_nodes()
    
    for node in nodes :
        if (node.id in listIns):
            gce.destroy_node(node)
            
            
def del_inst_rackspace(request, listIns):
    
    cls = get_driver(Provider.RACKSPACE)



    driver = cls(request['rkusername'],request['apikey'])
    
    nodes = driver.list_nodes()
    
    for node in nodes :
        if (node.id in listIns):
            driver.destroy_node(node)
    

def delInstance(request,cb,depReq):
      
    machines = request['delmachines']
    
    listIns = []
    for mc in machines:
        listIns.append(mc['nodeid'])
        
    pvm = request['vmprimary']
    print "DEL"
    print listIns

     
    
    username = request['username']
    depname = request['depname']
    depIndex = request['deploymentIndex']
    
    result = cb.get("user::{0}".format(username)).value  
    
    a = 0;
    listDns = []
    listPip = []
    
    if (request['provider'] == "AWS"):
        for mc in machines:
            listDns.append(mc['dns'])
    else:
        for mc in machines:
            listPip.append(mc['pip'])
        
    
    
    print listDns
    newVM = []
    
    if (request['provider'] == "AWS"):
        for res in result['deploy'][depIndex]['vm']:
            if res['dns'] not in listDns:
                    newVM.append(res)
    else:
        for res in result['deploy'][depIndex]['vm']:
            if res['pip'] not in listPip:
                    newVM.append(res)
    
    result['deploy'][depIndex]['vm'] = newVM
    
    cb.set ('user::{0}'.format(username), result)
    cpu = result['deploy'][depIndex]['request']['cpus']
    result['deploy'][depIndex]['request']['cpus'] = int(cpu) - len(machines)
    
   
    
    if request['provider'] == "AWS":
        
        for res in listDns:
            cmd='sudo ./couchbase-cli rebalance -c {0}  --server-remove={1}  -u Administrator -p password'.format(pvm,res)
            p4 = subprocess.Popen(r'{0}'.format(cmd),
                                  cwd = r'/root/opt/couchbase/bin', shell =True)
            p4.wait()
        
        del_aws_ins(request, listIns)
    elif request['provider'] == "GCE":
        
        for res in listPip:
            cmd='sudo ./couchbase-cli rebalance -c {0}  --server-remove={1}  -u Administrator -p password'.format(pvm,res)
            p4 = subprocess.Popen(r'{0}'.format(cmd),
                                  cwd = r'/root/opt/couchbase/bin', shell =True)
            p4.wait()
            
        del_inst(request,listIns)
    else:
        
        for res in listPip:
            cmd='sudo ./couchbase-cli rebalance -c {0}  --server-remove={1}  -u Administrator -p password'.format(pvm,res)
            p4 = subprocess.Popen(r'{0}'.format(cmd),
                                  cwd = r'/root/opt/couchbase/bin', shell =True)
            p4.wait()
            
        del_inst_rackspace(request,listIns)
        
    request['status'] = "IHDEL"
    print result       
    cb.set(depReq, request)
    cb.set("user::{0}".format(username), result)
    
    
    
def main(argv):
    
    depReq = argv[0]
    cb = Couchbase.connect(bucket="default", host="localhost")

    
    request = cb.get(depReq).value
    
    
    if request['status'] == "RDDE":
        request['status'] = "INUSEDE"
        cb.set(depReq, request)
        handleNewDeployment(request,cb,depReq)  
    elif request['status'] == "RDAD": 
        request['status'] = "INUSEAD"   
        cb.set(depReq, request)
        handleNewInstances(request,cb,depReq)  
    elif request['status'] == "RDDEL":
        request['status'] = "INUSEDEL"
        cb.set(depReq, request)
        delInstance(request,cb,depReq)       
            

def convert_node_ip_string(st):
        a = "{0}".format(st)
        a = a.replace('[', '')
        a = a.replace('u\'', '')
        a = a.replace('\'','')
        a = a.replace(']','')
        return a
    

def aws_mkfile_add(vm, user, key):
    '''
    filekey = open("/tmp/piushs.pem".format(user), "w")
    filekey.write(key)
    filekey.close()
    '''
    file = "/tmp/test-{0}.ini".format(timestamp())
    cfgfile = open(file,'w')
    
    cb = Couchbase.connect(bucket = 'default', host = 'localhost')
    val = cb.get(depReq).value
    val['testmkfile'] = file
    cb.set(depReq, val)
    
    Config = ConfigParser.ConfigParser()
    
    Config.add_section('global')
    Config.set('global','username','ec2-user')
    Config.set('global','ssh_key', "/tmp/{0}.pem".format(user))
    Config.set('global','port', "8091")
    
    Config.add_section('servers')
    
    count = 1
    for v in vm:
        
        Config.set('servers', "{0}".format(count),"{0}".format(v['dns']))
        count = count +1
    
    Config.add_section('membase')
    Config.set('membase','rest_username',"Administrator")
    Config.set('membase','rest_password', "password")
    
    
    Config.write(cfgfile)
    cfgfile.close()

def gce_mkfile(nodesup, depReq):
   
    file = "/tmp/test-{0}.ini".format(timestamp())
    cfgfile = open(file,'w')
    
    
    cb = Couchbase.connect(bucket = 'default', host = 'localhost')
    val = cb.get(depReq).value
    val['testmkfile'] = file
    cb.set(depReq, val)
    
    Config = ConfigParser.ConfigParser()
    
    Config.add_section('global')
    Config.set('global','username','couchbase')
    Config.set('global','ssh_key', "/tmp/id_rsa")
    Config.set('global','port', "8091")
    
    Config.add_section('servers')
    
    count = 1
    for node in nodesup:
        a = convert_node_ip_string(node.public_ips)
        Config.set('servers', "{0}".format(count),"{0}".format(a))
        count = count +1
    
    Config.add_section('membase')  
    Config.set('membase','rest_username',"Administrator")
    Config.set('membase','rest_password', "password")
    
    
    Config.write(cfgfile)
    cfgfile.close()

def gce_mkfile_cluster(nodesup, depReq):
   
    file = "/tmp/test-{0}.ini".format(timestamp())
    cfgfile = open(file,'w')
    
    cb = Couchbase.connect(bucket = 'default', host = 'localhost')
    
    
    Config = ConfigParser.ConfigParser()
    
    Config.add_section('global')
    Config.set('global','username','user')
    Config.set('global','ssh_key', "/tmp/id_rsa")
    Config.set('global','port', "8091")
    
    Config.add_section('servers')
    
    count = 1
    for node in nodesup:
        if count == 1:
            a = convert_node_ip_string(node.public_ips)
            Config.set('servers', "{0}".format(count),"{0}".format(a))
        else:
            a = convert_node_ip_string(node.private_ips)
            Config.set('servers', "{0}".format(count),"{0}".format(a))
        count = count +1
    
    Config.add_section('membase')  
    Config.set('membase','rest_username',"Administrator")
    Config.set('membase','rest_password', "password")
    
    
    Config.write(cfgfile)
    cfgfile.close()

def aws_mkfile(nodesup,depReq):
    
    file = "/tmp/test-{0}.ini".format(timestamp())
    cfgfile = open(file,'w')
    
    cb = Couchbase.connect(bucket = 'default', host = 'localhost')
    val = cb.get(depReq).value
    val['testmkfile'] = file
    cb.set(depReq, val)
    
    Config = ConfigParser.ConfigParser()
    
    Config.add_section('global')
    Config.set('global','username','ec2-user')
    Config.set('global','ssh_key', "/tmp/piushs.pem")
    Config.set('global','port', "8091")
    
    Config.add_section('servers')
    
    count = 1
    for node in nodesup:
        a = convert_node_ip_string(node.public_ips)
        Config.set('servers', "{0}".format(count),"{0}".format(node.__dict__['extra']['dns_name']))
        count = count +1
    
    Config.add_section('membase')
    Config.set('membase','rest_username',"Administrator")
    Config.set('membase','rest_password', "password")
    
    
    Config.write(cfgfile)
    cfgfile.close()
    
    cfgfile = open("/tmp/testCluster.ini",'w')
    Config.write(cfgfile)
    cfgfile.close()


def rackspace_mkfile(nodesup,depReq):
    
    file = "/tmp/test-{0}.ini".format(timestamp())
    cb = Couchbase.connect(bucket = 'default', host = 'localhost')
    val = cb.get(depReq).value
    val['testmkfile'] = file
    cb.set(depReq, val)
    
    cfgfile = open(file,'w')
    
    Config = ConfigParser.ConfigParser()
    
    Config.add_section('global')
    Config.set('global','username','root')
    Config.set('global','ssh_key', "/tmp/rackspacepk")
    Config.set('global','port', "8091")
    
    Config.add_section('servers')
    
    count = 1
    for node in nodesup:
        a = convert_node_ip_string(node.public_ips[0])
        Config.set('servers', "{0}".format(count),"{0}".format(a))
        count = count +1
    
    Config.add_section('membase')
    Config.set('membase','rest_username',"Administrator")
    Config.set('membase','rest_password', "password")
    
    
    Config.write(cfgfile)
    cfgfile.close()
    
    cfgfile = open("/tmp/testCluster.ini",'w')
    Config.write(cfgfile)
    cfgfile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
