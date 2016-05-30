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
        CreateNewsletter)
from lac.content.newsletter import (
    NewsletterSchema, Newsletter)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='createnewsletter',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateNewsletterView(FormView):

    title = _('Create a newsletter')
    schema = select(NewsletterSchema(factory=Newsletter, editable=True),
                    ['title', 'description', 'content_template'])
    behaviors = [CreateNewsletter, Cancel]
    formid = 'formcreatenewsletter'
    name = 'createnewsletter'


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateNewsletter: CreateNewsletterView})
