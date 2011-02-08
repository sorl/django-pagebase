from pagebase.helpers import registry
from pagebase.models.base import EmptyPage


def page(request):
    try:
        page = registry.published_queryset.get(url=request.path)
    except registry.model.DoesNotExist:
        page = EmptyPage()
    return {'page': page}

