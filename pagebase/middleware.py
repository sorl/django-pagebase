from abc import ABCMeta, abstractmethod
from django.conf import settings
from django.http import Http404


class PageFallbackMiddlewareBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_response(self, request):
        """
        Return the response of a view with current request and url here.
        """
        raise NotImplemented

    def process_response(self, request, response):
        if response.status_code == 404:
            try:
                response = self.get_response(request)
            except Http404:
                pass # prevent exception to propagate to handler
            except Exception:
                if settings.DEBUG:
                    raise
        return response

