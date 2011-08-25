import os
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.contrib import admin
from settings import PROJECT_PATH
import vocab.urls

admin.autodiscover()


urlpatterns = patterns('',
    # Homepage
    (r'^$', 'vocab.views.facebook_home'),
    (r'^$', 'home.views.homepage'),

    # Auth
    (r'^login/$','accounts.views.login_handler'),
    (r'^logout/$','accounts.views.logout_handler'),
    url(r'', include('social_auth.urls')),

    # v2 prototype
    (r'^prototypes/framework/?$', redirect_to,
        {'url':'/prototypes/framework/framework.html','permanent':False,'query_string':True}),
    (r'^prototypes/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root':os.path.join(PROJECT_PATH,'oldprototypes')}),

    # Admin
    (r'^admin/', include(admin.site.urls)),
)
urlpatterns += vocab.urls.urlpatterns

