# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import deform
import hashlib
from functools import reduce
from zope.interface import implementer

from substanced.schema import NameSchemaNode
from substanced.content import content
from substanced.util import get_oid

from dace.descriptors import (
    CompositeUniqueProperty,
    SharedUniqueProperty,
    SharedMultipleProperty)
from dace.util import getSite
from pontus.core import VisualisableElementSchema
from pontus.widget import (
    FileWidget
    )
from pontus.file import ObjectData
from pontus.form import FileUploadTempStore

from lac import _
from lac.core import (
    VisualisableElement,
    SearchableEntity,
    SearchableEntitySchema,
    DuplicableEntity,
    ParticipativeEntity)
from lac.content.interface import IArtistInformationSheet
from lac.file import Image
from lac.views.widget import RichTextWidget
from lac.utilities.duplicates_utility import (
    find_duplicates_artist)


@colander.deferred
def picture_widget(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    tmpstore = FileUploadTempStore(request)
    source = None
    root = getSite()
    if context is not root:
        if context.picture:
            source = context.picture

    return FileWidget(
        tmpstore=tmpstore,
        source=source,
        file_type=['image']
        )


def context_is_a_artist(context, request):
    return request.registry.content.istype(context, 'artist')


class ArtistInformationSheetSchema(VisualisableElementSchema, SearchableEntitySchema):
    """Schema for artist"""

    name = NameSchemaNode(
        editing=context_is_a_artist,
        )

    id = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title=_('Id'),
        missing=""
        )

    title = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title=_('Title')
        )

    description = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=4, cols=60),
        title=_('Description'),
        missing=""
        )

    biography = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        title=_("Biography"),
        missing=""
        )

    picture = colander.SchemaNode(
        ObjectData(Image),
        widget=picture_widget,
        title=_('Picture'),
        required=False,
        missing=None,
        )

    is_director = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Is a director'),
        title='',
        default=False,
        missing=False
        )

    origin_oid = colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.HiddenWidget(),
        title=_('OID'),
        missing=0
        )


def get_artist_data(artists, artist_schema):
    result = []
    for artist in artists:
        artist_data = artist.get_data(artist_schema)
        if artist_data['picture']:
            picture = artist_data['picture']
            artist_data['picture'] = picture.get_data(None)

        result.append(artist_data)

    return result


@content(
    'artist',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IArtistInformationSheet)
class ArtistInformationSheet(VisualisableElement, DuplicableEntity,
                             ParticipativeEntity, SearchableEntity):
    """Artist information sheet class"""

    type_title = _('Artist information sheet')
    icon = 'glyphicon glyphicon-star'
    templates = {'default': 'lac:views/templates/artist_result.pt',
                 'bloc': 'lac:views/templates/artist_result.pt',
                 'diff': 'lac:views/templates/diff_artist_template.pt',
                 'duplicates': 'lac:views/templates/artist_duplicates.pt'}
    picture = CompositeUniqueProperty('picture')
    author = SharedUniqueProperty('author', 'contents')
    creations = SharedMultipleProperty('creations', 'artists')
    productions = SharedMultipleProperty('productions', 'artists')

    def __init__(self, **kwargs):
        super(ArtistInformationSheet, self).__init__(**kwargs)
        self.hash_picture = None
        self.hash_artist = None
        self.hash_picture_fp()
        self.hash_artist_data()

    @property
    def id(self):
        return self.get_id()

    def hash_picture_fp(self):
        if self.picture:
            m = hashlib.md5()
            picture_r = self.picture.fp.readall()
            self.picture.fp.seek(0)
            m.update(picture_r)
            self.hash_picture = m.digest()
        else:
            self.hash_picture = None

    @property
    def related_contents(self):
        result = list(self.creations)
        result.extend(list(self.productions))
        return result

    @property
    def improved_artist(self):
        original = getattr(self, 'original', None)
        return original if original is not self else None

    def get_id(self):
        return str(get_oid(self, 0))

    def replace_by(self, source):
        if self is not source:
            creations = source.creations
            productions = source.productions
            connections_to = source.connections_to
            for creation in self.creations:
                if creation not in creations:
                    source.addtoproperty('creations', creation)
                    creation.reindex()

            self.setproperty('creations', [])
            for production in self.productions:
                if production not in productions:
                    source.addtoproperty('productions', production)
                    production.reindex()

            self.setproperty('productions', [])
            for connection in self.connections_to:
                if connection not in connections_to:
                    source.addtoproperty('connections_to', connection)

            self.setproperty('connections_to', [])
            for branch in self.branches:
                source.addtoproperty('branches', branch)

            original = self.original
            if original and original is not source:
                source.setproperty('original', original)
                self.setproperty('original', None)

            source.add_contributors(self.contributors)
            self.setproperty('branches', [])
            return True

        return False

    def reject(self):
        original = self.original
        if original:
            self.replace_by(original)

    def hash_artist_data(self):
        result = self.title
        result += getattr(self, 'description', '')
        result += getattr(self, 'biography', '')
        result += str(getattr(self, 'is_director', False))
        result += str(self.hash_picture)
        result = result.replace(' ', '').strip()
        m = hashlib.md5()
        m.update(result.encode())
        self.hash_artist = m.digest()

    def eq(self, other):
        hash_artist = getattr(self, 'hash_artist', None)
        other_hash_artist = getattr(other, 'hash_artist', None)
        if hash_artist != other_hash_artist:
            return False

        return True

    def get_more_contents_criteria(self):
        "return specific query, filter values"
        artists = reduce(lambda result, x: result + getattr(x, 'artists', []),
                         filter(lambda x: 'published' in x.state, self.creations), [])
        artists = filter(lambda x: 'published' in x.state, artists)
        return None, {'objects': set(artists)}

    def get_duplicates(self, states=('published', )):
        return find_duplicates_artist(self, states)
