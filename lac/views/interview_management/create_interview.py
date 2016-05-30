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
    CreateInterview)
from lac.content.interview import (
    InterviewSchema, Interview)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='createinterview',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateInterviewView(FormView):

    title = _('Create an interview')
    schema = select(InterviewSchema(factory=Interview,
                                    editable=True,
                                    omit=('artists', 'artists_ids', 'metadata')),
               ['title', 'review', 'tree', 'artists_ids', 'artists',
                'picture', 'article',
                'signature', 'informations',
                'showcase_review',
                ('metadata', ['accessibility', 'object_labels', 'connections_to'])])
    behaviors = [CreateInterview, Cancel]
    formid = 'formcreateinterview'
    name = 'createinterview'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/contextual_help_interview.js',
                                 'lac:static/js/artist_management.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update({CreateInterview: CreateInterviewView})
