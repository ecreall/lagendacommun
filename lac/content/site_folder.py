# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import datetime
import deform
import pytz
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from zope.interface import implementer
from pyramid.threadlocal import get_current_registry

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from dace.descriptors import (
    CompositeMultipleProperty,
    CompositeUniqueProperty,
    SharedUniqueProperty)
from pontus.file import OBJECT_DATA
from pontus.core import VisualisableElement, VisualisableElementSchema
from pontus.schema import omit, select
from pontus.file import ObjectData as ObjectDataOrigine
from pontus.widget import (
    SequenceWidget,
    SimpleMappingWidget,
    Select2Widget)
from deform_treepy.utilities.tree_utility import (
    get_keywords_by_level, merge_tree,
    tree_to_keywords, normalize_tree,
    get_tree_nodes_by_level,
    normalize_keywords, get_branches, get_all_branches)

from .interface import ISiteFolder
from lac import _, DEFAULT_SITE_INFORMATIONS
from lac.mail import DEFAULT_SITE_MAILS
from lac.core import FileEntity, ServiceableEntity
from lac.views.widget import SimpleMappingtWidget
from lac.content.site_configuration import (
    FilterConfigurationSchema,
    MailTemplatesConfigurationSchema,
    UserInterfaceConfigurationSchema,
    PublicationConfigurationSchema,
    KeywordsConfSchema,
    OtherSchema,
    DEFAULT_DAYS_VISIBILITY,
    DEFAULT_DELAY_BEFORE_PUBLICATION,
    DEFAULT_CLOSING_FREQUENCE,
)
from lac.core_schema import (
    ContactSchema as ContactSchemaO)
from lac.utilities.utils import synchronize_tree
from lac.content.keyword import (
    DEFAULT_TREE, ROOT_TREE)


_marker = object()


def context_is_a_sitefolder(context, request):
    return request.registry.content.istype(context, 'sitefolder')


class ObjectData(ObjectDataOrigine):

    def clean_cstruct(self, node, cstruct):
        result, appstruct, hasevalue = super(ObjectData, self)\
                                       .clean_cstruct(node, cstruct)
        if 'ui_conf' in result:
            ui_conf = result.pop('ui_conf')
            if 'picture' in ui_conf and ui_conf['picture'] and \
               OBJECT_DATA in ui_conf['picture']:
                ui_conf['picture'] = ui_conf['picture'][OBJECT_DATA]

            if 'favicon' in ui_conf and ui_conf['favicon'] and \
               OBJECT_DATA in ui_conf['favicon']:
                ui_conf['favicon'] = ui_conf['favicon'][OBJECT_DATA]

            if 'theme' in ui_conf and ui_conf['theme'] and\
               OBJECT_DATA in ui_conf['theme']:
                ui_conf['theme'] = ui_conf['theme'][OBJECT_DATA]

            result.update(ui_conf)

        if 'pub_conf' in result:
            pub_conf = result.pop('pub_conf')
            if 'extraction_template' in pub_conf and\
               pub_conf['extraction_template'] and\
               OBJECT_DATA in pub_conf['extraction_template']:
                pub_conf['extraction_template'] = pub_conf['extraction_template'][OBJECT_DATA]

            result.update(pub_conf)

        if 'filter_conf' in result:
            filter_conf = result.pop('filter_conf')
            result.update(filter_conf)

        if 'mail_conf' in result:
            mail_conf = result.pop('mail_conf')
            templates = mail_conf['mail_templates']
            for template in templates:
                mail_id = template['mail_id']
                if mail_id in DEFAULT_SITE_MAILS:
                    template['title'] = DEFAULT_SITE_MAILS[mail_id]['title']

            result.update(mail_conf)

        if 'keywords_conf' in result:
            keywords_conf = result.pop('keywords_conf')
            result.update(keywords_conf)

        if 'other_conf' in result:
            other_conf = result.pop('other_conf')
            result.update(other_conf)

        return result, appstruct, hasevalue


@colander.deferred
def default_title(node, kw):
    request = node.bindings['request']
    return request.localizer.translate(_('Administration service'))


class ContactSchema(ContactSchemaO):

    title = colander.SchemaNode(
        colander.String(),
        title=_('Title'),
        default=default_title
        )

    address = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=4, cols=60),
        title=_('Address'),
        missing=""
        )


@colander.deferred
def urls_ids_choise(node, kw):
    context = node.bindings['context']
    values = getattr(context, 'urls_ids', [])
    values = [(v, v) for v in values]
    return Select2Widget(values=values, create=True, multiple=True)


