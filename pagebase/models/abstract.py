#coding=utf-8
from pagebase.models.fields import IntegerArrayField, AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _


SECTIONS = (
    ('main', _('Main')),
    ('eyebrow', _('Eyebrow')),
)

class PageBase(models.Model):
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

