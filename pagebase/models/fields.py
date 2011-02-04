"""
Most of these fields will only work with PostgreSQL
"""
import re
import unicodedata
from django.db import models
from django.utils.datastructures import DictWrapper
from django.utils.encoding import force_unicode


__all__ = ('CharArrayField', 'IntegerArrayField', 'BooleanArrayField',
           'AutoSlugField', 'SouthMixin')


invalid_pat = re.compile(r'[^-a-z0-9]')
limit_pat = re.compile(r'-{2,}')


def slugify(s):
    """
    Make slugs for SlugField
    """
    # force unicode
    s = force_unicode(s)
    # normalize to ascii
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    # lowercase
    s = s.lower()
    # make invalid chars -
    s = invalid_pat.sub('-', s)
    # limit - to one
    s = limit_pat.sub('-', s)
    # strip -
    s = s.strip('-')
    return s


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


class AutoSlugField(SouthMixin, models.SlugField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 110)
        kwargs.setdefault('unique', True)
        kwargs.setdefault('editable', False)
        self.update = kwargs.pop('update', True)
        self.populate_from = kwargs.pop('populate_from', 'title')
        self.slugify = kwargs.pop('slugify', slugify)
        self.invalid = kwargs.pop('invalid', [])
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, obj, add):
        if add or self.update:
            value = getattr(obj, self.populate_from)
            if callable(value):
                value = value()
        else:
            value = self.value_from_object(obj)
        slug = self.slugify(value)
        counter = 1
        _slug = slug
        invalid = self.invalid
        if callable(invalid):
            invalid = invalid()
        while True:
            qs = obj.__class__._default_manager.filter(**{self.attname: _slug})
            if not add:
                qs = qs.exclude(pk=obj.pk)
            if _slug not in invalid and not qs:
                break
            _slug = '%s-%s' % (slug, counter)
            counter += 1
        slug = _slug
        setattr(obj, self.attname, slug)
        return slug

