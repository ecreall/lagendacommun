# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.base_review_management.behaviors import (
    CreateCinemaReview)
from lac.content.cinema_review import (
    CinemaReviewSchema, CinemaReview)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='createcinemareview',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateCinemaReviewView(FormView):

    title = _('Create a review')
    schema = select(CinemaReviewSchema(factory=CinemaReview,
                                       editable=True,
                                       omit=('artists', 'artists_ids',
                                             'directors', 'directors_ids',
                                             'metadata')),
               ['title', 'surtitle',
                'tree', 'duration',
                'directors', 'directors_ids',
                'artists_ids', 'artists',
                'nationality', 'picture',
                'article', 'appreciation',
                'opinion', 'signature',
                'informations', 'showcase_review',
                ('metadata', ['accessibility', 'object_labels', 'connections_to', 'visibility_dates'])])
    behaviors = [CreateCinemaReview, Cancel]
    formid = 'formcreatecinemareview'
    name = 'createcinemareview'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/artist_management.js',
                                 'lac:static/js/director_management.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateCinemaReview: CreateCinemaReviewView})
