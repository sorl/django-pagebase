from django.template import Library
from django.contrib.admin.templatetags.admin_list import result_list


register = Library()


result_list = register.inclusion_tag("pagebase/admin/change_list_results.html")(result_list)

