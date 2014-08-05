from django.conf.urls import *

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CouchbaseCloud.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^auth/$', 'auth.views.auth_user'),
    url(r'^login/$','auth.views.login_user'),
    url(r'^signup/$','auth.views.register_user'),
    url(r'^create_account/$','auth.views.create_account'),
    url(r'^couchdep/$','auth.views.couchdep'),
    url(r'^deploy/$','auth.views.deploy'),
    url(r'^mngcluster/$','auth.views.mngcluster'),
    url(r'^Add/$','auth.views.mngviewAdd'),
    url(r'^Del/$','auth.views.mngviewDel')
)
