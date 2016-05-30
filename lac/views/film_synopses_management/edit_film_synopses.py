# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.file import get_file_data
from lac.content.artist import get_artist_data
from lac.content.processes.film_synopses_management.behaviors import (
    EditFilmSynopses)
from lac.content.film_synopses import (
    FilmSynopsesSchema, FilmSynopses)
from lac import _


@view_config(
    name='editfilmsynopses',
    context=FilmSynopses,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditFilmSynopsesView(FormView):

    title = _('Edit the film synopsis')
    schema = select(FilmSynopsesSchema(omit=('artists_ids', 'artists',
                                             'directors', 'directors_ids', 'metadata')),
               ['title', 'film_release_date', 'duration',
                'directors', 'directors_ids',
                'artists_ids', 'artists',
                'nationality', 'picture',
                'tree', 'abstract', 'informations',
                ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [EditFilmSynopses, Cancel]
    formid = 'formeditfilmsynopses'
    name = 'editfilmsynopses'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/artist_management.js',
                                 'lac:static/js/director_management.js']}

    def default_data(self):
        result = self.context.get_data(self.schema)
        result['artists'] = get_artist_data(
            result['artists'], self.schema.get('artists').children[0])
        result['directors'] = get_artist_data(
            result['directors'], self.schema.get('directors').children[0])
        picture = get_file_data(result['picture'])
        result.update(picture)
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditFilmSynopses: EditFilmSynopsesView})
