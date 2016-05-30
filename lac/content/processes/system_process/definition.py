# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
from dace.processdefinition.processdef import ProcessDefinition
from dace.processdefinition.activitydef import ActivityDefinition
from dace.processdefinition.gatewaydef import (
    ExclusiveGatewayDefinition,
    ParallelGatewayDefinition)
from dace.processdefinition.eventdef import (
    IntermediateCatchEventDefinition,
    TimerEventDefinition)
from dace.processdefinition.transitiondef import TransitionDefinition
from dace.processdefinition.eventdef import (
    StartEventDefinition,
    EndEventDefinition)
from dace.objectofcollaboration.services.processdef_container import (
    process_definition)
from pontus.core import VisualisableElement

from .behaviors import (
    ArchiveCulturalEvent,
    SynchronizePublishSettings,
    SendNewsletters,
    AlertUsers
    )

from lac import _


def calculate_next_date_block1(process):
    next_date = datetime.timedelta(days=1) + \
                datetime.datetime.today()
    return datetime.datetime.combine(next_date,
                              datetime.time(0, 0, 0, tzinfo=pytz.UTC))


def calculate_next_date_block2(process):
    #TODO
    next_date = datetime.timedelta(days=1) + \
                datetime.datetime.today()
    return datetime.datetime.combine(next_date,
                              datetime.time(0, 0, 0, tzinfo=pytz.UTC))


@process_definition(name='systemprocess', 
                    id='systemprocess')
class SystemProcess(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(SystemProcess, self).__init__(**kwargs)
        self.title = _('System process')
        self.description = _('System process')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                #First loop
                pgblock1 = ParallelGatewayDefinition(),
                pgblock1sync = ParallelGatewayDefinition(),
                egblock1 = ExclusiveGatewayDefinition(),
                archiveculturalevent = ActivityDefinition(contexts=[ArchiveCulturalEvent],
                                       description=_("Archive cultural events"),
                                       title=_("Archive cultural events"),
                                       groups=[]),
                send_newsletters = ActivityDefinition(contexts=[SendNewsletters],
                                       description=_("Send newsletters"),
                                       title=_("Send newsletters"),
                                       groups=[]),
                alert_users = ActivityDefinition(contexts=[AlertUsers],
                                       description=_("Alert users"),
                                       title=_("Alert users"),
                                       groups=[]),
                timerblock1 = IntermediateCatchEventDefinition(
                                 TimerEventDefinition(
                                   time_date=calculate_next_date_block1)),
                #Second loop
                pgblock2 = ParallelGatewayDefinition(),
                pgblock2sync = ParallelGatewayDefinition(),
                egblock2 = ExclusiveGatewayDefinition(),
                synchronizepublishsettings = ActivityDefinition(contexts=[SynchronizePublishSettings],
                                       description=_("Synchronize publish settings"),
                                       title=_("Synchronize publish settings"),
                                       groups=[]),
                timerblock2 = IntermediateCatchEventDefinition(
                                 TimerEventDefinition(
                                   time_date=calculate_next_date_block2)),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                #First loop
                TransitionDefinition('pg', 'egblock1'),
                TransitionDefinition('egblock1', 'pgblock1'),
                TransitionDefinition('pgblock1', 'archiveculturalevent'),
                TransitionDefinition('archiveculturalevent', 'pgblock1sync'),
                TransitionDefinition('pgblock1', 'send_newsletters'),
                TransitionDefinition('send_newsletters', 'pgblock1sync'),
                TransitionDefinition('pgblock1', 'alert_users'),
                TransitionDefinition('alert_users', 'pgblock1sync'),
                TransitionDefinition('pgblock1sync', 'timerblock1'),
                TransitionDefinition('timerblock1', 'egblock1'),
                #Second loop
                TransitionDefinition('pg', 'egblock2'),
                TransitionDefinition('egblock2', 'pgblock2'),
                TransitionDefinition('pgblock2', 'synchronizepublishsettings'),
                TransitionDefinition('synchronizepublishsettings', 'pgblock2sync'),
                TransitionDefinition('pgblock2sync', 'timerblock2'),
                TransitionDefinition('timerblock2', 'egblock2'),
        )
