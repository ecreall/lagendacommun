# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer, get_oid

from dace.descriptors import (
    SharedUniqueProperty,
    CompositeUniqueProperty,
    SharedMultipleProperty
    )

from lac import _
from lac.core import SearchableEntity
from lac.utilities.utils import html_to_text
from .interface import IFilmSynopses
from .cinema_review import CinemaReviewSchema
from lac.views.widget import RichTextWidget


def context_is_a_film_synopses(context, request):
    return request.registry.content.istype(context, 'film_synopses')


class FilmSynopsesSchema(CinemaReviewSchema):
    """FilmSynopses schema"""

    name = NameSchemaNode(
        editing=context_is_a_film_synopses,
        )

    film_release_date = colander.SchemaNode(
        colander.Date(),
        title=_('Release date')
        )

    abstract = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        title=_("Abstract")
        )


@content(
    'film_synopses',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IFilmSynopses)
class FilmSynopses(SearchableEntity):
    """FilmSynopses class"""

    type_title = _('Film synopsis')
    icon = 'lac-icon icon-film-synopses'
    templates = {'default': 'lac:views/templates/film_synopses_result.pt',
                 'bloc': 'lac:views/templates/film_synopses_result_bloc.pt'}
    name = renamer()
    picture = CompositeUniqueProperty('picture')
    author = SharedUniqueProperty('author', 'contents')
    artists = SharedMultipleProperty('artists', 'creations')
    directors = SharedMultipleProperty('directors', 'productions')

    def __init__(self, **kwargs):
        self._presentation_text = None
        super(FilmSynopses, self).__init__(**kwargs)
        self.set_data(kwargs)

    def _init_presentation_text(self):
        self._presentation_text = html_to_text(
            getattr(self, 'abstract', ''))

    def __setattr__(self, name, value):
        super(FilmSynopses, self).__setattr__(name, value)
        if name == 'abstract':
            self._init_presentation_text()

    @property
    def artists_ids(self):
        return [str(get_oid(a)) for a in self.artists]

    @property
    def directors_ids(self):
        return [str(get_oid(a)) for a in self.directors]

    @property
    def relevant_data(self):
        result = super(FilmSynopses, self).relevant_data
        result.extend([', '.join([a.title for a in self.directors]),
                       ', '.join([a.title for a in self.artists])])
        return result

    def presentation_text(self, nb_characters=400):
        text = getattr(self, '_presentation_text', None)
        if text is None:
            self._init_presentation_text()
            text = getattr(self, '_presentation_text', '')

        return text[:nb_characters]+'...'
