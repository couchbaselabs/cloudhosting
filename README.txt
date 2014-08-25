This software allows the user to easily manage the deployment of couchbase server to multiple clouds. This software currently supports the cloud providers mainly AWS, RackSpace and Google Cloud. It also supports Azure until the point of creating the instances in Azure cloud. This software uses the Apache Libcloud Library (Python), Apache Web Server, Django (Python framework) for web development

Installation : 
pip install apache-libcloud

The Library provides an interface to interact with the API’s of the respective cloud providers
This software currently supports Rackspace, Google Cloud and AWS

We use the library for getting authenticated to the cloud providers, create instances and delete the instances

Libcloud acts as a lowest common denominator and exposes a unified base API which allows you to work with many different cloud providers through a single code base.

Being a lowest common denominator by definition means that not all of the functionality offered by different cloud service providers is available through a base API.

Libcloud solves this problem and allows user to access provider specific functionality through a so called extension methods and arguments. Extension methods and arguments are all the methods and arguments which are prefixed with ex_.

Extension methods are there for your convenience, but you should be careful when you use them because they make switching or working with multiple providers harder.

=====================================================================================

Directory Structure

    CouchbaseCloud
         -->  auth
         -->  static
         -->  CouchbaseCloud_Settings
		-->Templates
    Install

=========================================================================================

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
2. The handling of client requests are there in auth/views.py file which is responsible for handling the requests from        user and directing the user to the appropriate web page and create a request in the Deployment::<user>::<timestamp>
   depending upon the activities of the user namely (adding, deleting and creating new deployments). All the user details     are present in the couchbase docuent with format like user::<username>
3. The deployment requests are stored in couchbase documents through these views
4. The Install folder has a file test.py (driver) which will trigger the processes (InstanceHadler, install) depending on     the value of the request status in the deployment document in database 
5. The next part of managing the instances(creation, deletion)  is done in InstanceHadler.py
   The logic creation of instances, deletion (management) is maintained in this file. 
6. The part of managing the couchbase deployments (installing couchbase on the instances and setting up the cluster) is       done in install.py
7. There is a file az.py in the Install folder manages the Azure instances (creation) uses Azure API's

Flow:
1. The home page in the website has the details for provisioning the user to create a new account
2. If the user is an existing one he can login and manage his deployments
3. There is an option to create a new deployment for the user where he can select a cloud provider of his choice and 
   provide the authentication details for the cloud and the parameters of the node to created in the deployment
4. The user can manage the instances by scaling (adding more servers) and removing the servers as required

===================================================================================

Executing the program:
1. Start the apache web server after all the configuration is made as discussed above. The web server should be run as       non-root user
2. Run test.py using (python test.py) which will turn on the InstanceHadler and install daemon 
3. Then you can start using the website

=====================================================================================

In case of any doubts you can email me at : srivastava.piush@gmail.com, pasrivas@syr.edu


 
