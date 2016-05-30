# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit
from pontus.file import OBJECT_OID

from lac.file import get_file_data
from lac.content.artist import get_artist_data
from lac.content.processes.base_review_management.behaviors import (
    EditReview)
from lac.content.review import (
    ReviewSchema, Review)
from lac import _


@view_config(
    name='editreview',
    context=Review,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditReviewView(FormView):

    title = _('Edit the review')
    schema = select(ReviewSchema(factory=Review,
                                 editable=True,
                                 omit=('artists', 'artists_ids', 'metadata')),
                    ['title', 'surtitle', 'tree', 'artists_ids', 'artists',
                     'picture', 'article',
                     'signature', 'informations',
                     'showcase_review',
                     ('metadata', ['accessibility', 'object_labels',
                                   'connections_to', 'release_date',
                                   'visibility_dates'])])
    behaviors = [EditReview, Cancel]
    formid = 'formeditreview'
    name = 'editreview'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/artist_management.js']}

    def before_update(self):
        if 'published' not in self.context.state:
            self.schema = omit(self.schema, [('metadata', ['release_date'])])

    def default_data(self):
        result = self.context.get_data(self.schema)
        result['artists'] = get_artist_data(
            result['artists'], self.schema.get('artists').children[0])
        picture = get_file_data(result['picture'])
        result.update(picture)
        result[OBJECT_OID] = get_oid(self.context)
        return result

DEFAULTMAPPING_ACTIONS_VIEWS.update({EditReview: EditReviewView})
