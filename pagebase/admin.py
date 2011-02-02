from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from pagebase.models.abstract import PageBase


class PageChangeList(ChangeList):
    def get_query_set(self):
        qs = super(PageChangeList, self).get_query_set()
        return qs.order_by(*PageBase._meta.ordering)


class PageBaseAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'url', 'position')
    list_editable = ('position',)
    change_list_template = 'pagebase/admin/change_list.html'

    def get_changelist(self, request, **kwargs):
        return PageChangeList

