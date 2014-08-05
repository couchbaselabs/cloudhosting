
# Create your views here.

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import json

from couchbase import Couchbase
from couchbase import *

import subprocess
import os
from django.conf import settings

import ConfigParser
from time import sleep


@csrf_exempt  
def auth_user(request):
    state = "Please log in below..."
    return render_to_response('auth.html',{'state':state})

@csrf_exempt
def login_user(request):
    state = "Please log in below..."
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    username = password = ''
    if request.POST:
        '''
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
            return render_to_response("message.html",{'state':state, 'username': username})
            '''
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        result = cb.get("user::piushs").value
        
        result = json.loads(result)        
        
        if (result['password1'] == password) :
                request.session['username'] = username
                return render_to_response("deployments.html",{'result':result})
        else :
                return render_to_response("auth.html",{'error':"IU", 'message':"Your username or password is invalid"})            
 
@csrf_exempt
def register_user(request):
    return render_to_response('registration.html')

@csrf_exempt
def create_account(request):
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    uname = request.POST.get('username')
    password = request.POST.get('password')
    accountname = request.POST.get('accountName')
    email = request.POST.get('email')
    
    
    value = {'username' : uname, 
             'password1':password,  
             'accountName':accountname,
             'email' :email,
             'deploy':None}
    
    print value['username']
    
    cb.set("user::{0}".format(uname),json.dumps(value))
                                              
    
    result = cb.get("user::{0}".format(uname)).value
    return render_to_response('deployments.html', {'result' :result})

@csrf_exempt
def couchdep(request) :
    return render_to_response('couchdbdep.html')

def convert_node_ip_string(st):
        a = "{0}".format(st)
        a = a.replace('[', '')
        a = a.replace('\'','')
        a = a.replace(']','')
        return a
        
def aws_mkfile(nodesup):

    cfgfile = open("/tmp/test.ini",'w')
    
    Config = ConfigParser.ConfigParser()
    
    Config.add_section('global')
    Config.set('global','username','ec2-user')
    Config.set('global','ssh_key', "/Users/piush/Key/piushs.pem")
    Config.set('global','port', "8091")
    
    Config.add_section('servers')
    
    count = 1
    for node in nodesup:
        a = convert_node_ip_string(node.public_ips)
        Config.set('servers', "{0}".format(count),a)
        count = count +1
    
    Config.add_section('membase')
    Config.set('membase','rest_username',"Administrator")
    Config.set('membase','rest_password', "password")
    
    
    Config.write(cfgfile)
    cfgfile.close()
    

@csrf_exempt
def deploy(request):
    
    
    username = request.session['username']
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    
    result = cb.get("user::{0}".format(username)).value
    
    result = json.loads(result)

    depname = request.POST.get('depname')
    cpus = request.POST.get('cpus')
    provider = request.POST.get('provider')
    loc = request.POST.get('loc')
    mc = request.POST.get('machine')
    cbs = request.POST.get('machine')    
    
    
    
    
    location = request.POST.get("loc")
    
    if  location == 'East':
        cls = get_driver(Provider.EC2_US_EAST)
    
    AWS_EC2_ACCESS_ID = "AKIAIM32BEWJ4F2K2VGQ"
    AWS_EC2_SECRET_KEY = "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"
    
    driver = cls(AWS_EC2_ACCESS_ID, AWS_EC2_SECRET_KEY)
    
    ACCESS_KEY_NAME = 'piushs'
    
    
    sizes = driver.list_sizes()
    
    for size in sizes:
        print size
    
    MY_SIZE = 'm3.large'
    MY_IMAGE = 'ami-76817c1e'
    
    
    size = [s for s in sizes if s.id == MY_SIZE][0]
    
    image = driver.get_image(MY_IMAGE)
    
    print image
    print size
    
    y = request.POST.get("cpus")
    a=0
    
    n = int(y)
    nodes = list()
    while a < n :
        node = driver.create_node(name="Test{0}".format(a), image=image, size=size, ex_keyname=ACCESS_KEY_NAME)
        nodes.append(node)
        a = a+1;
    
    nodesup = list()    
    for node in nodes :
        while node.state != 0 :
            regionNodes = driver.list_nodes() 
            node = [val for val in regionNodes if val.id == node.id][0]
            continue
        nodesup.append(node)
    
    
    bucket =[]
    vms = []
    
    for node in nodesup :
        vms.append({'ip' : convert_node_ip_string(node.public_ips), 'nodeid':node.id})
        
    bucket.append ({ 'name' : "default", 'vm':vms });
    
    print "hehhr" 
    print result

    if result['deploy'] == None:
        print "1"
        result['deploy'] = [{'name':depname,'Provider':provider,'cpu': cpus,'cbi':cbs, 'loc':loc, 'mc':mc, 'bucket': bucket}]
    else :
        print "2"
        result['deploy'].append({'name':depname,'Provider':provider,'cpu': cpus,'cbi':cbs, 'loc':loc, 'mc':mc, 'bucket' : bucket})
    
    
    print result       
    cb.set("user::{0}".format(username), result)
       
    aws_mkfile(nodesup)
   
    path = os.getcwd() 
    print path
    os.chdir(path + "/auth/testrunner")
    os.system('pwd')
    
    substr = "Can't establish SSH session"
    op = "Can't establish SSH session"
    print op.find(substr)
    while  op.find(substr) != -1 :
        
        var = os.popen('python scripts/install.py -i /tmp/test.ini -p product=cb,version=3.0.0-966-rel,amazon=true').read()
    
        op = "{0}".format(var)
        print "Piush"
        print op
        print op.find(substr)
    
    os.chdir(path)
    
    
    return render_to_response("managecluster.html", {'bucket' : bucket})

