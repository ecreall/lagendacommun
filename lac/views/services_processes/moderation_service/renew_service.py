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
    RenewModerationService)
from lac.content.service import ModerationService
from lac import _


class RenewModerationServiceViewStudyReport(BasicView):
    title = 'Alert for renew'
    name = 'alertforrenew'
    template = 'lac:views/services_processes/moderation_service/templates/alert_renew.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RenewModerationServiceView(FormView):
    title = _('Renew the moderation service')
    behaviors = [RenewModerationService, Cancel]
    formid = 'formrenewmoderationservice'
    name = 'renewmoderationservice'
    validate_behaviors = False

    def default_data(self):
        return self.context


@view_config(
    name='renewmoderationservice',
    context=ModerationService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RenewModerationServiceViewMultipleView(MultipleView):
    title = _('Renew the moderation service')
    name = 'renewmoderationservice'
    viewid = 'renewmoderationservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RenewModerationServiceViewStudyReport,
             RenewModerationServiceView)
    validators = [RenewModerationService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RenewModerationService: RenewModerationServiceViewMultipleView})
