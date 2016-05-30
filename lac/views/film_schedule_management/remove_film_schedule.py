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

from lac.content.processes.film_schedule_management.behaviors import (
    RemoveFilmSchedule)
from lac.content.film_schedule import FilmSchedule
from lac import _


class RemoveFilmscheduleViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/film_schedule_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveFilmscheduleView(FormView):
    title = _('Remove')
    name = 'removefilmscheduleform'
    formid = 'formremovefilmschedule'
    behaviors = [RemoveFilmSchedule, Cancel]
    validate_behaviors = False


@view_config(
    name='removefilmschedule',
    context=FilmSchedule,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveFilmscheduleViewMultipleView(MultipleView):
    title = _('Remove the film session')
    name = 'removefilmschedule'
    viewid = 'removefilmschedule'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveFilmscheduleViewStudyReport, RemoveFilmscheduleView)
    validators = [RemoveFilmSchedule.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveFilmSchedule: RemoveFilmscheduleViewMultipleView})
