from django.conf.urls import *

#from django.contrib import admin
#admin.autodiscover()
import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CouchbaseCloud.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^userlogin/$', 'auth.views.auth_user'),
    url(r'^getRamSize/$', 'auth.views.getRamSize'),
    url(r'^login/$','auth.views.login_user'),
    url(r'^home/$','auth.views.register_user'),
    url(r'^create_account/$','auth.views.create_account'),
    url(r'^couchdep/$','auth.views.couchdep'),
    url(r'^deploy/$','auth.views.save_deployment'),
    url(r'^mngcluster/$','auth.views.mngcluster'),
    url(r'^Add/$','auth.views.mngviewAdd'),
    url(r'^Del/$','auth.views.mngviewDel'),
    url(r'^installation/$','auth.views.install'),
    url(r'^conf/$','auth.views.conf_couchbase'),
    url(r'^poll_state/$', 'auth.views.poll_state'),
    url(r'^poll_ins_state/$', 'auth.views.poll_ins_state'),
    url(r'^gotoDeployments/$', 'auth.views.handleProgress'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    url(r'^getDeployment/$','auth.views.getDeployment')
)
