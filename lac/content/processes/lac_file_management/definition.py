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
    CreateFile,
    SeeFile,
    EditFile,
    SeeFiles,
    )
from lac import _


@process_definition(name='lacfilemanagement',
                    id='lacfilemanagement')
class CreationCulturelleFileManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(CreationCulturelleFileManagement, self).__init__(**kwargs)
        self.title = _('File management')
        self.description = _('File management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateFile],
                                       description=_("Create a file"),
                                       title=_("Create a file"),
                                       groups=[_('Add')]),
                editfile = ActivityDefinition(contexts=[EditFile],
                                       description=_("Edit the file"),
                                       title=_("Edit"),
                                       groups=[]),
                seefile = ActivityDefinition(contexts=[SeeFile],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                seefiles = ActivityDefinition(contexts=[SeeFiles],
                                       description=_("Files"),
                                       title=_("Files"),
                                       groups=[_('See')]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'creat'),
                TransitionDefinition('creat', 'eg'),
                TransitionDefinition('pg', 'seefile'),
                TransitionDefinition('seefile', 'eg'),
                TransitionDefinition('pg', 'editfile'),
                TransitionDefinition('editfile', 'eg'),
                TransitionDefinition('pg', 'seefiles'),
                TransitionDefinition('seefiles', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
