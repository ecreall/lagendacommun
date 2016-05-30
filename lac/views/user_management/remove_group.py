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

from lac.content.processes.user_management.behaviors import (
    RemoveGroup)
from lac.content.person import Group
from lac import _


class RemoveGroupViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/user_management/templates/alert_remove_group.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveGroupView(FormView):
    title = _('Remove')
    name = 'removegroupform'
    formid = 'formremovegroup'
    behaviors = [RemoveGroup, Cancel]
    validate_behaviors = False


@view_config(
    name='removegroup',
    context=Group,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveGroupViewMultipleView(MultipleView):
    title = _('Remove the group')
    name = 'removegroup'
    viewid = 'removegroup'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveGroupViewStudyReport, RemoveGroupView)
    validators = [RemoveGroup.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveGroup: RemoveGroupViewMultipleView})
