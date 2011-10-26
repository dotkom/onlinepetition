from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('petition.views',
    url(r'^$', 'latest', name='campaign_latest'),
    url(r'^list$', 'list', name='campaign_list'),
    url(r'^(?P<campaign_id>\d+)/$', 'details', name='campaign_details'),
    url(r'^(?P<campaign_id>\d+)/register$', 'register', name='campaign_register'),
    url(r'^(?P<campaign_id>\d+)/activate/(?P<email>\w+)/(?P<hash>\w+)$', 'activate', name='campaign_activate'),
    url(r'about$', 'about', name='petition_about'),
    url(r'faq$', 'faq', name='petition_faq'),
    url(r'login$', 'mylogin', name='petition_login'),
    url(r'logout$', 'mylogout', name='petition_logout'),
)


