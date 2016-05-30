# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from dace.util import getSite
from dace.objectofcollaboration.entity import Entity
from dace.descriptors import SharedMultipleProperty
from pontus.core import VisualisableElement, VisualisableElementSchema
from pontus.widget import (
    Select2Widget, SequenceWidget, SimpleMappingWidget)
from pontus.schema import Schema, select, omit

from .interface import IKeyword
from lac import _
# from lac.views.widget import SimpleMappingtWidget


ROOT_TREE = "Rubrique"

DEFAULT_TREE = {ROOT_TREE: {}}

DEFAULT_TREE_LEN = 5


def context_is_a_keyword(context, request):
    return request.registry.content.istype(context, 'keyword')


@colander.deferred
def keywords_choice(node, kw):
    root = getSite()
    values = [(k, k) for k in root.keywords_ids]
    values.insert(0, ('', _('- Select -')))
    return Select2Widget(
        values=values,
        create=True)


class KeywordSchema(VisualisableElementSchema):
    """Schema for keyword"""

    name = NameSchemaNode(
        editing=context_is_a_keyword,
        )

    title = colander.SchemaNode(
        colander.String(),
        widget=keywords_choice,
        title=_('/'),
        missing="",
        )


@content(
    'keyword',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IKeyword)
class Keyword(VisualisableElement, Entity):
    """Keyword class"""

    name = renamer()
    referenced_elements = SharedMultipleProperty('referenced_elements',
                                                 'keywords')

    def __init__(self, **kwargs):
        super(Keyword, self).__init__(**kwargs)
        self.set_data(kwargs)


@colander.deferred
def content_types_choices(node, kw):
    from lac import core
    request = node.bindings['request']
    values = []
    exclude_internal = request.user is None
    values = [(key, getattr(c, 'type_title', c.__class__.__name__))
              for key, c in list(core.SEARCHABLE_CONTENTS.items())
              if not exclude_internal or
              (exclude_internal and not getattr(c, 'internal_type', False))]

    values = sorted(values, key=lambda e: e[0])
    return Select2Widget(values=values, multiple=True)


@colander.deferred
def aliases_choices(node, kw):
    request = node.bindings['request']
    values = request.root.get_keywords_by_level()
    if values:
        values = list(set([item for sublist in values for item in sublist]))
        values = sorted([(k, k) for k in values], key=lambda e: e[0])

    return Select2Widget(
        values=values,
        create=True,
        multiple=True)


@colander.deferred
def node_choices(node, kw):
    request = node.bindings['request']
    values = request.get_site_folder.get_all_branches()
    if values:
        values = sorted([(k, k) for k in values], key=lambda e: e[0])

    return Select2Widget(
        values=values)


class KeywordMappingSchema(Schema):

    node_id = colander.SchemaNode(
        colander.String(),
        widget=node_choices,
        title=_('Node'),
        description=_("You can select the node to map."),
    )

    aliases = colander.SchemaNode(
        colander.Set(),
        widget=aliases_choices,
        title=_('Aliases'),
        description=_("You can select aliases corresponding to the node."),
        default=[]
        )

    content_types = colander.SchemaNode(
        colander.Set(),
        widget=content_types_choices,
        title=_('Associated types'),
        description=_('You can select content types associated to this node.'),
        default=[],
        missing=[]
        )


class KeywordsMappingSchema(Schema):

    mapping = colander.SchemaNode(
        colander.Sequence(),
        omit(select(KeywordMappingSchema(
            name='mapping',
            widget=SimpleMappingWidget(
                                css_class='object-well default-well')),
                    ['node_id', 'aliases', 'content_types']),
            ['_csrf_token_']),
        widget=SequenceWidget(
            add_subitem_text_template=_("Add a new keyword's mapping")),
        title=_("keywords's mapping"),
        missing=[]
        )
