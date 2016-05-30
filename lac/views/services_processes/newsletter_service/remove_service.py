# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView
from pontus.form import FormView
from pontus.default_behavior import Cancel
from pontus.view_operation import MultipleView

from lac.content.processes.services_processes.behaviors import (
    RemoveNewsletterService)
from lac.content.service import NewsletterService
from lac import _


class RemoveNewsletterServiceViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/services_processes/newsletter_service/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveNewsletterServiceView(FormView):
    title = _('Remove')
    name = 'removenewsletterserviceform'
    formid = 'formremovenewsletterservice'
    behaviors = [RemoveNewsletterService, Cancel]
    validate_behaviors = False


@view_config(
    name='removenewsletterservice',
    context=NewsletterService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveNewsletterServiceViewMultipleView(MultipleView):
    title = _('Remove the service')
    name = 'removenewsletterservice'
    viewid = 'removenewsletterservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveNewsletterServiceViewStudyReport, RemoveNewsletterServiceView)
    validators = [RemoveNewsletterService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveNewsletterService: RemoveNewsletterServiceViewMultipleView})
