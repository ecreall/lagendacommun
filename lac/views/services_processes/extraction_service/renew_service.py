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
    RenewExtractionService)
from lac.content.service import (
    ExtractionServiceSchema, ExtractionService)
from lac import _


class RenewExtractionServiceViewStudyReport(BasicView):
    title = 'Alert for renew'
    name = 'alertforrenew'
    template = 'lac:views/services_processes/extraction_service/templates/alert_renew.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RenewExtractionServiceView(FormView):
    title = _('Renew the extraction service')
    schema = select(ExtractionServiceSchema(
                    factory=ExtractionService,
                    editable=True),
                    ['title', 'sources'])
    behaviors = [RenewExtractionService, Cancel]
    formid = 'formrenewextractionservice'
    name = 'renewextractionservice'
    validate_behaviors = False

    def default_data(self):
        return self.context


@view_config(
    name='renewextractionservice',
    context=ExtractionService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RenewExtractionServiceViewMultipleView(MultipleView):
    title = _('Renew the extraction service')
    name = 'renewextractionservice'
    viewid = 'renewextractionservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RenewExtractionServiceViewStudyReport, RenewExtractionServiceView)
    validators = [RenewExtractionService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RenewExtractionService: RenewExtractionServiceViewMultipleView})
