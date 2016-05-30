# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from dace.processdefinition.processdef import ProcessDefinition
from dace.processdefinition.activitydef import ActivityDefinition
from dace.processdefinition.gatewaydef import (
    ExclusiveGatewayDefinition,
    ParallelGatewayDefinition)
from dace.processdefinition.transitiondef import TransitionDefinition
from dace.processdefinition.eventdef import (
    StartEventDefinition,
    EndEventDefinition)
from dace.objectofcollaboration.services.processdef_container import (
    process_definition)
from pontus.core import VisualisableElement

from .behaviors import (
    AddCinemagoer,
    EditFilmSchedule,
    SeeFilmSchedule,
    RemoveFilmSchedule)
from lac import _


@process_definition(name='filmschedulemanagement',
                    id='filmschedulemanagement')
class FilmScheduleManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(FilmScheduleManagement, self).__init__(**kwargs)
        self.title = _('Film schedule management')
        self.description = _('Film schedule management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                add_cinemagoer = ActivityDefinition(contexts=[AddCinemagoer],
                                       description=_("Add cinema sessions"),
                                       title=_("Add cinema sessions"),
                                       groups=[_("Add")]),
                edit = ActivityDefinition(contexts=[EditFilmSchedule],
                                       description=_("Edit the film synopsis"),
                                       title=_("Edit"),
                                       groups=[]),
                see = ActivityDefinition(contexts=[SeeFilmSchedule],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveFilmSchedule],
                                       description=_("Remove the film synopsis"),
                                       title=_("Remove"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'add_cinemagoer'),
                TransitionDefinition('add_cinemagoer', 'eg'),
                TransitionDefinition('pg', 'see'),
                TransitionDefinition('see', 'eg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
