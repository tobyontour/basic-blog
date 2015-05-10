from django.conf import settings

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def site_name_processor(request):
    if not hasattr(settings, 'SITE_NAME'):
        logger.warning('No SITE_NAME set in settings.')
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Blog'),
    }