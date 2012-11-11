from django.db import models
from datetime import datetime, timedelta

# Create your models here.

class Cronjob(models.Model):
    description = models.CharField(max_length=200)

    run_every = models.IntegerField('run every (seconds)')
    last_run = models.DateTimeField()

    def run_now(self):
        self.last_run = datetime.now()

    def need_run(self):
        return datetime.now() > (self.last_run + timedelta(seconds=self.run_every))

    def before_next_run(self):
        t = self.last_run + timedelta(seconds=self.run_every) - datetime.now()
        return t.seconds + t.microseconds / 1E6 + t.days * 86400

    def __unicode__(self):
        return self.description

class Entry(models.Model):
    gh_project = models.CharField(max_length=200)
    cronjob = models.ForeignKey(Cronjob)
    sub_date = models.DateTimeField('date submitted', auto_now_add=True)
    approved = models.BooleanField(default=False)

    github_user = models.CharField(max_length=200)
    travis_token  = models.CharField(max_length=200)
    repository_owner_name = models.CharField(max_length=200)

    motivation = models.CharField(max_length=500)
    special_requests = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return self.gh_project

    def clean(self):
        from django.core.exceptions import ValidationError
        if not '/' in self.gh_project:
            raise ValidationError('The GitHub project must be formatted like rg3/youtube-dl')