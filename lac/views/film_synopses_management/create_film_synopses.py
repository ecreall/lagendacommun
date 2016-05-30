# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.film_synopses_management.behaviors import (
    CreateFilmSynopses)
from lac.content.film_synopses import (
    FilmSynopsesSchema, FilmSynopses)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='createfilmsynopses',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateFilmSynopsesView(FormView):

    title = _('Create a film synopsis')
    schema = select(FilmSynopsesSchema(factory=FilmSynopses,
                                       editable=True,
                                       omit=('artists_ids', 'artists',
                                             'directors', 'directors_ids', 'metadata')),
               ['title', 'film_release_date', 'duration',
                'directors', 'directors_ids',
                'artists_ids', 'artists',
                'nationality', 'picture',
                'tree', 'abstract', 'informations', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [CreateFilmSynopses, Cancel]
    formid = 'formcreatefilmsynopses'
    name = 'createfilmsynopses'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/artist_management.js',
                                 'lac:static/js/director_management.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateFilmSynopses: CreateFilmSynopsesView})
