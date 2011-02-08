from abc import ABCMeta, abstractmethod
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from pagebase.models.base import EmptyPage


class PageContextMiddleWareBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_query_set(self):
        raise NotImplemented

    def process_template_response(self, request, response):
        if 'page' not in response.context_data:
            try:
                page = self.get_query_set().get(url=request.path)
            except ObjectDoesNotExist:
                page = EmptyPage()
            response.context_data['page'] = page
        return response


class PageFallbackMiddlewareBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_view(self):
        raise NotImplemented

    def process_response(self, request, response):
        if response.status_code == 404:
            try:
                response = self.get_view()(request, url=request.path)
                # unfortunately we have to render the view since template
                # processing middleware has already been run.
                if hasattr(response, 'render') and callable(response.render):
                    response = response.render()
            except Http404:
                pass # prevent exception to propagate to handler
            except Exception:
                if settings.DEBUG:
                    raise
        return response

