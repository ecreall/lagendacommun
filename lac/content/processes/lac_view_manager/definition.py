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
    Search,
    SeeMyContents,
    SeeHome,
    SeeContentsToModerate,
    Contact,
    SeeGames,
    SeeEntityHistory,
    DiffView,
    SeeAllDuplicates,
    SeeAlerts,
    SeeContributors,
    Questionnaire,
    Improve
    )
from lac import _


@process_definition(name='lacviewmanager',
                    id='lacviewmanager')
class CreationCulturelleViewManager(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(CreationCulturelleViewManager, self).__init__(**kwargs)
        self.title = _('User access manager')
        self.description = _('User access manager')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                search = ActivityDefinition(contexts=[Search],
                                       description=_("Search"),
                                       title=_("Search"),
                                       groups=[]),
                home = ActivityDefinition(contexts=[SeeHome],
                                       description=_("Home"),
                                       title=_("Home"),
                                       groups=[]),
                mycontents = ActivityDefinition(contexts=[SeeMyContents],
                                       description=_("See my contents"),
                                       title=_("My contents"),
                                       groups=[_('See')]),
                seecontenttomoderate = ActivityDefinition(contexts=[SeeContentsToModerate],
                                       description=_("See content to moderate"),
                                       title=_("Contents to moderate"),
                                       groups=[_('See')]),
                seegames = ActivityDefinition(contexts=[SeeGames],
                                       description=_("See games"),
                                       title=_("Games & Competitions"),
                                       groups=[_('See')]),
                seehistory = ActivityDefinition(contexts=[SeeEntityHistory],
                                       description=_("See history"),
                                       title=_("History"),
                                       groups=[]),
                seecontributors = ActivityDefinition(contexts=[SeeContributors],
                                       description=_("See contributors"),
                                       title=_("Contributors"),
                                       groups=[]),
                contact = ActivityDefinition(contexts=[Contact],
                                       description=_("Contact"),
                                       title=_("Contact"),
                                       groups=[]),
                diff_view = ActivityDefinition(contexts=[DiffView],
                                       description=_("Differences"),
                                       title=_("Differences"),
                                       groups=[]),
                see_all_dup = ActivityDefinition(contexts=[SeeAllDuplicates],
                                       description=_("All duplicates"),
                                       title=_("All duplicates"),
                                       groups=[_('See')]),
                seealerts = ActivityDefinition(contexts=[SeeAlerts],
                                       description=_("See alerts"),
                                       title=_("Alerts"),
                                       groups=[]),
                questionnaire = ActivityDefinition(contexts=[Questionnaire],
                                       description=_("Questionnaire"),
                                       title=_("Let us have your feedback"),
                                       groups=[]),
                improve = ActivityDefinition(contexts=[Improve],
                                       description=_("Questionnaire"),
                                       title=_("Let us have your feedback"),
                                       groups=[]),
                
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'search'),
                TransitionDefinition('search', 'eg'),
                TransitionDefinition('pg', 'home'),
                TransitionDefinition('home', 'eg'),
                TransitionDefinition('pg', 'mycontents'),
                TransitionDefinition('mycontents', 'eg'),
                TransitionDefinition('pg', 'seecontributors'),
                TransitionDefinition('seecontributors', 'eg'),
                TransitionDefinition('pg', 'seecontenttomoderate'),
                TransitionDefinition('seecontenttomoderate', 'eg'),
                TransitionDefinition('pg', 'seegames'),
                TransitionDefinition('seegames', 'eg'),
                TransitionDefinition('pg', 'contact'),
                TransitionDefinition('contact', 'eg'),
                TransitionDefinition('pg', 'seehistory'),
                TransitionDefinition('seehistory', 'eg'),
                TransitionDefinition('pg', 'diff_view'),
                TransitionDefinition('diff_view', 'eg'),
                TransitionDefinition('pg', 'see_all_dup'),
                TransitionDefinition('see_all_dup', 'eg'),
                TransitionDefinition('pg', 'seealerts'),
                TransitionDefinition('seealerts', 'eg'),
                TransitionDefinition('pg', 'questionnaire'),
                TransitionDefinition('questionnaire', 'eg'),
                TransitionDefinition('pg', 'improve'),
                TransitionDefinition('improve', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
