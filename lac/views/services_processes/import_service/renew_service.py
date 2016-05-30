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
    RenewImportService)
from lac.content.service import ImportService
from lac import _


class RenewImportServiceViewStudyReport(BasicView):
    title = 'Alert for renew'
    name = 'alertforrenew'
    template = 'lac:views/services_processes/import_service/templates/alert_renew.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RenewImportServiceView(FormView):
    title = _('Renew the import service')
    behaviors = [RenewImportService, Cancel]
    formid = 'formrenewimportservice'
    name = 'renewimportservice'
    validate_behaviors = False

    def default_data(self):
        return self.context


@view_config(
    name='renewimportservice',
    context=ImportService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RenewImportServiceViewMultipleView(MultipleView):
    title = _('Renew the import service')
    name = 'renewimportservice'
    viewid = 'renewimportservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RenewImportServiceViewStudyReport, RenewImportServiceView)
    validators = [RenewImportService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RenewImportService: RenewImportServiceViewMultipleView})

