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
    RemoveBrief)
from lac.content.brief import Brief
from lac import _


class RemoveBriefViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/brief_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveBriefView(FormView):
    title = _('Remove')
    name = 'removebriefform'
    formid = 'formremovebrief'
    behaviors = [RemoveBrief, Cancel]
    validate_behaviors = False


@view_config(
    name='removebrief',
    context=Brief,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveBriefViewMultipleView(MultipleView):
    title = _('Remove the news flash')
    name = 'removebrief'
    viewid = 'removebrief'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveBriefViewStudyReport, RemoveBriefView)
    validators = [RemoveBrief.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update({RemoveBrief: RemoveBriefViewMultipleView})
