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
    EditReview,
    PublishReview,
    RejectReview,
    PrepareForPublicationReview,
    EditCinemaReview,
    EditInterview,
    )
from lac import _


@process_definition(name='basereviewmoderation',
                    id='basereviewmoderation')
class BaseReviewModeration(ProcessDefinition, VisualisableElement):
  
    discriminator = 'Service'
    isControlled = True

    def __init__(self, **kwargs):
        super(BaseReviewModeration, self).__init__(**kwargs)
        self.title = _('Base review moderation')
        self.description = _('Base review moderation')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                edit = ActivityDefinition(contexts=[EditReview, EditCinemaReview, EditInterview],
                                       description=_("Edit the review"),
                                       title=_("Edit"),
                                       groups=[]),
                reject = ActivityDefinition(contexts=[RejectReview],
                                       description=_("Reject the review"),
                                       title=_("Reject"),
                                       groups=[]),
                publish = ActivityDefinition(contexts=[PublishReview],
                                       description=_("Publish the review"),
                                       title=_("Publish"),
                                       groups=[]),
                prepare = ActivityDefinition(contexts=[PrepareForPublicationReview],
                                       description=_("Prepare the review for publication"),
                                       title=_("Prepare for publication"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('pg', 'publish'),
                TransitionDefinition('publish', 'eg'),
                TransitionDefinition('pg', 'prepare'),
                TransitionDefinition('prepare', 'eg'),
                TransitionDefinition('pg', 'reject'),
                TransitionDefinition('reject', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
