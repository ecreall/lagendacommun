# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
from dace.processdefinition.processdef import ProcessDefinition
from dace.processdefinition.activitydef import ActivityDefinition
from dace.processdefinition.gatewaydef import (
    ExclusiveGatewayDefinition,
    ParallelGatewayDefinition)
from dace.processdefinition.transitiondef import TransitionDefinition
from dace.processdefinition.eventdef import (
    StartEventDefinition,
    EndEventDefinition,
    IntermediateCatchEventDefinition,
    TimerEventDefinition)
from dace.objectofcollaboration.services.processdef_container import (
    process_definition)
from pontus.core import VisualisableElement

from .behaviors import (
    CreateGame,
    SeeGame,
    EditGame,
    PublishGame,
    RejectGame,
    ArchiveGame,
    SubmitGame,
    WithdrawGame,
    RemoveGame,
    SendResult,
    Draw,
    SystemPublishGame,
    Participate
    )
from lac import _


def timer_start(process):
    game = process.execution_context.created_entity('game')
    return getattr(
        game, 'start_date', datetime.datetime.now())


def timer_end(process):
    game = process.execution_context.created_entity('game')
    return getattr(
        game, 'end_date', datetime.datetime.now())


@process_definition(name='gamemanagement',
                    id='gamemanagement')
class GameManagement(ProcessDefinition, VisualisableElement):

    def __init__(self, **kwargs):
        super(GameManagement, self).__init__(**kwargs)
        self.title = _('Game management')
        self.description = _('Game management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                pg1 = ParallelGatewayDefinition(),
                pg2 = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateGame],
                                       description=_("Create a game"),
                                       title=_("Create a game"),
                                       groups=[_('Add')]),
                edit = ActivityDefinition(contexts=[EditGame],
                                       description=_("Edit the game"),
                                       title=_("Edit the game"),
                                       groups=[]),
                submit = ActivityDefinition(contexts=[SubmitGame],
                                       description=_("Submit the game"),
                                       title=_("Submit"),
                                       groups=[]),
                withdraw = ActivityDefinition(contexts=[WithdrawGame],
                                       description=_("Withdraw the game"),
                                       title=_("Withdraw"),
                                       groups=[]),
                reject = ActivityDefinition(contexts=[RejectGame],
                                       description=_("Reject the game"),
                                       title=_("Reject"),
                                       groups=[]),
                publish = ActivityDefinition(contexts=[PublishGame],
                                       description=_("Publish the game"),
                                       title=_("Publish"),
                                       groups=[]),
                archive = ActivityDefinition(contexts=[ArchiveGame],
                                       description=_("Archive the game"),
                                       title=_("Archive"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveGame],
                                       description=_("Remove the game"),
                                       title=_("Remove"),
                                       groups=[]),
                draw = ActivityDefinition(contexts=[Draw],
                                       description=_("Draw"),
                                       title=_("Draw"),
                                       groups=[]),
                send_result = ActivityDefinition(contexts=[SendResult],
                                       description=_("Send the result"),
                                       title=_("Send the result"),
                                       groups=[]),
                timer_start = IntermediateCatchEventDefinition(
                           TimerEventDefinition(time_date=timer_start)),
                system_publish = ActivityDefinition(contexts=[SystemPublishGame],
                                       description=_("Publish the game"),
                                       title=_("Publish"),
                                       groups=[]),
                participate = ActivityDefinition(contexts=[Participate],
                                       description=_("Participate"),
                                       title=_("Participate"),
                                       groups=[]),
                timer_end = IntermediateCatchEventDefinition(
                           TimerEventDefinition(time_date=timer_end)),
                eg = ExclusiveGatewayDefinition(),
                eg1 = ExclusiveGatewayDefinition(),
                eg2 = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'creat'),
                TransitionDefinition('creat', 'eg'),
                TransitionDefinition('eg', 'pg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('pg', 'submit'),
                TransitionDefinition('submit', 'eg1'),
                TransitionDefinition('eg1', 'withdraw'),
                TransitionDefinition('withdraw', 'eg'),
                TransitionDefinition('eg1', 'publish'),
                TransitionDefinition('pg1', 'archive'),
                TransitionDefinition('archive', 'eg2'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg2'),
                TransitionDefinition('eg1', 'reject'),
                TransitionDefinition('reject', 'eg2'),
                TransitionDefinition('publish', 'pg1'),
                TransitionDefinition('pg1', 'timer_start'),
                TransitionDefinition('timer_start', 'system_publish'),
                TransitionDefinition('system_publish', 'pg2'),
                TransitionDefinition('pg2', 'timer_end'),
                TransitionDefinition('pg2', 'participate'),
                TransitionDefinition('timer_end', 'draw'),
                TransitionDefinition('draw', 'send_result'),
                TransitionDefinition('send_result', 'eg2'),
                TransitionDefinition('eg2', 'end'),

        )



@process_definition(name='globalgamemanagement',
                    id='globalgamemanagement')
class GlobalGameManagement(ProcessDefinition, VisualisableElement):

    isUnique = True

    def __init__(self, **kwargs):
        super(GlobalGameManagement, self).__init__(**kwargs)
        self.title = _('Global game management')
        self.description = _('Global game management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                see = ActivityDefinition(contexts=[SeeGame],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'see'),
                TransitionDefinition('see', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
