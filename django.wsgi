#
# mod_wsgi handler for the onlineweb django project
#


import site
site.addsitedir('/usr/local/pythonenv/onlinepetition/lib/python2.6/site-packages')

import os
import sys

#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

sys.path.append('/var/websites/prod/onlinepetition')
sys.path.append('/var/websites/prod/onlinepetition/onlinepetition')

os.environ['DJANGO_SETTINGS_MODULE'] = 'onlinepetition.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