class SiteFolderSchema(VisualisableElementSchema):
    """Schema for schedule"""

    typ_factory = ObjectData

    name = NameSchemaNode(
        editing=context_is_a_sitefolder,
        )

    title = colander.SchemaNode(
        colander.String(),
        title=_('Title'),
        )

    urls_ids = colander.SchemaNode(
        colander.Set(),
        widget=urls_ids_choise,
        title=_('URLs ids'),
        )

    contacts = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ContactSchema(name='contact',
                                  widget=SimpleMappingWidget(
                                  css_class='contact-well object-well default-well')),
                    ['title', 'address', 'phone', 'surtax', 'email', 'website', 'fax']),
            ['_csrf_token_']),
        widget=SequenceWidget(
            min_len=1,
            add_subitem_text_template=_('Add a new contact')),
        title='Contacts',
        oid='contacts'
        )

    filter_conf = omit(FilterConfigurationSchema(widget=SimpleMappingtWidget(
                                mapping_css_class='controled-form'
                                                  ' object-well default-well hide-bloc',
                                ajax=True,
                                activator_css_class="glyphicon glyphicon-filter",
                                activator_title=_('Set up a filter'))),
                        ["_csrf_token_"])

    mail_conf = omit(MailTemplatesConfigurationSchema(widget=SimpleMappingtWidget(
                                mapping_css_class='controled-form'
                                                  ' object-well default-well hide-bloc',
                                ajax=True,
                                activator_css_class="glyphicon glyphicon-envelope",
                                activator_title=_('Edit mail templates'))),
                        ["_csrf_token_"])

    ui_conf = omit(UserInterfaceConfigurationSchema(widget=SimpleMappingtWidget(
                                mapping_css_class='controled-form'
                                                  ' object-well default-well hide-bloc',
                                ajax=True,
                                activator_css_class="glyphicon glyphicon-eye-open",
                                activator_title=_('Configure the ui'))),
                        ["_csrf_token_"])

    pub_conf = omit(PublicationConfigurationSchema(widget=SimpleMappingtWidget(
                                mapping_css_class='controled-form'
                                                  ' object-well default-well hide-bloc',
                                ajax=True,
                                activator_css_class="lac-icon icon-history",
                                activator_title=_('Configure the publication settings'))),
                        ["_csrf_token_"])
    keywords_conf = omit(KeywordsConfSchema(widget=SimpleMappingtWidget(
                                mapping_css_class='controled-form'
                                                  ' object-well default-well hide-bloc',
                                ajax=True,
                                activator_css_class="glyphicon glyphicon-tags",
                                activator_title=_('Configure the keywords tree'))),
                        ["_csrf_token_"])

    other_conf = omit(OtherSchema(widget=SimpleMappingtWidget(
                                mapping_css_class='controled-form'
                                                  ' object-well default-well hide-bloc',
                                ajax=True,
                                activator_css_class="glyphicon glyphicon-plus",
                                activator_title=_('Other'))),
                        ["_csrf_token_"])


