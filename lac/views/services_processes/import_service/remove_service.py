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
    RemoveImportService)
from lac.content.service import ImportService
from lac import _


class RemoveImportServiceViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/services_processes/import_service/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveImportServiceView(FormView):
    title = _('Remove')
    name = 'removeimportserviceform'
    formid = 'formremoveimportservice'
    behaviors = [RemoveImportService, Cancel]
    validate_behaviors = False


@view_config(
    name='removeimportservice',
    context=ImportService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveImportServiceViewMultipleView(MultipleView):
    title = _('Remove the service')
    name = 'removeimportservice'
    viewid = 'removeimportservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveImportServiceViewStudyReport, RemoveImportServiceView)
    validators = [RemoveImportService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveImportService: RemoveImportServiceViewMultipleView})
