# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from pyramid.threadlocal import get_current_registry

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer
from substanced.property import PropertySheet

from dace.util import getSite
from dace.objectofcollaboration.application import Application
from dace.descriptors import CompositeMultipleProperty
from pontus.core import VisualisableElement, VisualisableElementSchema
from pontus.widget import SequenceWidget, SimpleMappingWidget
from pontus.schema import omit
from deform_treepy.widget import (
    DictSchemaType, KeywordsTreeWidget)
from deform_treepy.utilities.tree_utility import (
    get_tree_nodes_by_level, merge_tree,
    get_keywords_by_level)

from lac import _
from .organization import OrganizationSchema, Organization
from lac.content.interface import ICreationCulturelleApplication
from lac.content.keyword import (
    DEFAULT_TREE, DEFAULT_TREE_LEN, ROOT_TREE)
from lac.content.resources import (
    default_resourcemanager,
    IResourceManager)
from lac.utilities.utils import synchronize_tree


DEFAULT_TITLES = [_('Mr'), _('Mrs'), _('Ms')]


DEFAULT_TICKET_TYPES_VALUES = [
    _('Paying admission'),
    _('Free admission'),
    _('Open price')]


def context_is_a_root(context, request):
    return request.registry.content.istype(context, 'Root')


@colander.deferred
def keyword_widget(node, kw):
    can_create = 0
    root = getSite()
    values = root.get_tree_nodes_by_level()
    if values:
        values = values[1:]

    return KeywordsTreeWidget(
        min_len=1,
        max_len=DEFAULT_TREE_LEN,
        can_create=can_create,
        levels=values)


@colander.deferred
def keywords_validator(node, kw):
    if DEFAULT_TREE == kw:
        raise colander.Invalid(node, _('Minimum one category required.'))


@colander.deferred
def organizations_choice(node, kw):
    context = node.bindings['context']
    len_organizations = len(context.organizations)
    if len_organizations == 0:
        len_organizations = -1

    return SequenceWidget(min_len=len_organizations,
                          max_len=len_organizations)


class CreationCulturelleApplicationSchema(VisualisableElementSchema):

    """Schema for application configuration."""

    name = NameSchemaNode(
        editing=context_is_a_root,
        )

    titles = colander.SchemaNode(
        colander.Sequence(),
        colander.SchemaNode(
            colander.String(),
            name=_("Title")
            ),
        widget=SequenceWidget(),
        default=DEFAULT_TITLES,
        title=_('List of titles'),
        )

    tree = colander.SchemaNode(
        typ=DictSchemaType(),
        validator=colander.All(keywords_validator),
        widget=keyword_widget,
        default=DEFAULT_TREE,
        title=_('Categories'),
        )

    organizations = colander.SchemaNode(
        colander.Sequence(),
        omit(OrganizationSchema(
            factory=Organization,
            editable=True,
            name=_('Organization'),
            widget=SimpleMappingWidget(css_class='object-well default-well'),
            omit=['managers']),
        ['_csrf_token_']),
        widget=organizations_choice,
        title=_('Organizations'),
        )


class CreationCulturelleApplicationPropertySheet(PropertySheet):
    schema = CreationCulturelleApplicationSchema()


@content(
    'Root',
    icon='glyphicon glyphicon-home',
    propertysheets=(
        ('Basic', CreationCulturelleApplicationPropertySheet),
        ),
    after_create='after_create',
    )
@implementer(ICreationCulturelleApplication)
class CreationCulturelleApplication(VisualisableElement, Application):

    """Application root."""

    name = renamer()
    tree = synchronize_tree()
    files = CompositeMultipleProperty('files')
    site_folders = CompositeMultipleProperty('site_folders')
    preregistrations = CompositeMultipleProperty('preregistrations')
    smart_folders = CompositeMultipleProperty('smart_folders')
    cultural_events = CompositeMultipleProperty('cultural_events')
    schedules = CompositeMultipleProperty('schedules')
    film_schedules = CompositeMultipleProperty('film_schedules')
    reviews = CompositeMultipleProperty('reviews')
    advertisings = CompositeMultipleProperty('advertisings')
    games = CompositeMultipleProperty('games')
    pictures = CompositeMultipleProperty('pictures')
    organizations = CompositeMultipleProperty('organizations')
    groups = CompositeMultipleProperty('groups')
    services_definition = CompositeMultipleProperty('services_definition')
    artists = CompositeMultipleProperty('artists')
    venues = CompositeMultipleProperty('venues')
    labels = CompositeMultipleProperty('labels')

    def __init__(self, **kwargs):
        super(CreationCulturelleApplication, self).__init__(**kwargs)
        self.initialization()

    def initialization(self):
        self.titles = DEFAULT_TITLES
        self.ticket_types_values = DEFAULT_TICKET_TYPES_VALUES
        self._tree = PersistentDict()
        self.keywords = PersistentList()
        self.tree = DEFAULT_TREE

    def get_keywords_by_level(self):
        return get_keywords_by_level(dict(self.tree), ROOT_TREE)

    def get_tree_nodes_by_level(self):
        return get_tree_nodes_by_level(dict(self.tree))

    def merge_tree(self, tree):
        self.tree = merge_tree(dict(self.tree), tree)

    @property
    def resourcemanager(self):
        return get_current_registry().getUtility(IResourceManager,
                                                 default_resourcemanager)

    def get_services_definition(self):
        return {service.service_id: service for service in self.services_definition}
