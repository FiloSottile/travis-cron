from django.core.management.base import BaseCommand, CommandError
from crons.models import Entry, Cronjob
from time import sleep

def ping(entry):
    pass

class Command(BaseCommand):
    help = 'Run the worker that performs the pings to Travis'

    def handle(self, *args, **options):
        self.stdout.write('[*] Starting...\n')
        while True:
            jobs = Cronjob.objects.all()
            for job in jobs:
                if not job.need_run(): continue
                self.stdout.write('[+] Running ' + job.description + '...\n')
                for entry in job.entry_set.filter(approved=True).exclude(travis_token=''):
                    self.stdout.write('[+] Ping ' + entry.gh_project + '\n')
                    ping(entry)
                job.run_now()
                job.save()
            before_next = min(map(lambda job: job.before_next_run(), jobs))
            before_next = 0 if before_next < 0 else int(before_next + 1)
            self.stdout.write('[-] Sleeping ' + str(before_next) + ' seconds...\n')
            self.stdout.flush()
            sleep(before_next)