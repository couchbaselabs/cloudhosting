
This software uses the Apache Libcloud Library (Python), Apache Web Server, Django (Python framework) for web development

Installation : 
pip install apache-libcloud

The Library provides an interface to interact with the API’s of the respective cloud providers
This software currently supports Rackspace, Google Cloud and AWS

We use the library for getting authenticated to the cloud providers, create instances and delete the instances

Libcloud acts as a lowest common denominator and exposes a unified base API which allows you to work with many different cloud providers through a single code base.

Being a lowest common denominator by definition means that not all of the functionality offered by different cloud service providers is available through a base API.

Libcloud solves this problem and allows user to access provider specific functionality through a so called extension methods and arguments. Extension methods and arguments are all the methods and arguments which are prefixed with ex_.

Extension methods are there for your convenience, but you should be careful when you use them because they make switching or working with multiple providers harder.

========================================================================================
The library has a driver for each of the cloud providers and if you need to add a new cloud provider in future 
you simply have to check whether it is supported in Libcloud in order to integrate it into this software

The compute component of libcloud allows you to manage cloud and virtual servers offered by different providers, more than 20 in total.

In addition to managing the servers this component also allows you to run deployment scripts on newly created servers. Deployment or “bootstrap” scripts allow you to execute arbitrary shell commands.
This functionality is usually used to prepare your freshly created server, install your SSH key, and run a configuration management tool (such as Puppet, Chef, or cfengine) on it.

Besides managing cloud and virtual servers, compute component also allows you to manage cloud block storage (not to be confused with cloud object storage) for providers which support it. Block storage management is lives under compute API, because it is in most cases tightly coupled with compute resources.

Terminology
Compute

    Node - represents a cloud or virtual server.
    NodeSize - represents node hardware configuration. Usually this is amount of the available RAM, bandwidth, CPU speed and disk size. Most of the drivers also expose an hourly price (in dollars) for the Node of this size.
    NodeImage - represents an operating system image.
    NodeLocation - represents a physical location where a server can be.
    NodeState - represents a node state. Standard states are: running, stopped, rebooting, terminated, pending, and unknown.

=====================================================================================
Companies using Libcloud

Companies and Organizations

Name: Rackspace
Website: http://www.rackspace.com/

Name: SixSq
Website: http://sixsq.com/

Name: CloudControl
Website: https://www.cloudcontrol.com/

Name: mist.io
Website: https://mist.io

Name: Cloudkick
Website: https://www.cloudkick.com
Reference: Announcing libcloud

Name: GlobalRoute
Website: http://globalroute.net/

Name: Server Density
Website: http://www.serverdensity.com/
Reference: Using vCloud and Amazon CloudWatch with libcloud

Name: CollabNet
Website: http://www.collab.net/
Reference: CollabNet Automates Build, Test And DevOps In The Cloud With New Version Of CollabNet Lab Management

Name: Salt Stack
Website: http://saltstack.com/

Name: Monash eScience and Grid Engineering Laboratory
Website: http://www.messagelab.monash.edu.au

Name: Scalr
Website: http://www.scalr.com/

Name: DivvyCloud
Website: http://www.divvycloud.com/

============================================================================================


How do I obtain Libcloud version?

You can obtain currently active Libcloud version by accessing the libcloud.__version__ variable.

Example #1 (command line):

python -c "import libcloud ; print libcloud.__version__"

Example #2 (code):

import libcloud
libcloud.__version__

======================================================================================

Upgrading

If you used pip to install the library you can also use it to upgrade it:

pip install --upgrade apache-libcloud

=====================================================================================

Using it

This section describes a standard work-flow which you follow when working with any of the Libcloud drivers.

    Obtain reference to the provider driver

from pprint import pprint

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

cls = get_driver(Provider.RACKSPACE)

    Instantiate the driver with your provider credentials

driver = cls('my username', 'my api key')

==================================================================================
=====================================================================================

Deployment

1. Set up the Apache Web Server on the machine you want to deploy
2. Update the httpd.conf with the directory of the project

example
<VirtualHost *:80>
     ServerName cen-1627.hq.couchbase.com
     WSGIScriptAlias / /home/ec2-user/CouchbaseCloud/CouchbaseCloud/CouchbaseCloud/wsgi.py
     ErrorLog /home/ec2-user/CouchbaseCloud/CouchbaseCloud/logs/apache_error.log
     CustomLog /home/ec2-user/CouchbaseCloud/CouchbaseCloud/logs/apache_access.log combined

     <Directory /home/ec2-user/CouchbaseCloud/CouchbaseCloud/CouchbaseCloud >
        <Files wsgi.py>
          Order deny,allow
          Allow from all
        </Files>
       Allow from all
    </Directory>
3. Modify the wsgi.py file to the path of the project


=============================================================================

Working 

1. All the HTML Templates are in the Template folder
2. The handling of client requests are there in auth/views.py file which is responsible for handling the requests from user 
   and directing the user to the appropriate web page and do the processing
3. The deployment requests are stored in Couchbase in these views
4. The Install folder has a file test.py which will trigger the processes (InstanceHadler, install) depending on the value of the request status 
   in the deployment document in database 
5. The next part of managing the instances(creation, deletion)  is done in InstanceHadler.py
6. The part of managing the couchbase deployments (installing couchbase on the instances and setting up the cluster) is done in install.py
 
