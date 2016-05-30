# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.default_behavior import Cancel
from pontus.schema import select

from lac.content.processes.services_processes.\
    newsletter_management.behaviors import (
        RedactNewsletter)
from lac.content.newsletter import (
    NewsletterSchema, Newsletter)
from lac import _


@view_config(
    name='redactnewsletter',
    context=Newsletter,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RedactNewsletterView(FormView):

    title = _('Redact a newsletter')
    schema = select(NewsletterSchema(factory=Newsletter, editable=True),
                    ['subject', 'content'])
    behaviors = [RedactNewsletter, Cancel]
    formid = 'formredactnewsletter'
    name = 'redactnewsletter'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RedactNewsletter: RedactNewsletterView})
