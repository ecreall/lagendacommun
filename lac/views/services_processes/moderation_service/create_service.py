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
    CreateModerationService)
from lac.content.service import (
    ModerationServiceSchema)
from lac.content.site_folder import (
    SiteFolder)
from lac import _


class CreateModerationServiceViewStudyReport(BasicView):
    title = 'Alert for create'
    name = 'alertforcreate'
    template = 'lac:views/services_processes/moderation_service/templates/alert_create.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class CreateModerationServiceView(FormView):
    title = _('Create a moderation service')
    schema = select(ModerationServiceSchema(),
               ['title', 'delegate'])
    behaviors = [CreateModerationService, Cancel]
    formid = 'formcreatemoderationservice'
    name = 'createmoderationservice'
    validate_behaviors = False


@view_config(
    name='createmoderationservice',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateModerationServiceViewMultipleView(MultipleView):
    title = _('Create a moderation service')
    name = 'createmoderationservice'
    viewid = 'createmoderationservice'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (CreateModerationServiceViewStudyReport,
             CreateModerationServiceView)
    validators = [CreateModerationService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateModerationService: CreateModerationServiceViewMultipleView})
