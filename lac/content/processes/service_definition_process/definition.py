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
    EditServiceDefinition,
    SeeServiceDefinition,
    SeeServicesDefinition)

from lac import _


@process_definition(name='servicedefinitionmanagement',
                    id='servicedefinitionmanagement')
class ServiceDefinitionManagement(ProcessDefinition, VisualisableElement):

    isUnique = True

    def __init__(self, **kwargs):
        super(ServiceDefinitionManagement, self).__init__(**kwargs)
        self.title = _('Service definition management')
        self.description = _('Service definition management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                see_service = ActivityDefinition(contexts=[SeeServiceDefinition],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                edit = ActivityDefinition(contexts=[EditServiceDefinition],
                                       description=_("Edit the service definition"),
                                       title=_("Edit"),
                                       groups=[]),
                sees = ActivityDefinition(contexts=[SeeServicesDefinition],
                                       description=_("See definitions"),
                                       title=_("Service definitions"),
                                       groups=[_('See')]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('pg', 'see_service'),
                TransitionDefinition('see_service', 'eg'),
                TransitionDefinition('pg', 'sees'),
                TransitionDefinition('sees', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
