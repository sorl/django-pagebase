#coding=utf-8
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.fields import Field
from django.utils.translation import ugettext_lazy as _
from pagebase.models.fields import IntegerArrayField, AutoSlugField


SECTIONS = (
    ('main', _('Main')),
    ('eyebrow', _('Eyebrow')),
)


class HideFieldsMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        cls._basepage_fields = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                cls._basepage_fields[k] = attrs.pop(k)
        return super(HideFieldsMeta, cls).__new__(cls, name, bases, attrs)


class PageBaseMeta(HideFieldsMeta):
    """
    This is what implementing classes need to use
    """
    def __new__(cls, name, bases, attrs):
        for k, v in cls._basepage_fields.items():
            if k not in attrs:
                attrs[k] = cls._basepage_fields.pop(k)
        return super(HideFieldsMeta, cls).__new__(cls, name, bases, attrs)


class PageBase(models.Model):
    __metaclass__ = HideFieldsMeta
    section = models.CharField(_('section'), choices=SECTIONS, max_length=10, blank=True)
    parent = models.ForeignKey('self', verbose_name=_(u'parent'), blank=True, null=True, related_name='children')
    title = models.CharField(_('title'), max_length=500)
    slug = AutoSlugField(max_length=510, blank=True)
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

