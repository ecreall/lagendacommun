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
    CreateFilmSynopses,
    EditFilmSynopses,
    SeeFilmSynopses,
    PutOnHoldFilmSynopses,
    PublishFilmSynopses,
    ArchiveFilmSynopses,
    RemoveFilmSynopses)
from lac import _


@process_definition(name='filmsynopsesmanagement',
                    id='filmsynopsesmanagement')
class FilmSynopsesManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(FilmSynopsesManagement, self).__init__(**kwargs)
        self.title = _('Film synopses management')
        self.description = _('Film synopses management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateFilmSynopses],
                                       description=_("Create a film synopsis"),
                                       title=_("Create a film synopsis"),
                                       groups=[_('Add')]),
                edit = ActivityDefinition(contexts=[EditFilmSynopses],
                                       description=_("Edit the film synopsis"),
                                       title=_("Edit"),
                                       groups=[]),
                see = ActivityDefinition(contexts=[SeeFilmSynopses],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                put_on_hold = ActivityDefinition(contexts=[PutOnHoldFilmSynopses],
                                       description=_("Put on hold the film synopsis"),
                                       title=_("Put on hold"),
                                       groups=[]),
                publish = ActivityDefinition(contexts=[PublishFilmSynopses],
                                       description=_("Publish the film synopsis"),
                                       title=_("Publish"),
                                       groups=[]),
                archive = ActivityDefinition(contexts=[ArchiveFilmSynopses],
                                       description=_("Archive the film synopsis"),
                                       title=_("Archive"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveFilmSynopses],
                                       description=_("Remove the film synopsis"),
                                       title=_("Remove"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'creat'),
                TransitionDefinition('creat', 'eg'),
                TransitionDefinition('pg', 'see'),
                TransitionDefinition('see', 'eg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('pg', 'put_on_hold'),
                TransitionDefinition('put_on_hold', 'eg'),
                TransitionDefinition('pg', 'publish'),
                TransitionDefinition('publish', 'eg'),
                TransitionDefinition('pg', 'archive'),
                TransitionDefinition('archive', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
