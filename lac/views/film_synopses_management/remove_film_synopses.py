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

from lac.content.processes.film_synopses_management.behaviors import (
    RemoveFilmSynopses)
from lac.content.film_synopses import FilmSynopses
from lac import _



class RemoveFilmsynopsesViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/film_synopses_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveFilmsynopsesView(FormView):
    title = _('Remove')
    name = 'removefilmsynopsesform'
    formid = 'formremovefilmsynopses'
    behaviors = [RemoveFilmSynopses, Cancel]
    validate_behaviors = False


@view_config(
    name='removefilmsynopses',
    context=FilmSynopses,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveFilmsynopsesViewMultipleView(MultipleView):
    title = _('Remove the film synopsis')
    name = 'removefilmsynopses'
    viewid = 'removefilmsynopses'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveFilmsynopsesViewStudyReport, RemoveFilmsynopsesView)
    validators = [RemoveFilmSynopses.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveFilmSynopses: RemoveFilmsynopsesViewMultipleView})
