# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from dace.descriptors import (
    SharedUniqueProperty,
    CompositeUniqueProperty,
    )
from dace.util import getSite
from pontus.widget import (
    ImageWidget,
    TextInputWidget)
from pontus.file import ObjectData
from pontus.form import FileUploadTempStore
from deform_treepy.widget import (
    DictSchemaType)

from lac import _
from lac.core import (
    SearchableEntitySchema, SearchableEntity,
    DEFAULT_TREE, keyword_widget)
from lac.utilities.utils import (
    html_to_text, get_site_folder)
from .interface import IBrief
from lac.file import Image
from lac.views.widget import RichTextWidget


def context_is_a_brief(context, request):
    return request.registry.content.istype(context, 'brief')


@colander.deferred
def publication_number_value(node, kw):
    site = get_site_folder(True)
    return getattr(site, 'publication_number', 0)


@colander.deferred
def picture_widget(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    tmpstore = FileUploadTempStore(request)
    source = None
    if context is not root:
        if context.picture:
            source = context.picture

    return ImageWidget(
        tmpstore=tmpstore,
        max_height=500,
        max_width=400,
        source=source,
        selection_message=_("Upload image.")
        )


class BriefSchema(SearchableEntitySchema):
    """Brief schema"""

    name = NameSchemaNode(
        editing=context_is_a_brief,
        )

    title = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_('Title')
        )

    picture = colander.SchemaNode(
        ObjectData(Image),
        widget=picture_widget,
        title=_('Picture'),
        )

    tree = colander.SchemaNode(
        typ=DictSchemaType(),
        widget=keyword_widget,
        default=DEFAULT_TREE,
        missing=DEFAULT_TREE,
        title=_('Categories'),
        )

    details = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        title=_("Details")
        )

    informations = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        title=_("Additional information")
        )

    publication_number = colander.SchemaNode(
        colander.Integer(),
        default=publication_number_value,
        missing=publication_number_value,
        title=_('Publication number'),
        )


@content(
    'brief',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IBrief)
class Brief(SearchableEntity):
    """Brief class"""

    type_title = _('News flash')
    icon = 'lac-icon icon-brief'
    templates = {'default': 'lac:views/templates/brief_result.pt',
                 'bloc': 'lac:views/templates/brief_result_bloc.pt'}
    name = renamer()
    picture = CompositeUniqueProperty('picture')
    author = SharedUniqueProperty('author', 'contents')

    def __init__(self, **kwargs):
        self._presentation_text = None
        super(Brief, self).__init__(**kwargs)
        self.set_data(kwargs)

    def _init_presentation_text(self):
        self._presentation_text = html_to_text(
            getattr(self, 'details', ''))

    def __setattr__(self, name, value):
        super(Brief, self).__setattr__(name, value)
        if name == 'details':
            self._init_presentation_text()

    def presentation_text(self, nb_characters=400):
        text = getattr(self, '_presentation_text', None)
        if text is None:
            self._init_presentation_text()
            text = getattr(self, '_presentation_text', '')

        return text[:nb_characters]+'...'
