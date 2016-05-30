# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import deform
from zope.interface import implementer, invariant
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from pyramid.threadlocal import get_current_request

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer, get_oid

from dace.objectofcollaboration.entity import Entity
from dace.descriptors import SharedMultipleProperty, SharedUniqueProperty
from pontus.schema import Schema, omit, select
from pontus.core import VisualisableElement, VisualisableElementSchema
from pontus.widget import (
    Select2Widget,
    SimpleMappingWidget,
    SequenceWidget)
from deform_treepy.widget import (
    DictSchemaType)
from deform_treepy.utilities.tree_utility import tree_to_keywords

from .interface import ISmartFolder
from lac import _
from lac.views.widget import (
    CssWidget,
    TextInputWidget,
    BootstrapIconInputWidget
    )
from lac import core
from lac import CLASSIFICATIONS, VIEW_TYPES
from lac.views.filter import FilterSchema as FilterSchemaOrigine
from lac.utilities.utils import get_site_folder
from lac.content.keyword import DEFAULT_TREE


DEFAULT_FOLDER_COLORS = {'usual_color': 'white, #2d6ca2',
                         'hover_color': 'white, #2d6ca2'}


class FilterSchema(FilterSchemaOrigine):

    tree = colander.SchemaNode(
        typ=DictSchemaType(),
        widget=core.keyword_widget,
        title=_('Categories'),
        description=_('You can select the categories of the contents to be displayed.'),
        default=DEFAULT_TREE,
        missing=None,
        )


def context_is_a_smartfolder(context, request):
    return request.registry.content.istype(context, 'smartfolder')


@colander.deferred
def types_widget(node, kw):
    values = [(key, getattr(c, 'type_title', c.__class__.__name__)) for key, c
              in list(core.SEARCHABLE_CONTENTS.items())]
    return Select2Widget(values=values,
                         multiple=True)


@colander.deferred
def classifications_widget(node, kw):
    values = [(f.classification_id, f.title) for f
              in list(CLASSIFICATIONS.values())]
    values.insert(0, ('', _('- Select -')))
    return Select2Widget(css_class="classification-field",
                         values=values)


@colander.deferred
def view_type_widget(node, kw):
    values = list(VIEW_TYPES.items())
    values.insert(0, ('', _('- Select -')))
    return Select2Widget(css_class="viewtype-field",
                         values=values)


@colander.deferred
def classifications_seq_widget(node, kw):
    return SequenceWidget(
        css_class="classifications-field",
        orderable=True,
        max_len=len(CLASSIFICATIONS),
        add_subitem_text_template=_('Add a new classification'))


class CssSchema(Schema):
    usual_color = colander.SchemaNode(
        colander.String(),
        widget=CssWidget(),
        title=_('Usual color'),
        # description=('Choisir la couleur du texte et du fond de la section de menu.'),
        description=_('Choose the text and background color of the menu section.'),
        )

    hover_color = colander.SchemaNode(
        colander.String(),
        widget=CssWidget(),
        title=_('Hover color'),
        # description=('Choisir la couleur du texte et du fond de la section de menu au survol de la souris.'),
        description=_('Choose the text and background color of the menu section on mouse-over.')
        )


class SmartFolderSchema(VisualisableElementSchema):
    """Schema for keyword"""

    name = NameSchemaNode(
        editing=context_is_a_smartfolder,
        )

    title = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(css_class="smartfolder-title-field"),
        title=_('Title'),
        )

    icon_data = colander.SchemaNode(
        DictSchemaType(),
        widget=BootstrapIconInputWidget(),
        title=_('Icon'),
        default={'icon': 'glyphicon-folder-open',
                 'icon_class': 'glyphicon'},
        description=_('Select an icon.')
        # description="Sélectionner une icône."
        )

    description = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=4, cols=60),
        title=_("Description"),
        )

    filters = colander.SchemaNode(
        colander.Sequence(),
        omit(select(FilterSchema(
                                name='filter',
                                title=_('Filter'),
                                widget=SimpleMappingWidget(
                                css_class='object-well default-well')),
                         ['metadata_filter', 'geographic_filter',
                          'temporal_filter', 'contribution_filter',
                          'text_filter', 'other_filter']),
             ["_csrf_token_"]),
        widget=SequenceWidget(
            min_len=1,
            add_subitem_text_template=_('Add a new filter')))

    classifications = colander.SchemaNode(
        colander.Sequence(),
        colander.SchemaNode(
            colander.String(),
            widget=classifications_widget,
            name=_("Classification")
            ),
        widget=classifications_seq_widget,
        title=_('Classifications'),
        description=_('You can select one or more options of classification.'),
        missing=[]
        )

    add_as_a_block = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Add as a block'),
        title='',
        description=_('You can add as a block to the home page.'),
        # description=('Vous pouvez ajouter en tant que bloc sur la page d\'accueil'),
        default=False,
        missing=False
        )

    style = omit(CssSchema(widget=SimpleMappingWidget()), ["_csrf_token_"])

    view_type = colander.SchemaNode(
        colander.String(),
        widget=view_type_widget,
        title=_("View type"),
        default='default'
        )

    @invariant
    def classification_invariant(self, appstruct):
        if appstruct.get('view_type', 'default') == 'bloc' and\
           appstruct['classifications']:
            raise colander.Invalid(
                self, _('The bloc view is not classifiable! Please remove all classifications.'))


