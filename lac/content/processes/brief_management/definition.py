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
    CreateBrief,
    EditBrief,
    SeeBrief,
    PublishBrief,
    ArchiveBrief,
    RemoveBrief)
from lac import _


@process_definition(name='briefmanagement',
                    id='briefmanagement')
class BriefManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(BriefManagement, self).__init__(**kwargs)
        self.title = _('News flash management')
        self.description = _('News flash management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateBrief],
                                       description=_("Create a news flash"),
                                       title=_("Create a news flash"),
                                       groups=[_('Add')]),
                edit = ActivityDefinition(contexts=[EditBrief],
                                       description=_("Edit the news flash"),
                                       title=_("Edit"),
                                       groups=[]),
                see = ActivityDefinition(contexts=[SeeBrief],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                publish = ActivityDefinition(contexts=[PublishBrief],
                                       description=_("Publish the news flash"),
                                       title=_("Publish"),
                                       groups=[]),
                archive = ActivityDefinition(contexts=[ArchiveBrief],
                                       description=_("Archive the news flash"),
                                       title=_("Archive"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveBrief],
                                       description=_("Remove the news flash"),
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
                TransitionDefinition('pg', 'publish'),
                TransitionDefinition('publish', 'eg'),
                TransitionDefinition('pg', 'archive'),
                TransitionDefinition('archive', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
