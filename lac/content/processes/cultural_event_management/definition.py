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
    SeeCulturalEvent,
    EditCulturalEvent,
    CreateCulturalEvent,
    PayCulturalEvent,
    ArchiveCulturalEvent,
    DuplicateCulturalEvent,
    RemoveCulturalEvent,
    SubmitCulturalEvent,
    ManageDuplicates,
    WithdrawCulturalEvent
    )

from lac import _


@process_definition(name='culturaleventmanagement',
                    id='culturaleventmanagement')
class CulturalEventManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(CulturalEventManagement, self).__init__(**kwargs)
        self.title = _('Cultural event management')
        self.description = _('Cultural event management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateCulturalEvent],
                                       description=_("Create a cultural event"),
                                       title=_("Create a cultural event"),
                                       groups=[_('Add')]),
                edit = ActivityDefinition(contexts=[EditCulturalEvent],
                                       description=_("Edit the cultural event"),
                                       title=_("Edit"),
                                       groups=[]),
                submit = ActivityDefinition(contexts=[SubmitCulturalEvent],
                                       description=_("Submit the cultural event"),
                                       title=_("Submit"),
                                       groups=[]),
                withdraw = ActivityDefinition(contexts=[WithdrawCulturalEvent],
                                       description=_("Withdraw the cultural event"),
                                       title=_("Withdraw"),
                                       groups=[]),
                pay = ActivityDefinition(contexts=[PayCulturalEvent],
                                       description=_("Pay the cultural event"),
                                       title=_("Pay"),
                                       groups=[]),
                archive = ActivityDefinition(contexts=[ArchiveCulturalEvent],
                                       description=_("Archive the cultural event"),
                                       title=_("Archive"),
                                       groups=[]),
                duplicate = ActivityDefinition(contexts=[DuplicateCulturalEvent],
                                       description=_("Improve the cultural event"),
                                       title=_("Improve"),
                                       groups=[]),
                seeculturalevent = ActivityDefinition(
                                       contexts=[SeeCulturalEvent],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveCulturalEvent],
                                       description=_("Remove the cultural event"),
                                       title=_("Remove"),
                                       groups=[]),
                manage_duplicates = ActivityDefinition(contexts=[ManageDuplicates],
                                       description=_("Manage duplicates"),
                                       title=_("Manage duplicates"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'creat'),
                TransitionDefinition('creat', 'eg'),
                TransitionDefinition('pg', 'pay'),
                TransitionDefinition('pay', 'eg'),
                TransitionDefinition('pg', 'archive'),
                TransitionDefinition('archive', 'eg'),
                TransitionDefinition('pg', 'duplicate'),
                TransitionDefinition('duplicate', 'eg'),
                TransitionDefinition('pg', 'submit'),
                TransitionDefinition('submit', 'eg'),
                TransitionDefinition('pg', 'withdraw'),
                TransitionDefinition('withdraw', 'eg'),
                TransitionDefinition('pg', 'seeculturalevent'),
                TransitionDefinition('seeculturalevent', 'eg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('pg', 'manage_duplicates'),
                TransitionDefinition('manage_duplicates', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
