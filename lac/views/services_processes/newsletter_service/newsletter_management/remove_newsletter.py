# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config


from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.content.processes.services_processes.\
    newsletter_management.behaviors import (
        RemoveNewsletter)
from lac.content.newsletter import (
    Newsletter)
from lac import _


class RemoveNewsletterViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/services_processes/newsletter_service/newsletter_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveNewsletterView(FormView):
    title = _('Remove')
    name = 'removenewsletterform'
    formid = 'formremovenewsletter'
    behaviors = [RemoveNewsletter, Cancel]
    validate_behaviors = False


@view_config(
    name='removenewsletter',
    context=Newsletter,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveNewsletterViewMultipleView(MultipleView):
    title = _('Remove the newsletter')
    name = 'removenewsletter'
    viewid = 'removenewsletter'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveNewsletterViewStudyReport, RemoveNewsletterView)
    validators = [RemoveNewsletter.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveNewsletter: RemoveNewsletterViewMultipleView})
