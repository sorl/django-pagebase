"""
Most of these fields will only work with PostgreSQL
"""
from django.db import models
from django.utils.datastructures import DictWrapper


__all__ = ('CharArrayField', 'IntegerArrayField', 'BooleanArrayField',
           'SouthMixin')


class SouthMixin(object):
    """
    Just some south introspection Mixin
    """
    def south_field_triple(self):
        from south.modelsinspector import introspector
        cls_name = '%s.%s' % (self.__class__.__module__ , self.__class__.__name__)
        args, kwargs = introspector(self)
        return (cls_name, args, kwargs)


class NoSerializeField(SouthMixin, models.Field):
    """
    A base field for field types that cannot be serialized
    """
    def __init__(self, *args, **kwargs):
        kwargs['serialize'] = False
        super(NoSerializeField, self).__init__(*args, **kwargs)


class BaseArrayField(NoSerializeField):
    def get_prep_value(self, value):
        if value == '':
            value = '{}'
        return value


class CharArrayField(BaseArrayField):
    """
    A character varying array field for PostgreSQL
    """
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 200)
        super(CharArrayField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        data = DictWrapper(self.__dict__, connection.ops.quote_name, "qn_")
        return 'character varying(%(max_length)s)[]' % data


class IntegerArrayField(BaseArrayField):
    """
    An integer array field for PostgreSQL
    """
    def db_type(self, connection):
        return 'integer[]'


class BooleanArrayField(BaseArrayField):
    """
    A boolean array field for PostgreSQL
    """
    def db_type(self, connection):
        return 'boolean[]'

