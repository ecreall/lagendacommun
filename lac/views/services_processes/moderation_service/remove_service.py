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
    RemoveModerationService)
from lac.content.service import ModerationService
from lac import _


class RemoveModerationServiceViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/services_processes/moderation_service/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveModerationServiceView(FormView):
    title = _('Remove')
    name = 'removemoderationserviceform'
    formid = 'formremovemoderationservice'
    behaviors = [RemoveModerationService, Cancel]
    validate_behaviors = False


@view_config(
    name='removemoderationservice',
    context=ModerationService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveModerationServiceViewMultipleView(MultipleView):
    title = _('Remove the service')
    name = 'removemoderationservice'
    viewid = 'removemoderationservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveModerationServiceViewStudyReport,
             RemoveModerationServiceView)
    validators = [RemoveModerationService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveModerationService: RemoveModerationServiceViewMultipleView})
