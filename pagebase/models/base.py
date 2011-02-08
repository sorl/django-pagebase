#coding=utf-8
from aislug import AISlugField
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.fields import Field
from django.utils.translation import ugettext_lazy as _
from pagebase.helpers import register
from pagebase.models.fields import IntegerArrayField


SECTIONS = (
    ('main', _('Main')),
    ('eyebrow', _('Eyebrow')),
)


class EmptyPage(object):
    def __nonzero__(self):
        return False

    def __getattr__(self, name):
        return ''


class PageBaseMeta(ModelBase):
    """
    Meta class for abstract class ``PageBaseMeta``. This class hides the model
    fields on allocation so that you can pick them up or not in a meta class
    that inherits this.
    """
    base_fields = {}

    def __new__(cls, name, bases, attrs):
        for k, v in attrs.items():
            if isinstance(v, Field):
                cls.base_fields[k] = attrs.pop(k)
        return ModelBase.__new__(cls, name, bases, attrs)


class PageMeta(PageBaseMeta):
    """
    This is what implementing classes need to use
    """
    def __new__(cls, name, bases, attrs):
        # inject PageBase fields
        for k, v in cls.base_fields.items():
            if k not in attrs:
                attrs[k] = cls.base_fields[k]
        page_cls = ModelBase.__new__(cls, name, bases, attrs)
        register(page_cls)
        return page_cls


class PageBase(models.Model):
    """
    The base model for page.
    """
    __metaclass__ = PageBaseMeta
    section = models.CharField(_('section'), choices=SECTIONS, max_length=10, blank=True)
    parent = models.ForeignKey('self', verbose_name=_(u'parent'), blank=True, null=True, related_name='children')
    title = models.CharField(_('title'), max_length=500)
    slug = AISlugField(max_length=510, blank=True)
    position = models.IntegerField(_('position'), default=0)

    # tree denormalizarion
    level = models.PositiveIntegerField(null=True, editable=False)
    url = models.CharField(max_length=500, db_index=True, blank=True, editable=False)
    id_array = IntegerArrayField(null=True, editable=False)
    position_array = IntegerArrayField(null=True, editable=False)

    def children_or_siblings(self):
        children = self.children.all()
        if children:
            return children
        if self.level > 1:
            return self._default_manager.filter(parent=self.parent)
        return []

    def get_absolute_url(self):
        return self.url

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ('-section', 'position_array', 'title')
        verbose_name = _('page')
        verbose_name_plural = _('pages')

