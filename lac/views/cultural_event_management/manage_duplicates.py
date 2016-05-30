# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import get_oid

import html_diff_wrapper
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.content.processes.cultural_event_management.behaviors import (
    ManageDuplicates, get_duplicates)
from lac.content.cultural_event import CulturalEvent
from lac import _


class DoubloonCulturalEventViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/cultural_event_management/templates/alert_doubloon.pt'

    def update(self):
        result = {}
        duplicates = get_duplicates(self.context)
        diff_bodies = {}
        context_view = self.content(
            args={'object': self.context},
            template=self.context.templates.get('diff', None))['body']

        for duplicate in duplicates:
            duplicate_view = self.content(
                args={'object': duplicate},
                template=duplicate.templates.get('diff', None))['body']
            soupt, textdiff = html_diff_wrapper.render_html_diff(
                context_view, duplicate_view)
            diff_bodies[duplicate] = (textdiff, get_oid(duplicate))

        values = {'context': self.context,
                  'oid': get_oid(self.context),
                  'context_view': context_view,
                  'contents': diff_bodies,
                  'view': self}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class DoubloonCulturalEventView(FormView):
    title = _('Remove')
    name = 'removeculturaleventform'
    formid = 'formremoveculturalevent'
    behaviors = [ManageDuplicates]
    validate_behaviors = False


@view_config(
    name='potentialduplicatesculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class DoubloonCulturalEventViewMultipleView(MultipleView):
    title = _('Duplicate detection')
    name = 'potentialduplicatesculturalevent'
    viewid = 'potentialduplicatesculturalevent'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (DoubloonCulturalEventViewStudyReport, DoubloonCulturalEventView)
    validators = [ManageDuplicates.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ManageDuplicates: DoubloonCulturalEventViewMultipleView})
