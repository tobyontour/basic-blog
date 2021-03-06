# Create your views here.

from django.conf import settings

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def site_metadata_processor(request):
    if not hasattr(settings, 'SITE_NAME'):  # pragma: no cover
        logger.warning('No SITE_NAME set in settings.')

    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Blog'),
        'SITE_COPYRIGHT': getattr(settings, 'SITE_COPYRIGHT', 'This content is copyrighted.'),
        'DISQUS_SHORTNAME': getattr(settings, 'DISQUS_SHORTNAME', None),
        'GOOGLE_SITE_VERIFICATION': getattr(settings, 'GOOGLE_SITE_VERIFICATION', None),
    }
