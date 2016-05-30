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
    Addapplications,
    AddFacebookApplication,
    AddTwitterApplication,
    AddGoogleApplication,
    SeeApplication,
    EditApplication,
    RemoveApplication
    )
from lac import _


@process_definition(name='socialapplicationsprocess',
                    id='socialapplicationsprocess')
class SocialApplicationsProcess(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(SocialApplicationsProcess, self).__init__(**kwargs)
        self.title = _('Social applications process')
        self.description = _('Social applications process')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                addapplication = ActivityDefinition(contexts=[Addapplications, AddFacebookApplication,
                                                              AddTwitterApplication, AddGoogleApplication],
                                       description=_("Add a social application"),
                                       title=_("Add a social application"),
                                       groups=[]),
                seeapplication = ActivityDefinition(contexts=[SeeApplication],
                                       description=_("See the application"),
                                       title=_("See the application"),
                                       groups=[]),
                editapplication = ActivityDefinition(contexts=[EditApplication],
                                       description=_("Edit the application"),
                                       title=_("Edit"),
                                       groups=[]),
                removeapplication = ActivityDefinition(contexts=[RemoveApplication],
                                       description=_("Remove the application"),
                                       title=_("Remove"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'addapplication'),
                TransitionDefinition('addapplication', 'eg'),
                TransitionDefinition('pg', 'seeapplication'),
                TransitionDefinition('seeapplication', 'eg'),
                TransitionDefinition('pg', 'editapplication'),
                TransitionDefinition('editapplication', 'eg'),
                TransitionDefinition('pg', 'removeapplication'),
                TransitionDefinition('removeapplication', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
