from abc import ABCMeta, abstractmethod
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect


class PageViewMixin(object):
    """
    This view is designed for aino-utkik `View`.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_query_set(self):
        """
        Implementing classes should return a queryset to filter on for the page
        detail view.
        """
        raise NotImplemented

    def get(self, url):
        """
        The get handler for the view.
        """
        if not url.endswith('/') and settings.APPEND_SLASH:
            return HttpResponseRedirect("%s/" % self.request.path)
        if not url.startswith('/'):
            url = "/" + url
        try:
            self.c.page = self.get_query_set().get(url=url)
        except ObjectDoesNotExist:
            raise Http404

