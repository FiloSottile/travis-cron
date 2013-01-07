# Create your views here.

from crons.models import Entry, Cronjob
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.conf import settings
import urllib2
import json
import random
from urllib import urlencode

def index(request):
    entry_list = Entry.objects.exclude(travis_token = '').order_by('sub_date')
    cron_list = Cronjob.objects.all()
    return render_to_response('crons_index.html',
                              { 'entry_list': entry_list, 'cron_list': cron_list },
                              context_instance=RequestContext(request))

def new(request):
    try:
        entry = Entry(gh_project = request.POST['gh_project'],
                      cronjob = Cronjob.objects.get(pk=request.POST['cronjob']),
                      #github_user = request.POST['github_user'],
                      travis_token = '',
                      #repository_owner_name = request.POST['repository_owner_name'],
                      motivation = request.POST['motivation'],
                      special_requests = request.POST['special_requests'])
        entry.full_clean()
        entry.save()

        state = '%030x' % random.randrange(256**15)
        request.session['state'] = state
        request.session['entry_id'] = entry.id
        return HttpResponseRedirect('https://github.com/login/oauth/authorize?client_id={}&scope=public_repo&state={}'
                                    .format(settings.GITHUB_CLIENT_ID, state))

    except KeyError:
        error_message = 'Something went wrong.'

    except ValidationError as e:
        if '__all__' in e.message_dict:
            error_message = ' '.join(e.message_dict['__all__'])
        else:
            error_message = ' '.join(map(lambda pair: ': '.join((pair[0], pair[1][0])), e.message_dict.items())) # TODO, fa schifo

    entry_list = Entry.objects.all().order_by('sub_date')
    cron_list = Cronjob.objects.all()
    return render_to_response('crons_index.html',
                              { 'entry_list': entry_list, 'cron_list': cron_list,
                              'error_message': error_message },
                              context_instance=RequestContext(request))

def callback(request):
    if request.GET['state'] != request.session['state']:
        return HttpResponse('Unauthorized', status=401)

    data = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET,
        'code': request.GET['code'],
        'state': request.GET['state']
    }
    req = urllib2.Request('https://github.com/login/oauth/access_token', urlencode(data))
    req.add_header('Accept', 'application/json')
    response = json.loads(urllib2.urlopen(req).read())

    if 'access_token' in response and response['access_token']:
        data = { 'github_token': response['access_token'] }
        req = urllib2.Request('https://api.travis-ci.org/auth/github', urlencode(data))
        req.add_header('Accept', 'application/json')
        travis_response = json.loads(urllib2.urlopen(req).read())

        if 'access_token' in travis_response and travis_response['access_token']:
            entry = Entry.objects.get(pk=request.session['entry_id'])
            entry.travis_token = travis_response['access_token']
            entry.save()

            mail_message = "%s - %s\n\n%s\n\nSpecial requests:\n%s\n" % (entry.gh_project, entry.cronjob.description, 
                                                                         entry.motivation, entry.special_requests or 'None :)')
            mail_admins('New entry!', mail_message)

            return HttpResponseRedirect(reverse('crons.views.index'))

        else:
            error_message = 'OAuth error on Travis side'

    else:
        error_message = 'OAuth error on GitHub side'

    entry_list = Entry.objects.all().order_by('sub_date')
    cron_list = Cronjob.objects.all()
    return render_to_response('crons_index.html',
                              { 'entry_list': entry_list, 'cron_list': cron_list,
                              'error_message': error_message },
                              context_instance=RequestContext(request))
