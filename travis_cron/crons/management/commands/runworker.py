from django.core.management.base import BaseCommand, CommandError
from crons.models import Entry, Cronjob
from time import sleep, time
from travis_ping import travis_ping
from traceback import print_exc

def ping(entry):
    travis_token = entry.travis_token
    repository = entry.gh_project
    return travis_ping(travis_token, repository)

class Command(BaseCommand):
    help = ('Run the worker that performs the pings to Travis. '
            'If invoked with an argument, this should be the number of seconds every which this command is run by cron; '
            'otherwise it will run continuously.')

    def handle(self, *args, **options):
        started = time()
        frequency = None
        if len(args) > 0:
            frequency = int(args[0])
        self.stdout.write('[*] Starting...\n')
        while True:
            jobs = Cronjob.objects.all()
            for job in jobs:
                if not job.need_run(): continue
                self.stdout.write('[+] Running ' + job.description + '...\n')
                for entry in job.entry_set.filter(approved=True).exclude(travis_token=''):
                    self.stdout.write('[+] Ping ' + entry.gh_project + '\n')
                    try: ping(entry)
                    except: print_exc()
                job.run_now()
                job.save()

            self.stdout.write('[-] Pinging myself as a Dead Man Snitch...\n')
            ping(Entry.objects.get(gh_project="FiloSottile/travis-cron"))

            before_next = min(map(lambda job: job.before_next_run(), jobs))
            before_next = 0 if before_next < 0 else int(before_next + 1)
            if frequency and (time() + before_next) > (started + frequency):
                    self.stdout.write('[-] Closing...\n')
                    break
            self.stdout.write('[-] Sleeping ' + str(before_next) + ' seconds...\n')
            self.stdout.flush()
            sleep(before_next)
