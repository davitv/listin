import gzip
import json
import io

from optparse import make_option

from django.core.management import BaseCommand, call_command

from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    """
    Generate fixtures necessary for local development of production database.

    NOTE: This should be run as a cron job on the production www.listin.ru
    infrastructure, it is not useful to run this in a local environment except
    for testing/debugging purposes of this command itself.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--file',
            default='/tmp/listin-dev-fixtures.json.gz',
            dest='outputfile',
            help='Specifies the output file location of the fixtures.',
        ),
    )

    help = "Generate development fixtures for local development"

    def handle(self, **options):
        outputfile = options.get('outputfile')

        content = io.BytesIO()
        call_command(
            "dumpdata",
            format='json',
            indent=4,
            exclude=[
                "sessions",
                "contenttypes",
            ],
            stdout=content,
        )
        content.seek(0)
        raw_json = content.getvalue()
        data = json.loads(raw_json)

        # Scrub User passwords for security
        for obj in data:
            if obj['model'] != "users.user":
                continue
            obj['fields']['password'] = make_password(None)

        with gzip.open(outputfile, 'wb') as out:
            out.write(bytes(json.dumps(data, indent=4)))