@csrf_exempt
def mngcluster(request):
    
    request.session['deploymentname'] = request.POST.get('deplist')
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    username = request.session['username']
    
    result = cb.get("user::{0}".format(username)).value
    
    print result
    dep = request.POST.get('deplist')
    print dep
   # result = json.loads(result)
    
    print result['deploy'][0]
    temp ={}
    for res in result['deploy'] :
        if res['name'] == dep:
            temp = res
            break
    
    return render_to_response("managecluster.html", {'bucket':temp['bucket']})


@csrf_exempt
def mngviewDel(request):

    username = request.session['username']
    dep = request.session ['deploymentname']
    bucket = request.POST.get("bucket")
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    
    result = cb.get("user::{0}".format(username)).value
    
    print result

    
    deploymentIndex = 0;

    temp ={}
    for res in result['deploy'] :
        if res['name'] == dep:
            temp = res
            break
        deploymentIndex = deploymentIndex + 1
    
    tempbucket= {}
    bucketIndex = 0
    for res in temp['bucket'] :
        if res['name'] == bucket:
            tempbucket = res
            break
        bucketIndex = bucketIndex + 1
    
    
    location = temp['loc']
    
    if  location == 'East':
        cls = get_driver(Provider.EC2_US_EAST)
    
    AWS_EC2_ACCESS_ID = "AKIAIM32BEWJ4F2K2VGQ"
    AWS_EC2_SECRET_KEY = "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"
    
    driver = cls(AWS_EC2_ACCESS_ID, AWS_EC2_SECRET_KEY)
    
    ACCESS_KEY_NAME = 'piushs'
    
    
    sizes = driver.list_sizes()
    
    for size in sizes:
        print size
    
    MY_SIZE = 'm3.large'
    MY_IMAGE = 'ami-76817c1e'
    
    
    size = [s for s in sizes if s.id == MY_SIZE][0]
    
    image = driver.get_image(MY_IMAGE)
    
    nodes = driver.list_nodes()
    
    print image
    print size
    
    y = request.POST.get("number")
    a=0
    
    n = int(y);
    
    listId = list()
    for res in result['deploy'][deploymentIndex]['bucket'][bucketIndex]['vm'] : 
        if (a < n):
            listId.append(res['nodeid'])
            del result['deploy'][deploymentIndex]['bucket'][bucketIndex]['vm'][a]
        else:
            break
        a= a+1
    
    print list
    
    for node in nodes :
        if (node.id in listId):
            driver.destroy_node(node)
                
    
    nodes = driver.list_nodes()
    
    print result       
    cb.set("user::{0}".format(username), result)
       
    return HttpResponse("Operation Successful")
    
    
@csrf_exempt
def mngviewAdd(request):
    

    username = request.session['username']
    dep = request.session ['deploymentname']
    bucket = request.POST.get("bucket")
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    
    result = cb.get("user::{0}".format(username)).value
    
    print result

    
    deploymentIndex = 0;

    temp ={}
    for res in result['deploy'] :
        if res['name'] == dep:
            temp = res
            break
        deploymentIndex = deploymentIndex + 1
    
    tempbucket= {}
    bucketIndex = 0
    for res in temp['bucket'] :
        if res['name'] == bucket:
            tempbucket = res
            break
        bucketIndex = bucketIndex + 1
    
    
    location = temp['loc']
    
    if  location == 'East':
        cls = get_driver(Provider.EC2_US_EAST)
    
    AWS_EC2_ACCESS_ID = "AKIAIM32BEWJ4F2K2VGQ"
    AWS_EC2_SECRET_KEY = "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"
    
    driver = cls(AWS_EC2_ACCESS_ID, AWS_EC2_SECRET_KEY)
    
    ACCESS_KEY_NAME = 'piushs'
    
    
    sizes = driver.list_sizes()
    
    for size in sizes:
        print size
    
    MY_SIZE = 'm3.large'
    MY_IMAGE = 'ami-76817c1e'
    
    
    size = [s for s in sizes if s.id == MY_SIZE][0]
    
    image = driver.get_image(MY_IMAGE)
    
    print image
    print size
    
    y = request.POST.get("number")
    a=0
    
    n = int(y)
    nodes = list()
    while a < n :
        node = driver.create_node(name="Test{0}".format(a), image=image, size=size, ex_keyname=ACCESS_KEY_NAME)
        nodes.append(node)
        a = a+1;
    
    nodesup = list()    
    for node in nodes :
        while node.state != 0 :
            regionNodes = driver.list_nodes() 
            node = [val for val in regionNodes if val.id == node.id][0]
            continue
        nodesup.append(node)
    
    vms = tempbucket['vm']
    
    for node in nodesup :
        vms.append({'ip' : convert_node_ip_string(node.public_ips), 'nodeid':node.id})
        
    result['deploy'][deploymentIndex]['bucket'][bucketIndex]['vm'] = vms
    
        
    print result       
    cb.set("user::{0}".format(username), result)
       
    aws_mkfile(nodesup)
   
    #sleep (120) 
    path = os.getcwd() 
    print path
    os.chdir(path + "/auth/testrunner")
    os.system('pwd')
    
    substr = "Can't establish SSH session"
    op = "Can't establish SSH session"
    
    print op.find(substr)
    while  op.find(substr) != -1 :
        
        var = os.popen('python scripts/install.py -i /tmp/test.ini -p product=cb,version=3.0.0-966-rel,amazon=true').read()
    
        op = "{0}".format(var)
        print "Piush"
        print op
        print op.find(substr)
        
    os.chdir(path)
    
    
    return HttpResponse ("Action Successful")