@content(
    'sitefolder',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(ISiteFolder)
class SiteFolder(VisualisableElement, ServiceableEntity):
    """SiteFolder class"""

    icon = 'glyphicon glyphicon-globe'
    templates = {'default': 'lac:views/templates/site_folder_result.pt',
                 'bloc': 'lac:views/templates/site_folder_result.pt'}
    name = renamer()
    tree = synchronize_tree()
    files = CompositeMultipleProperty('files')
    newsletters = CompositeMultipleProperty('newsletters', 'site')
    picture = CompositeUniqueProperty('picture')
    favicon = CompositeUniqueProperty('favicon')
    extraction_template = CompositeUniqueProperty('extraction_template')
    theme = CompositeUniqueProperty('theme')
    customer = SharedUniqueProperty('customer', 'sites')
    applications = CompositeMultipleProperty('applications', 'site')
    # controleur de publication
    current_cover = CompositeUniqueProperty('current_cover')
    alerts = CompositeMultipleProperty('alerts')

    def __init__(self, **kwargs):
        super(SiteFolder, self).__init__(**kwargs)
        self.set_data(kwargs)
        self.init_informations()
        self._keywords_ = []
        self._init_keywords()

    @property
    def mail_conf(self):
        return self.get_data(omit(MailTemplatesConfigurationSchema(),
                                 '_csrf_token_'))

    @property
    def filter_conf(self):
        result = self.get_data(omit(FilterConfigurationSchema(),
                                  '_csrf_token_'))
        return result

    @property
    def pub_conf(self):
        return self.get_data(omit(PublicationConfigurationSchema(),
                                  '_csrf_token_'))

    @property
    def ui_conf(self):
        return self.get_data(omit(UserInterfaceConfigurationSchema(),
                                  '_csrf_token_'))

    @property
    def keywords_conf(self):
        return self.get_data(omit(KeywordsConfSchema(),
                                  '_csrf_token_'))

    @property
    def other_conf(self):
        return self.get_data(omit(OtherSchema(),
                                  '_csrf_token_'))

    @property
    def real_closing_date(self):
        now = datetime.datetime.now(tz=pytz.UTC)
        closing_date = getattr(self, 'closing_date', _marker)
        closing_frequence = getattr(self, 'closing_frequence', 0)
        if closing_date is _marker:
            closing_date = now

        last_closing_date = closing_date - datetime.timedelta(
            days=closing_frequence)
        if now < last_closing_date:
            return last_closing_date

        return closing_date

    @property
    def publication_date(self):
        closing_date = self.real_closing_date
        closing_frequence = getattr(self, 'closing_frequence', 0)
        delay_before_publication = getattr(self, 'delay_before_publication', 0)
        delay = delay_before_publication - closing_frequence
        return datetime.timedelta(days=delay) + closing_date

    @property
    def sections(self):
        levels = self.get_keywords_by_level()
        if len(levels) >= 2:
            return sorted(levels[1])

        return []

    def __setattr__(self, name, value):
        super(SiteFolder, self).__setattr__(name, value)
        if name == 'filters':
            self._init_keywords()

    def init_informations(self):
        self.closing_frequence = DEFAULT_CLOSING_FREQUENCE
        self.delay_before_publication = DEFAULT_DELAY_BEFORE_PUBLICATION
        self.days_visibility = DEFAULT_DAYS_VISIBILITY
        self.publication_number = 0
        self.closing_date = datetime.datetime.now(tz=pytz.UTC) +\
            datetime.timedelta(days=self.closing_frequence)
        self._tree = PersistentDict()
        self.keywords = PersistentList()
        self.tree = DEFAULT_TREE
        self.init_files()

    def get_keywords_by_level(self):
        return get_keywords_by_level(dict(self.tree), ROOT_TREE)

    def get_tree_nodes_by_level(self):
        return get_tree_nodes_by_level(dict(self.tree))

    def get_all_branches(self):
        return get_all_branches(self.tree)

    def merge_tree(self, tree):
        mapping = getattr(self, 'keywords_mapping', {}).get('mapping', [])
        self.tree = merge_tree(dict(self.tree), tree, mapping)

    def get_normalized_tree(self, tree, type_='out'):
        mapping = getattr(self, 'keywords_mapping', {}).get('mapping', [])
        return normalize_tree(tree, mapping, type_)

    def get_normalized_keywords(self, keywords, type_='out'):
        mapping = getattr(self, 'keywords_mapping', {}).get('mapping', [])
        return normalize_keywords(keywords, mapping, type_)

    def get_tree_branches(self):
        return get_branches(getattr(self, 'tree', {}))

    def init_files(self):
        for information in DEFAULT_SITE_INFORMATIONS:
            if not self.get(information['name'], None):
                info_file = FileEntity(title=information['title'])
                info_file.text = information['content']
                info_file.__name__ = information['name']
                self.addtoproperty('files', info_file)

    def next_publication_date(self, week_number=0):
        closing_date = self.real_closing_date
        delay_before_publication = getattr(self, 'delay_before_publication', 0)
        days = getattr(self, 'closing_frequence', 0) * week_number
        return datetime.timedelta(days=delay_before_publication) +\
            closing_date +\
            datetime.timedelta(days=days)

    def get_mail_template(self, id):
        for mail in getattr(self, 'mail_templates', {}):
            if mail.get('mail_id', None) == id:
                return mail

        template = DEFAULT_SITE_MAILS.get(id, None)
        if template:
            template = template.copy()
            template['mail_id'] = id

        return template

    def get_site_sender(self):
        registry = get_current_registry()
        default_sender = registry.settings['lac.admin_email']
        return getattr(self, 'site_sender', default_sender)

    def _init_keywords(self):
        alltrees = [f.get('metadata_filter', {}).get('tree', {})
                    for f in getattr(self, 'filters', [])]
        keywords = [tree_to_keywords(tree) for tree in alltrees]
        keywords = list(set([item for sublist in keywords for item in sublist]))
        self._keywords_ = keywords

    def get_all_keywords(self):
        if hasattr(self, '_keywords_'):
            return self._keywords_
        self._init_keywords()
        return self._keywords_.copy()

    def get_group(self):
        if not self.customer:
            return []

        sites = list(self.customer.sites)
        if self in sites:
            sites.remove(self)

        return sites
