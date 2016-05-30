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
    CreateImportService)
from lac.content.service import (
    ImportServiceSchema)
from lac.content.site_folder import (
    SiteFolder)
from lac import _


class CreateImportServiceViewStudyReport(BasicView):
    title = 'Alert for create'
    name = 'alertforcreate'
    template = 'lac:views/services_processes/import_service/templates/alert_create.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class CreateImportServiceView(FormView):

    title = _('Create an import service')
    schema = select(ImportServiceSchema(),
               ['title', 'sources'])
    behaviors = [CreateImportService, Cancel]
    formid = 'formcreateimportservice'
    name = 'createimportservice'
    validate_behaviors = False


@view_config(
    name='createimportservice',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateImportServiceViewMultipleView(MultipleView):
    title = _('Create an import service')
    name = 'createimportservice'
    viewid = 'createimportservice'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (CreateImportServiceViewStudyReport, CreateImportServiceView)
    validators = [CreateImportService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateImportService: CreateImportServiceViewMultipleView})
