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
    ArchiveBrief)
from lac.content.brief import (
    Brief)
from lac import _


class ArchiveBriefViewStudyReport(BasicView):
    title = 'Alert for archive'
    name = 'alertforarchive'
    template = 'lac:views/brief_management/templates/alert_event_archive.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ArchiveBriefView(FormView):
    title = _('Archive')
    name = 'Archivebriefform'
    formid = 'formarchivebrief'
    behaviors = [ArchiveBrief, Cancel]
    validate_behaviors = False


@view_config(
    name='archivebrief',
    context=Brief,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ArchiveBriefViewMultipleView(MultipleView):
    title = _('Archive the news flash')
    name = 'archivebrief'
    viewid = 'archivebrief'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ArchiveBriefViewStudyReport, ArchiveBriefView)
    validators = [ArchiveBrief.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ArchiveBrief: ArchiveBriefViewMultipleView})
