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

from lac.content.processes.brief_management.behaviors import (
    PublishBrief)
from lac.content.brief import (
    Brief)
from lac import _


class PublishBriefViewStudyReport(BasicView):
    title = 'Alert for publishing'
    name = 'alertforpublishing'
    template = 'lac:views/brief_management/templates/alert_event_publishing.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PublishBriefView(FormView):
    title = _('Publish')
    name = 'publishbriefform'
    formid = 'formpublishbrief'
    behaviors = [PublishBrief, Cancel]
    validate_behaviors = False


@view_config(
    name='publishbrief',
    context=Brief,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishBriefViewMultipleView(MultipleView):
    title = _('Publish the news flash')
    name = 'publishbrief'
    viewid = 'publishbrief'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishBriefViewStudyReport, PublishBriefView)
    validators = [PublishBrief.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PublishBrief: PublishBriefViewMultipleView})
