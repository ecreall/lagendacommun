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
    AddSmartFolder,
    AddSubSmartFolder,
    EditSmartFolder,
    RemoveSmartFolder,
    SeeSmartFolder,
    AddSiteFolder,
    EditSiteFolder,
    ConfigureSiteFolder,
    SeeSiteFolder,
    RemoveSiteFolder,
    SeeSiteFolders,
    SeeSmartFolders,
    PublishSmartFolder,
    WithdrawSmartFolder,
    FixAccessPerimeter,
    OrderSmartFolders,
    OrderSubSmartFolders,
    Extract,
    ManageKeywords,
    )
from lac import _


@process_definition(name='adminprocess',
                    id='adminprocess')
class AdminProcess(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(AdminProcess, self).__init__(**kwargs)
        self.title = _('Admin process')
        self.description = _('Admin process')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                add_smart_folder = ActivityDefinition(contexts=[AddSmartFolder],
                                       description=_("Add a smart folder"),
                                       title=_("Add a smart folder"),
                                       groups=[_("Add")]),
                addsub_smart_folder = ActivityDefinition(contexts=[AddSubSmartFolder],
                                       description=_("Add a sub smart folder"),
                                       title=_("Add a sub smart folder"),
                                       groups=[]),
                edit_smart_folder = ActivityDefinition(contexts=[EditSmartFolder],
                                       description=_("Edit the smart folder"),
                                       title=_("Edit"),
                                       groups=[]),
                remove_smart_folder = ActivityDefinition(contexts=[RemoveSmartFolder],
                                       description=_("Remove the smart folder"),
                                       title=_("Remove"),
                                       groups=[]),
                see_smart_folder = ActivityDefinition(contexts=[SeeSmartFolder],
                                       description=_("See a smart folder"),
                                       title=_("See a smart folder"),
                                       groups=[]),
                publish_smart_folder = ActivityDefinition(contexts=[PublishSmartFolder],
                                       description=_("Publish the smart folder"),
                                       title=_("Publish"),
                                       groups=[]),
                withdraw_smart_folder = ActivityDefinition(contexts=[WithdrawSmartFolder],
                                       description=_("Withdraw the smart folder"),
                                       title=_("Withdraw the smart folder"),
                                       groups=[]),
                add_site_folder = ActivityDefinition(contexts=[AddSiteFolder],
                                       description=_("Add a site folder"),
                                       title=_("Add a site folder"),
                                       groups=[_("Add")]),
                edit_site_folder = ActivityDefinition(contexts=[EditSiteFolder],
                                       description=_("Edit the site folder"),
                                       title=_("Edit"),
                                       groups=[]),
                configure_site_folder = ActivityDefinition(contexts=[ConfigureSiteFolder],
                                       description=_("Configure the site folder"),
                                       title=_("Configure"),
                                       groups=[]),
                see_site_folder = ActivityDefinition(contexts=[SeeSiteFolder],
                                       description=_("See a site folder"),
                                       title=_("See a site folder"),
                                       groups=[]),
                remove_site_folder = ActivityDefinition(contexts=[RemoveSiteFolder],
                                       description=_("Remove the site folder"),
                                       title=_("Remove"),
                                       groups=[]),
                see_site_folders = ActivityDefinition(contexts=[SeeSiteFolders],
                                       description=_("Site folders"),
                                       title=_("Site folders"),
                                       groups=[_('See')]),
                see_smart_folders = ActivityDefinition(contexts=[SeeSmartFolders],
                                       description=_("Smart folders"),
                                       title=_("Smart folders"),
                                       groups=[_('See')]),
                fix_access_params = ActivityDefinition(contexts=[FixAccessPerimeter],
                                       description=_("Change the access perimeter"),
                                       title=_("Change the access perimeter"),
                                       groups=[]),
                order_smart_folders = ActivityDefinition(contexts=[OrderSmartFolders],
                                       description=_("Order"),
                                       title=_("Order"),
                                       groups=[]),
                order_sub_smart_folders = ActivityDefinition(contexts=[OrderSubSmartFolders],
                                       description=_("Order"),
                                       title=_("Order"),
                                       groups=[]),
                extract = ActivityDefinition(contexts=[Extract],
                                       description=_("Extract"),
                                       title=_("Extract"),
                                       groups=[_('More')]),
                managekeywords = ActivityDefinition(contexts=[ManageKeywords],
                                       description=_("Manage keywords"),
                                       title=_("Manage keywords"),
                                       groups=[_('More')]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'add_smart_folder'),
                TransitionDefinition('add_smart_folder', 'eg'),
                TransitionDefinition('pg', 'publish_smart_folder'),
                TransitionDefinition('publish_smart_folder', 'eg'),
                TransitionDefinition('pg', 'withdraw_smart_folder'),
                TransitionDefinition('withdraw_smart_folder', 'eg'),
                TransitionDefinition('pg', 'addsub_smart_folder'),
                TransitionDefinition('addsub_smart_folder', 'eg'),
                TransitionDefinition('pg', 'edit_smart_folder'),
                TransitionDefinition('edit_smart_folder', 'eg'),
                TransitionDefinition('pg', 'remove_smart_folder'),
                TransitionDefinition('remove_smart_folder', 'eg'),
                TransitionDefinition('pg', 'see_smart_folder'),
                TransitionDefinition('see_smart_folder', 'eg'),
                TransitionDefinition('pg', 'add_site_folder'),
                TransitionDefinition('add_site_folder', 'eg'),
                TransitionDefinition('pg', 'edit_site_folder'),
                TransitionDefinition('edit_site_folder', 'eg'),
                TransitionDefinition('pg', 'configure_site_folder'),
                TransitionDefinition('configure_site_folder', 'eg'),
                TransitionDefinition('pg', 'see_site_folder'),
                TransitionDefinition('see_site_folder', 'eg'),
                TransitionDefinition('pg', 'remove_site_folder'),
                TransitionDefinition('remove_site_folder', 'eg'),
                TransitionDefinition('pg', 'see_site_folders'),
                TransitionDefinition('see_site_folders', 'eg'),
                TransitionDefinition('pg', 'see_smart_folders'),
                TransitionDefinition('see_smart_folders', 'eg'),
                TransitionDefinition('pg', 'fix_access_params'),
                TransitionDefinition('fix_access_params', 'eg'),
                TransitionDefinition('pg', 'order_smart_folders'),
                TransitionDefinition('order_smart_folders', 'eg'),
                TransitionDefinition('pg', 'order_sub_smart_folders'),
                TransitionDefinition('order_sub_smart_folders', 'eg'),
                TransitionDefinition('pg', 'extract'),
                TransitionDefinition('extract', 'eg'),
                TransitionDefinition('pg', 'managekeywords'),
                TransitionDefinition('managekeywords', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
