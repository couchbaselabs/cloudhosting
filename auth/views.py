
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

import sys

import copy

from pprint import pprint

import time

def timestamp():
   now = time.time()
   localtime = time.localtime(now)
   milliseconds = '%03d' % int((now - int(now)) * 1000)
   return time.strftime('%Y%m%d%H%M%S', localtime) + milliseconds

@csrf_exempt  
def getRamSize(request):
    
    cb = Couchbase.connect(bucket="default", host = "localhost")
    
    result = cb.get("Machine").value
    try:
        store = result
        result = json.loads(result)
    except:
        result = store

    c = result[request.POST.get('provider')][request.POST.get('machine')]
    return HttpResponse(c)
    
@csrf_exempt  
def auth_user(request):
    state = "Please log in below..."
    
    cb= Couchbase.connect(bucket="default", host="localhost")
    diction = {"AWS":{'m3.large': '3584'}, "GCE":{"n1-highmem-4":'3584', "n1-highmem-8":'3584'},
               "RackSpace":{"8GB Standard Instance":'3584'}, "Azure" :{"Large" : '3584'}}
    cb.set ("Machine", diction )
    return render_to_response('auth.html',{'state':state})

@csrf_exempt
def login_user(request):
    state = "Please log in below..."
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    username = password = ''
    if request.POST:
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try :
            result = cb.get("user::{0}".format(username)).value
            print result
            
            try :
                store = result
                result = json.loads(result)  
            except:
                result = store
                  
            session = {}
        
            if (result['password1'] == password) :
                session['username'] = username
                sessionname = "SessionDetails::{0}".format(username)
                cb.set(sessionname,session)
                
                return render_to_response("deployments.html",{'result':result, 'username' : username})
            else :
                return render_to_response("auth.html",{'error':"IU", 'message':"Your username or password is invalid"})  
        except:
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
    
    session = {}
    
    sessionname = "SessionDetails::{0}".format(uname)    
    session['username'] = uname
    cb.set(sessionname,session)
    
    value = {'username' : uname, 
             'password1':password,  
             'accountName':accountname,
             'email' :email,
             'deploy':None}
    
    print value['username']
    
    cb.set("user::{0}".format(uname),json.dumps(value))
                                              
    
    result = cb.get("user::{0}".format(uname)).value
    print result
    return render_to_response('deployments.html', {'result' :result, 'username':uname})

@csrf_exempt
def handleProgress(request):
    
    cb = Couchbase.connect(bucket="default", host="localhost")
    
    res = cb.get("SessionDetails::{0}".format(request.POST.get('username'))).value
    username = res['username']
    
    result = cb.get("user::{0}".format(username)).value
    return render_to_response('deployments.html',{'result':result, 'username':username})

@csrf_exempt
def couchdep(request) :
    
    postval = {'username':request.POST.get('hiduname')}
    return render_to_response('couchdbdep.html', {'postval':postval})

def convert_node_ip_string(st):
        a = "{0}".format(st)
        a = a.replace('[', '')
        a = a.replace('\'','')
        a = a.replace(']','')
        return a
        
        
def save_dep_GCE(storeReq,request):
    
    testFile = request.FILES['permission']
    textf = testFile.read()
    
    fp = open('/tmp/PRIV.pem','w')    
    fp.write(textf)
    fp.close()
        

@csrf_exempt
def save_deployment(request):
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    result = cb.get("SessionDetails::{0}".format(request.POST.get('hiduname'))).value
    
    if (result != None):
        username = result['username']
    
    result['deploymentname'] = request.POST.get('depname')
    
    
    cb.set("SessionDetails::{0}".format(username),result)
   
    provider = request.POST.get('provider')
    
    'Use the parameters in the request for creating instances'
    
    if provider == "AWS":
        storeReq = copy.deepcopy(request.POST)
        key = request.FILES['keyfile'] 
        fp = open("/tmp/piushs.pem", 'w')
        fp.write(key.read())
        fp.close()
        
    if provider == "GCE":
        storeReq = copy.deepcopy(request.POST)
        save_dep_GCE(storeReq, request)
        
    if provider == "RackSpace":
        storeReq = copy.deepcopy(request.POST)
        key = request.FILES['prkeyfile'] 
        fp = open("/tmp/rackspacepk", 'w')
        fp.write(key.read())
        fp.close()
        
    if provider == "Azure":
        storeReq = copy.deepcopy(request.POST)
        key = request.FILES['certificate'] 
        fp = open("/tmp/azurekey", 'w')
        fp.write(key.read())
        fp.close()
    
    storeReq['status'] = "WA"
    storeReq['username'] = username
    
    depDoc = "DeploymentRequest::{0}::{1}".format(username, timestamp())
    cb.set("{0}".format(depDoc),storeReq)
    
    result['depDoc'] = depDoc
    cb.set("SessionDetails::{0}".format(username),result)
    
    test = cb.set(depDoc, storeReq)
    
    
    return render_to_response("couchbaseconfiguration.html",{'provider':storeReq['provider'],
                                                             'machine':storeReq['machine'], 'cpus':storeReq['cpus'], 
                                                             'username':username})

