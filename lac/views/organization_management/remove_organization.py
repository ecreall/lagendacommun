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

from lac.content.processes.organization_management.behaviors import (
    RemoveOrganization)
from lac.content.organization import Organization
from lac import _


class RemoveOrganizationViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/organization_management/templates/alert_remove_organization.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveOrganizationView(FormView):
    title = _('Remove')
    name = 'removeorganizationform'
    formid = 'formremoveorganization'
    behaviors = [RemoveOrganization, Cancel]
    validate_behaviors = False


@view_config(
    name='removeorganization',
    context=Organization,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveOrganizationViewMultipleView(MultipleView):
    title = _('Remove the organization')
    name = 'removeorganization'
    viewid = 'removeorganization'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveOrganizationViewStudyReport, RemoveOrganizationView)
    validators = [RemoveOrganization.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveOrganization: RemoveOrganizationViewMultipleView})
