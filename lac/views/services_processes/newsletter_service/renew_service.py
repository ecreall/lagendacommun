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
from pontus.schema import select

from lac.content.processes.services_processes.behaviors import (
    RenewNewsletterService)
from lac.content.service import (
    NewsletterServiceSchema, NewsletterService)
from lac import _


class RenewNewsletterServiceViewStudyReport(BasicView):
    title = 'Alert for renew'
    name = 'alertforrenew'
    template = 'lac:views/services_processes/newsletter_service/templates/alert_renew.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RenewNewsletterServiceView(FormView):
    title = _('Renew the newsletter service')
    schema = select(NewsletterServiceSchema(
                    factory=NewsletterService,
                    editable=True), ['title'])
    behaviors = [RenewNewsletterService, Cancel]
    formid = 'formrenewnewsletterservice'
    name = 'renewnewsletterservice'
    validate_behaviors = False

    def default_data(self):
        return self.context


@view_config(
    name='renewnewsletterservice',
    context=NewsletterService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RenewNewsletterServiceViewMultipleView(MultipleView):
    title = _('Renew the newsletter service')
    name = 'renewnewsletterservice'
    viewid = 'renewnewsletterservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RenewNewsletterServiceViewStudyReport, RenewNewsletterServiceView)
    validators = [RenewNewsletterService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RenewNewsletterService: RenewNewsletterServiceViewMultipleView})
