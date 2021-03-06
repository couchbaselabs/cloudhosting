from azure import *
from azure.servicemanagement import *
import base64
import os

import time
import datetime

def timestamp():
   now = time.time()
   localtime = time.localtime(now)
   milliseconds = '%03d' % int((now - int(now)) * 1000)
   return time.strftime('%Y%m%d%H%M%S', localtime) + milliseconds

def _wait_for_async(sms,request_id):
    count = 0
    result = sms.get_operation_status(request_id)
    while result.status == 'InProgress':
        count = count + 1
        time.sleep(5)
        result = sms.get_operation_status(request_id)
    
    
def _wait_for_deployment(sms,service_name, deployment_name,status='Running'):
    count = 0
    props = sms.get_deployment_by_name(service_name, deployment_name)
    while props.status != status:
        count = count + 1
        time.sleep(5)
        props = sms.get_deployment_by_name(service_name, deployment_name)
        
def _wait_for_role(sms,service_name, deployment_name, role_instance_name,status='ReadyRole'):
    count = 0
    props = sms.get_deployment_by_name(service_name, deployment_name)
    while _get_role_instance_status(props, role_instance_name) != status:
        count = count + 1
        props = sms.get_deployment_by_name(service_name, deployment_name)

def _get_role_instance_status(deployment, role_instance_name):
    for role_instance in deployment.role_instance_list:
        if role_instance.instance_name == role_instance_name:
            return role_instance.instance_status
    return None

def AzureHandler(request):
    
    subscription_id = request['subid']
    certificate_path = '/tmp/azurekey'
    
    sms = ServiceManagementService(subscription_id, certificate_path)

    image_name='5112500ae3b842c8b9c604889f8753c3__OpenLogic-CentOS-65-20140606'
    
    
    
    tm = timestamp()
    name = "{0}".format(request['depname']) + "{0}".format(tm)
    label = name
    desc = name
    location = request['loc']
    
    sms.create_hosted_service(name, label, desc, location)

    i = datetime.datetime.now()
    dateVar = '{0}-{1}-{2}'.format(i.year, i.month, i.day)
    media_link = 'https://portalvhdsmtcz83fp9vjrb.blob.core.windows.net/vhds/'+ name + '-' + name + '-' +dateVar +'.vhd'
    
    
    
    location = request['loc']
    linux_user_id='azureuser'
    linux_config = LinuxConfigurationSet(name, 'azureuser',user_password=None,disable_ssh_password_authentication=True)
    
    
    azure_config = "/tmp" + '/.azure'
    cert_data_path = azure_config + "/myCert.pfx"
    with open(cert_data_path, "rb") as bfile:
        cert_data = base64.b64encode(bfile.read())
    
    cert_format = 'pfx'
    cert_password = ''
    cert_res = sms.add_service_certificate(service_name=name,
                                data=cert_data,
                                certificate_format=cert_format,
                                password=cert_password)
    
    vars(cert_res)
    time.sleep(60)
    
    
    azure_config = "/tmp" + '/.azure'
    thumbprint_path = azure_config + '/thumbprint'
    authorized_keys = "/home/" + linux_user_id + "/.ssh/authorized_keys" 
    try:
        thumbprint=open(thumbprint_path, 'r').readline().split('\n')[0]
    except:
        thumbprint=None
    
    
    publickey = PublicKey(thumbprint, authorized_keys)
    linux_config.ssh.public_keys.public_keys.append(publickey)
    
    print vars(publickey)
    print vars(linux_config.ssh.public_keys.public_keys.list_type)
    
    
    
    print vars(linux_config.ssh.public_keys)
    print vars(linux_config.ssh.key_pairs)
    
    os_hd  = OSVirtualHardDisk(image_name, media_link)
    
    print vars(os_hd)
    
    network = ConfigurationSet()
    network.configuration_set_type = 'NetworkConfiguration'
    network.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('ssh', 'tcp', '22', '22'))
    network.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('http', 'tcp','8091','8091'))
    '''
    portIndex = 0
    while portIndex <= 65535:
        network.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('http', 'tcp', "{0}".format(portIndex), 
                                                                                     '{0}'.format(portIndex)))
        portIndex = portIndex + 1
    '''
    result = sms.create_virtual_machine_deployment(service_name=name,
        deployment_name=name,
        deployment_slot='production',
        label=name,
        role_name=name,
        system_config=linux_config,
        network_config=network,
        os_virtual_hard_disk=os_hd,
        role_size='Large')
    
    request_id = result.request_id
    print request_id
    print result
    
    _wait_for_async(sms,result.request_id)
    _wait_for_deployment(sms,service_name=name, deployment_name=name)
    _wait_for_role(sms,service_name=name, deployment_name=name, role_instance_name=name)
        
    cpus = int(request['cpus']) - 1
    i=0 
    while i<cpus:
        print "Piush"
        tm = timestamp()
        rolename = "{0}".format(request['depname']) + "{0}".format(tm)
        linux_config = LinuxConfigurationSet(rolename, 'azureuser',user_password=None,disable_ssh_password_authentication=True)
        linux_config.ssh.public_keys.public_keys.append(publickey)
        
        media_link = 'https://portalvhdsmtcz83fp9vjrb.blob.core.windows.net/vhds/'+ name + '-' + rolename + '-' +dateVar +'.vhd'
        os_hd  = OSVirtualHardDisk(image_name, media_link)
        
        network=None
        result = sms.add_role(service_name=name, deployment_name=name, role_name=rolename,
                              system_config = linux_config, os_virtual_hard_disk=os_hd, network_config= network,
                              role_size = 'Large')
        request_id = result.request_id
        print request_id
        print result
        i = i+ 1
    
    print vars(linux_config.ssh.public_keys)
    print vars(linux_config.ssh.key_pairs)
    
    time.sleep (60)
    status = sms.get_operation_status(request_id)
    try:
        print vars(status.error)
    except:
        print vars(status)
    
    service_name = name
    deployment_name = name
    props = sms.get_deployment_by_name(service_name, deployment_name)
    vars(props)
    
    result = sms.list_locations()
    for location in result:
        print(location.name)
    

    deployment = sms.get_deployment_by_slot(name, 'production')

    for instance in deployment.role_instance_list:
        while instance.instance_status != "ReadyRole":
            continue
        print('Instance name: ' + instance.instance_name)
        print('Instance status: ' + instance.instance_status)
        print('Instance size: ' + instance.instance_size)
        print('Instance role name: ' + instance.role_name)
        print('Instance ip address: ' + instance.ip_address)
        print instance.__dict__
        print('')
        
    
        
    node = {
            'nodeid':None,
            'private_ip':None,
            'public_ip': None}
    
    return node
    
    