@csrf_exempt
def mngcluster(request):
    
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    var = "SessionDetails::{0}".format (request.POST.get('hiduname'))
    result = cb.get (var).value

    result['deploymentname'] = request.POST.get('deplist')
    
    cb.set("SessionDetails::{0}".format(request.POST.get('hiduname')), result)
    
    username = result['username']
    
    result = cb.get("user::{0}".format(username)).value
    dep = request.POST.get('deplist')
    
    print result
    
    
    temp ={}
    
    try :
        store = result
        result = json.loads(result)
    except:
        result = store
   
    if result ['deploy'] != None :     
        for res in result['deploy'] :
            if res['request']['depname'] == dep:
                temp = res
                break

    if bool(temp):
        return render_to_response("managecluster.html", {'temp':temp, 'username': username})
    else:
        return render_to_response("deployments.html", {'username':username})

@csrf_exempt
def conf_couchbase(request):

    print "Coming Here"
    return render_to_response("couchbaseconfiguration.html",None)
    
@csrf_exempt
def install(request):
    
    cb = Couchbase.connect (bucket='default', host="localhost")
    
    val = cb.get("SessionDetails::{0}".format(request.POST.get('hiduname'))).value
    
    store = cb.get(val['depDoc']).value
    
    store['bucketname'] = request.POST.get('bkname')
    store['operation'] = request.POST.get('operation')
    store['replica'] = request.POST.get ('numrep')
    store['password_sasl'] = request.POST.get('rdpasswd')
    store['bucket_size'] = request.POST.get('size')
    store['ramquota'] = request.POST.get('ramquota')
    
    
    store['status'] = 'RDDE'
    cb.set (val['depDoc'], store)
    
    cpu = store['cpus']
    return render_to_response("progress.html",{'cpu':cpu, 'uname' : request.POST.get('hiduname') })

@csrf_exempt
def mngviewDel(request):

    
    bucket = request.POST.get("bucket")
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    resultsess = cb.get("SessionDetails::{0}".format(request.POST.get('hiduname'))).value
    username = resultsess['username']
    dep = resultsess['deploymentname']
    
    result = cb.get("user::{0}".format(username)).value
    
    print result

    
    deploymentIndex = 0;

    temp ={}
    for res in result['deploy'] :
        if res['request']['depname'] == dep:
            temp = res['request']
            break
        deploymentIndex = deploymentIndex + 1
    
    

    machines = request.POST.getlist('ck')

    
    vms = result['deploy'][deploymentIndex]['vm']    
     
    flag = 0
    primarydns = ''
    for vm in vms:
        for mc in machines:
            if vm['dns'] != mc:
                flag = 1
                primarydns = vm['dns']
                break
        if flag == 1:
            break
        
    machineInfo=[]
    for vm in vms:
        for mc in machines:
            if vm['dns'] == mc:
                machineInfo.append(vm)
                break
        
    delReq = result['deploy'][deploymentIndex]['request']
    delReq['deploymentIndex'] = deploymentIndex
    delReq['vmprimary'] = primarydns
    delReq['status'] = "RDDEL"
    delReq['delmachines'] = machineInfo
    
    depReq = "DeploymentRequest::{0}::{1}".format(username, timestamp())
    cb.set(depReq, delReq)
    
    result = cb.get("user::{0}".format(username)).value
    
    ret = cb.get(depReq).value
    
    while ret['status'] != "IHDEL":
        ret = cb.get(depReq).value
        continue
    
    return render_to_response("deployments.html", {'result':result, 'username':username})
    
    
@csrf_exempt
def mngviewAdd(request):
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    resultsess = cb.get("SessionDetails::{0}".format(request.POST.get('hiduname'))).value
    username = resultsess['username']
    dep = resultsess['deploymentname']
    
    
    result = cb.get("user::{0}".format(username)).value
    
    print result
  
    deploymentIndex = 0;

    temp ={}
    for res in result['deploy'] :
        if res['request']['depname'] == dep:
            temp = res['request']
            break
        deploymentIndex = deploymentIndex + 1
    
    
    
    temp['status'] = 'RDAD'
    temp['cpus'] = request.POST.get('number')
    temp['deploymentIndex'] = deploymentIndex
    
    depDoc = "DeploymentRequest::{0}::{1}".format(username,timestamp())
    cb.set("{0}".format(depDoc),temp)
    
    resultsess['depDoc'] = depDoc
    cb.set ("SessionDetails::{0}".format(username), resultsess)
    cpu = request.POST.get('number')
    return render_to_response ("progress.html", {'cpu':cpu, 'uname':request.POST.get('hiduname')})


@csrf_exempt
def poll_state( request):
    
    pollcb=Couchbase.connect(bucket='default', host='localhost')
    
    stre = "SessionDetails::{0}".format(request.POST.get('username'))
    sess = pollcb.get(stre).value
    result = pollcb.get(sess['depDoc']).value
    
    c = result['status']
    
    c= json.dumps(c)
    
    return HttpResponse(c,mimetype='application/json')



@csrf_exempt
def poll_ins_state(request):
    
    pollcbconn=Couchbase.connect(bucket='default', host='localhost')
    
    result = pollcbconn.get("DeploymentRequest").value
    
    c = result['status']
    
    c= json.dumps(c)
    return HttpResponse(c,mimetype='application/json')

@csrf_exempt
def getDeployment(request):
    
    cb=Couchbase.connect(bucket='default', host='localhost')
    
    try:
        result = cb.get("user::{0}".format(request.POST.get('username'))).value
        store = result
        result = json.loads(result)
    except:
        result = store
    
    depname = request.POST.get('deplist')
    c = result['deploy']
    
    deploymentIndex =0 
    for res in result['deploy'] :
        if res['request']['depname'] == depname:
            temp = res['request']
            break
        deploymentIndex = deploymentIndex + 1
    
    temp = json.dumps(temp)
    return HttpResponse(temp,mimetype='application/json')

