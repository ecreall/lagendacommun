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
    PutOnHoldFilmSynopses)
from lac.content.film_synopses import (
    FilmSynopses)
from lac import _



class PutOnHoldFilmSynopsesViewStudyReport(BasicView):
    title = 'Alert for submission'
    name = 'alertforsubmission'
    template = 'lac:views/film_synopses_management/templates/alert_event_submission.pt'

    def update(self):
        result = {}
        not_published_artists = [a for a in self.context.artists
                                 if 'published' not in a.state]
        values = {'not_published_artists': not_published_artists}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PutOnHoldFilmSynopsesView(FormView):
    title = _('Put on hold')
    name = 'putonholdfilmsynopsesform'
    formid = 'formputonholdfilmsynopses'
    behaviors = [PutOnHoldFilmSynopses, Cancel]
    validate_behaviors = False


@view_config(
    name='putonholdfilmsynopses',
    context=FilmSynopses,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PutOnHoldFilmSynopsesViewMultipleView(MultipleView):
    title = _('Put on hold the film synopses')
    name = 'putonholdfilmsynopses'
    viewid = 'putonholdfilmsynopses'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PutOnHoldFilmSynopsesViewStudyReport, PutOnHoldFilmSynopsesView)
    validators = [PutOnHoldFilmSynopses.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PutOnHoldFilmSynopses: PutOnHoldFilmSynopsesViewMultipleView})
