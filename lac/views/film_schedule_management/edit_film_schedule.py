# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.film_schedule_management.behaviors import (
    EditFilmSchedule)
from lac.content.film_schedule import (
    FilmScheduleSchema, FilmSchedule)
from lac import _


@view_config(
    name='editfilmschedule',
    context=FilmSchedule,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditFilmScheduleView(FormView):

    title = _('Edit the film session')
    schema = select(FilmScheduleSchema(editable=True, factory=FilmSchedule,
                                       omit=('metadata', )),
               ['title', 'description', 'picture', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [EditFilmSchedule, Cancel]
    formid = 'formeditfilmschedule'
    name = 'editfilmschedule'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/contextual_help_cinema_sessions.js']}

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditFilmSchedule: EditFilmScheduleView})
