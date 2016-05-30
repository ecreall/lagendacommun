# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.services_processes.behaviors import (
    EditNewsletterService)
from lac.content.service import (
    NewsletterServiceSchema, NewsletterService)
from lac import _


@view_config(
    name='editnewsletterservice',
    context=NewsletterService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditNewsletterServiceView(FormView):

    title = _('Edit a newsletter service')
    schema = select(NewsletterServiceSchema(factory=NewsletterService,
                                            editable=True),
               ['title'])
    behaviors = [EditNewsletterService, Cancel]
    formid = 'formeditnewsletterservice'
    name = 'editnewsletterservice'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditNewsletterService: EditNewsletterServiceView})
