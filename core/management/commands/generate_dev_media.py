import os
import tarfile

from optparse import make_option

from django.core.management import BaseCommand
from django.conf import settings


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


class Command(BaseCommand):
    """
    Archive media files necessary for local development.

    NOTE: This should be run as a cron job on the production www.listin.ru
    infrastructure, it is not useful to run this in a local environment except
    for testing/debugging purposes of this command itself.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--file',
            default='/tmp/listin-dev-media.tar.gz',
            dest='outputfile',
            help='Specifies the output file location of the fixtures.',
        ),
    )

    help = "Generate development media files."

    def handle(self, **options):
        outputfile = options.get('outputfile')

        self.stdout.write(self.style.SUCCESS('Archiving media root folder. May take a while...'))
        make_tarfile(outputfile, settings.MEDIA_ROOT)
        self.stdout.write(self.style.SUCCESS('Finished. Now you can use %s archive' % (outputfile, )))
