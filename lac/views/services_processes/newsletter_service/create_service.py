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
    CreateNewsletterService)
from lac.content.service import (
    NewsletterServiceSchema)
from lac.content.site_folder import (
    SiteFolder)
from lac import _


class CreateNewsletterServiceViewStudyReport(BasicView):
    title = 'Alert for create'
    name = 'alertforcreate'
    template = 'lac:views/services_processes/newsletter_service/templates/alert_create.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class CreateNewsletterServiceView(FormView):

    title = _('Create a newsletter service')
    schema = select(NewsletterServiceSchema(),
               ['title'])
    behaviors = [CreateNewsletterService, Cancel]
    formid = 'formcreatenewsletterservice'
    name = 'createnewsletterservice'
    validate_behaviors = False


@view_config(
    name='createnewsletterservice',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateNewsletterServiceViewMultipleView(MultipleView):
    title = _('Create a newsletter service')
    name = 'createnewsletterservice'
    viewid = 'createnewsletterservice'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (CreateNewsletterServiceViewStudyReport, CreateNewsletterServiceView)
    validators = [CreateNewsletterService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateNewsletterService: CreateNewsletterServiceViewMultipleView})
