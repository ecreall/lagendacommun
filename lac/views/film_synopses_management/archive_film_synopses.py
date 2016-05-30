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
    ArchiveFilmSynopses)
from lac.content.film_synopses import (
    FilmSynopses)
from lac import _



class ArchiveFilmSynopsesViewStudyReport(BasicView):
    title = 'Alert for archive'
    name = 'alertforarchive'
    template = 'lac:views/film_synopses_management/templates/alert_event_archive.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ArchiveFilmSynopsesView(FormView):
    title = _('Archive')
    name = 'Archivefilmsynopsesform'
    formid = 'formarchivefilmsynopses'
    behaviors = [ArchiveFilmSynopses, Cancel]
    validate_behaviors = False


@view_config(
    name='archivefilmsynopses',
    context=FilmSynopses,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ArchiveFilmSynopsesViewMultipleView(MultipleView):
    title = _('Archive the film synopsis')
    name = 'archivefilmsynopses'
    viewid = 'archivefilmsynopses'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ArchiveFilmSynopsesViewStudyReport, ArchiveFilmSynopsesView)
    validators = [ArchiveFilmSynopses.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ArchiveFilmSynopses: ArchiveFilmSynopsesViewMultipleView})
