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
    CreateReview)
from lac.content.review import (
    ReviewSchema, Review)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='createreview',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateReviewView(FormView):

    title = _('Create a review')
    schema = select(ReviewSchema(factory=Review,
                                 editable=True,
                                 omit=('artists', 'artists_ids', 'metadata')),
                    ['title', 'surtitle', 'tree', 'artists_ids', 'artists',
                     'picture', 'article',
                     'signature',
                     'informations', 'showcase_review',
                     ('metadata', ['accessibility', 'object_labels', 'connections_to', 'visibility_dates'])])
    behaviors = [CreateReview, Cancel]
    formid = 'formcreatereview'
    name = 'createreview'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/artist_management.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update({CreateReview: CreateReviewView})
