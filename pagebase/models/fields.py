"""
Most of these fields will only work with PostgreSQL
"""
from django.db import models
from django.utils.datastructures import DictWrapper


__all__ = ('CharArrayField', 'IntegerArrayField', 'BooleanArrayField')


class ArrayFieldBase(models.Field):
    """
    A base class for PostgreSQL array fields.
    """
    def __init__(self, *args, **kwargs):
        kwargs['serialize'] = False # TODO, figure this out
        super(ArrayFieldBase, self).__init__(*args, **kwargs)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        name = '%s.%s' % (self.__class__.__module__ , self.__class__.__name__)
        args, kwargs = introspector(self)
        return name, args, kwargs

    def get_prep_value(self, value):
        if value == '':
            value = '{}'
        return value


class CharArrayField(ArrayFieldBase):
    """
    A character varying array field for PostgreSQL
    """
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 200)
        super(CharArrayField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        data = DictWrapper(self.__dict__, connection.ops.quote_name, "qn_")
        return 'character varying(%(max_length)s)[]' % data


class IntegerArrayField(ArrayFieldBase):
    """
    An integer array field for PostgreSQL
    """
    def db_type(self, connection):
        return 'integer[]'


class BooleanArrayField(ArrayFieldBase):
    """
    A boolean array field for PostgreSQL
    """
    def db_type(self, connection):
        return 'boolean[]'

