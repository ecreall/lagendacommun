# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select
from pontus.file import OBJECT_OID

from lac.file import get_file_data
from lac.content.artist import get_artist_data
from lac.content.processes.base_review_management.behaviors import (
    EditInterview)
from lac.content.interview import (
    InterviewSchema, Interview)
from lac import _


@view_config(
    name='editinterview',
    context=Interview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditInterviewView(FormView):

    title = _('Edit the interview')
    schema = select(InterviewSchema(factory=Interview,
                                    editable=True,
                                    omit=('artists', 'artists_ids', 'metadata')),
               ['title', 'review', 'tree', 'artists_ids', 'artists',
                'picture', 'article',
                'signature', 'informations',
                'accessibility', 'showcase_review',
                ('metadata', ['accessibility', 'object_labels', 'connections_to'])])
    behaviors = [EditInterview, Cancel]
    formid = 'formeditinterview'
    name = 'editinterview'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/artist_management.js']}

    def default_data(self):
        result = self.context.get_data(self.schema)
        result['artists'] = get_artist_data(
            result['artists'], self.schema.get('artists').children[0])
        picture = get_file_data(result['picture'])
        result.update(picture)
        result[OBJECT_OID] = get_oid(self.context)
        return result

DEFAULTMAPPING_ACTIONS_VIEWS.update({EditInterview: EditInterviewView})
