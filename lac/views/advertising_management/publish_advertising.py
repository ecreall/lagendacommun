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

from lac.content.processes.advertising_management.behaviors import (
    PublishAdvertising)
from lac.core import Advertising
from lac import _



class PublishAdvertisingViewStudyReport(BasicView):
    title = 'Alert for publishing'
    name = 'alertforpublishing'
    template = 'lac:views/advertising_management/templates/alert_publishing.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PublishAdvertisingView(FormView):
    title = _('Publish')
    name = 'publishadvertisingform'
    formid = 'formpublishadvertising'
    behaviors = [PublishAdvertising, Cancel]
    validate_behaviors = False


@view_config(
    name='publishadvertising',
    context=Advertising,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishAdvertisingViewMultipleView(MultipleView):
    title = _('Publish the advertisement')
    name = 'publishadvertising'
    viewid = 'publishadvertising'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishAdvertisingViewStudyReport, PublishAdvertisingView)
    validators = [PublishAdvertising.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PublishAdvertising: PublishAdvertisingViewMultipleView})
