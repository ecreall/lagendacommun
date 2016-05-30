# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit

from lac.file import get_file_data
from lac.content.artist import get_artist_data
from lac.content.processes.base_review_management.behaviors import (
    EditCinemaReview)
from lac.content.cinema_review import (
    CinemaReviewSchema, CinemaReview)
from lac import _


@view_config(
    name='editcinemareview',
    context=CinemaReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditCinemaReviewView(FormView):

    title = _('Edit the review')
    schema = select(CinemaReviewSchema(omit=('artists', 'artists_ids',
                                             'directors', 'directors_ids',
                                             'metadata')),
               ['title', 'surtitle',
                'tree', 'duration',
                'directors', 'directors_ids',
                'artists_ids', 'artists',
                'nationality', 'picture',
                'article', 'appreciation',
                'opinion', 'signature',
                'informations', 'accessibility', 'showcase_review',
                ('metadata', ['accessibility', 'object_labels', 'connections_to',
                              'release_date', 'visibility_dates'])])
    behaviors = [EditCinemaReview, Cancel]
    formid = 'formeditcinemareview'
    name = 'editcinemareview'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/artist_management.js',
                                'lac:static/js/director_management.js']}

    def before_update(self):
        if 'published' not in self.context.state:
            self.schema = omit(self.schema, [('metadata', ['release_date'])])

    def default_data(self):
        result = self.context.get_data(self.schema)
        result['artists'] = get_artist_data(
            result['artists'], self.schema.get('artists').children[0])
        result['directors'] = get_artist_data(
            result['directors'], self.schema.get('directors').children[0])
        picture = get_file_data(result['picture'])
        result.update(picture)
        return result

DEFAULTMAPPING_ACTIONS_VIEWS.update({EditCinemaReview: EditCinemaReviewView})
