from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'travis_cron.views.home', name='home'),
    # url(r'^travis_cron/', include('travis_cron.foo.urls')),
    url(r'^$', 'crons.views.index'),
    url(r'^new$', 'crons.views.new'),
    url(r'^callback$', 'crons.views.callback'),

    (r'^robots\.txt$', direct_to_template,
     {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^humans\.txt$', direct_to_template,
     {'template': 'humans.txt', 'mimetype': 'text/plain'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
