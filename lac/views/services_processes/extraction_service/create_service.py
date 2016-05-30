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
    CreateExtractionService)
from lac.content.service import (
    ExtractionServiceSchema)
from lac.content.site_folder import (
    SiteFolder)
from lac import _


class CreateExtractionServiceViewStudyReport(BasicView):
    title = 'Alert for create'
    name = 'alertforcreate'
    template = 'lac:views/services_processes/extraction_service/templates/alert_create.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class CreateExtractionServiceView(FormView):

    title = _('Create an extraction service')
    schema = select(ExtractionServiceSchema(),
               ['title', 'has_periodic'])
    behaviors = [CreateExtractionService, Cancel]
    formid = 'formcreateextractionservice'
    name = 'createextractionservice'
    validate_behaviors = False


@view_config(
    name='createextractionservice',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateExtractionServiceViewMultipleView(MultipleView):
    title = _('Create an extraction service')
    name = 'createextractionservice'
    viewid = 'createextractionservice'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (CreateExtractionServiceViewStudyReport, CreateExtractionServiceView)
    validators = [CreateExtractionService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateExtractionService: CreateExtractionServiceViewMultipleView})
