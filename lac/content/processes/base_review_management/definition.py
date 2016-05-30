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
    CreateReview,
    SeeReview,
    EditReview,
    ArchiveReview,
    CreateCinemaReview,
    SubmitReview,
    WithdrawReview,
    SeeCinemaReview,
    EditCinemaReview,
    CreateInterview,
    EditInterview,
    SeeInterview,
    RemoveReview,
    PayReview
    )
from lac import _


@process_definition(name='basereviewmanagement',
                    id='basereviewmanagement')
class BaseReviewManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(BaseReviewManagement, self).__init__(**kwargs)
        self.title = _('Base review management')
        self.description = _('Base review management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateReview, CreateCinemaReview, CreateInterview],
                                       description=_("Create a review"),
                                       title=_("Create a review"),
                                       groups=[_('Add')]),
                edit = ActivityDefinition(contexts=[EditReview, EditCinemaReview, EditInterview],
                                       description=_("Edit the review"),
                                       title=_("Edit"),
                                       groups=[]),
                see = ActivityDefinition(contexts=[SeeReview, SeeCinemaReview, SeeInterview],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                submit = ActivityDefinition(contexts=[SubmitReview],
                                       description=_("Submit the review"),
                                       title=_("Submit"),
                                       groups=[]),
                withdraw = ActivityDefinition(contexts=[WithdrawReview],
                                       description=_("Withdraw the review"),
                                       title=_("Withdraw"),
                                       groups=[]),
                pay = ActivityDefinition(contexts=[PayReview],
                                       description=_("Pay"),
                                       title=_("Pay"),
                                       groups=[]),
                archive = ActivityDefinition(contexts=[ArchiveReview],
                                       description=_("Archive the review"),
                                       title=_("Archive"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveReview],
                                       description=_("Remove the review"),
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
                TransitionDefinition('pg', 'submit'),
                TransitionDefinition('submit', 'eg'),
                TransitionDefinition('pg', 'withdraw'),
                TransitionDefinition('withdraw', 'eg'),
                TransitionDefinition('pg', 'pay'),
                TransitionDefinition('pay', 'eg'),
                TransitionDefinition('pg', 'archive'),
                TransitionDefinition('archive', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
