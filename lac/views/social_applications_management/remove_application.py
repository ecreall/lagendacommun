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

from lac.content.processes.social_applications_management.behaviors import (
    RemoveApplication)
from lac.content.social_application import Application
from lac import _


class RemoveApplicationViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/social_applications_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveApplicationView(FormView):
    title = _('Remove')
    name = 'removeapplicationform'
    formid = 'formremoveapplication'
    behaviors = [RemoveApplication, Cancel]
    validate_behaviors = False


@view_config(
    name='removeapplication',
    context=Application,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveApplicationViewMultipleView(MultipleView):
    title = _('Remove the application')
    name = 'removeapplication'
    viewid = 'removeapplication'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveApplicationViewStudyReport, RemoveApplicationView)
    validators = [RemoveApplication.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveApplication: RemoveApplicationViewMultipleView})