@content(
    'smartfolder',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(ISmartFolder)
class SmartFolder(VisualisableElement, Entity):
    """SmartFolder class"""

    default_icon = 'glyphicon glyphicon-folder-open'
    name = renamer()
    children = SharedMultipleProperty('children', 'parents')
    parents = SharedMultipleProperty('parents', 'children')
    author = SharedUniqueProperty('author', 'folders')

    def __init__(self, **kwargs):
        super(SmartFolder, self).__init__(**kwargs)
        self.set_data(kwargs)
        self.source_site = get_oid(
            get_site_folder(True), None)
        self.folder_order = PersistentDict({})
        self._keywords_ = []
        self._init_keywords()
        self.access_control = PersistentList([self.source_site])

    @property
    def parent(self):
        parents = self.parents
        return parents[0] if parents else None

    @property
    def root(self):
        parent = self.parent
        return parent.root if parent else self

    @property
    def folder_lineage(self):
        result = [self]
        parent = self.parent
        if parent:
            parent_result = parent.folder_lineage
            parent_result.extend(result)
            result = parent_result

        return result

    @property
    def icon(self):
        icon = getattr(self, 'icon_data', {})
        if icon:
            return icon.get('icon_class') + ' ' + icon.get('icon')
        else:
            return self.default_icon

    @property
    def url(self,):
        request = get_current_request()
        return self.get_url(request)

    def _init_keywords(self):
        alltrees = [f.get('metadata_filter', {}).get('tree', {})
                    for f in getattr(self, 'filters', [])]
        keywords = [tree_to_keywords(tree) for tree in alltrees]
        keywords = list(set([item for sublist in keywords for item in sublist]))
        self._keywords_ = keywords

    def contains(self, folder):
        if folder is None:
            return False

        if folder is self:
            return True

        return any(c.contains(folder) for c in self.children)

    def all_sub_folders(self, state=None):
        if state:
            result = [f for f in self.children if state in f.state]
        else:
            result = list(self.children)

        for sub_f in list(result):
            result.extend(sub_f.all_sub_folders(state))

        return list(set(result))

    def get_folder_with_content(self, content_types, state=None):
        folders = self.all_sub_folders(state)
        if state and state in self.state:
            folders.append(self)

        def filter_op(content_types):
            def op(x):
                filters = getattr(x, 'filters', [])
                folder_content_types = [f.get('metadata_filter', {}).get(
                                        'content_types', content_types)
                                        for f in filters
                                        if not f.get('metadata_filter', {}).get(
                                            'negation', False)]
                folder_content_types = set([item for sublist
                                            in folder_content_types
                                            for item in sublist])
                return any(c in folder_content_types for c in content_types)

            return op

        valid_folders = filter(filter_op(content_types), folders)
        for folder in valid_folders:
            return folder

        return None

    def get_all_keywords(self):
        if hasattr(self, '_keywords_'):
            return self._keywords_
        self._init_keywords()
        return self._keywords_.copy()

    def __setattr__(self, name, value):
        super(SmartFolder, self).__setattr__(name, value)
        if name == 'filters':
            self._init_keywords()

    def get_order(self, site_id):
        folder_order = getattr(self, 'folder_order', {}).get(site_id, None)
        if folder_order is None:
            root = self.__parent__
            folders = root.smart_folders
            if self in folders:
                self.set_order(site_id, folders.index(self))

        return getattr(self, 'folder_order', {}).get(site_id, 0)

    def set_order(self, site_id, order):
        if not hasattr(self, 'folder_order'):
            self.folder_order = PersistentDict({site_id: order})
        else:
            self.folder_order[site_id] = order

    def get_url(self, request):
        return request.resource_url(
            request.root, 'open', query={'folderid': get_oid(self)})


def generate_search_smart_folder(name, classifications=('section_classification',
                                                        'city_classification')):
    folder = SmartFolder(title=name,
                         style=DEFAULT_FOLDER_COLORS)
    folder.__name__ = name.lower()
    source_classification = None
    for classification in reversed(classifications):
        source_classification = CLASSIFICATIONS[classification](
            source_classification)

    folder.classifications = source_classification
    return folder
