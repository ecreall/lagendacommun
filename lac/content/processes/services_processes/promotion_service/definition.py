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
    AddPromotions)

from lac import _


@process_definition(name='promotionserviceprocess',
                    id='promotionserviceprocess')
class PromotionServiceProcess(ProcessDefinition, VisualisableElement):

    discriminator = 'Service'
    isUnique = True

    def __init__(self, **kwargs):
        super(PromotionServiceProcess, self).__init__(**kwargs)
        self.title = _('Promotion service process')
        self.description = _('Promotion service process')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                add_promotions = ActivityDefinition(contexts=[AddPromotions],
                                       description=_("Add promotions"),
                                       title=_("Add promotions"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'add_promotions'),
                TransitionDefinition('add_promotions', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
