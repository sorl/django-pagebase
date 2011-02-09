from abc import ABCMeta, abstractproperty, abstractmethod
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView
from django.http import Http404, HttpResponseRedirect


class PageViewMixinBase(object):
    __metaclass__ = ABCMeta

    template_name = 'pages/default.html'

    @abstractmethod
    def get_query_set(self):
        raise NotImplemented

    def get_context_data(self, url=None):
        if not url.endswith('/') and settings.APPEND_SLASH:
            return HttpResponseRedirect("%s/" % self.request.path)
        if not url.startswith('/'):
            url = "/" + url
        try:
            page = self.get_query_set().get(url=url)
        except ObjectDoesNotExist:
            raise Http404
        return {'page': page}


class PageViewBase(PageViewMixinBase, TemplateView):
    pass

