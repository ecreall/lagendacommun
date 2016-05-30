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
    EditCulturalEvent,
    RejectCulturalEvent,
    PublishCulturalEvent)

from lac import _


@process_definition(name='culturaleventmoderation',
                    id='culturaleventmoderation')
class CulturalEventModeration(ProcessDefinition, VisualisableElement):

    discriminator = 'Service'
    isControlled = True

    def __init__(self, **kwargs):
        super(CulturalEventModeration, self).__init__(**kwargs)
        self.title = _('Cultural event moderation')
        self.description = _('Cultural event moderation')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                edit = ActivityDefinition(contexts=[EditCulturalEvent],
                                       description=_("Edit the cultural event"),
                                       title=_("Edit"),
                                       groups=[]),
                reject = ActivityDefinition(contexts=[RejectCulturalEvent],
                                       description=_("Reject the cultural event"),
                                       title=_("Reject"),
                                       groups=[]),
                publish = ActivityDefinition(contexts=[PublishCulturalEvent],
                                       description=_("Publish the cultural event"),
                                       title=_("Publish"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'reject'),
                TransitionDefinition('reject', 'eg'),
                TransitionDefinition('pg', 'publish'),
                TransitionDefinition('publish', 'eg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
