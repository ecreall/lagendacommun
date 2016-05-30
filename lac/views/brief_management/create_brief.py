# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit

from lac.content.processes.brief_management.behaviors import (
    CreateBrief)
from lac.content.brief import (
    BriefSchema, Brief)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _
from lac.utilities.utils import get_site_folder


@view_config(
    name='createbrief',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateBriefView(FormView):

    title = _('Create a news flash')
    schema = select(BriefSchema(factory=Brief,
                                editable=True,
                                omit=('metadata',)),
                    ['title', 'picture', 'tree', 'details',
                     'informations', 'publication_number',
                     ('metadata', ['accessibility', 'object_labels', 'connections_to'])])
    behaviors = [CreateBrief, Cancel]
    formid = 'formcreatebrief'
    name = 'createbrief'

    def before_update(self):
        site = get_site_folder(True)
        services = site.get_all_services(
            kinds=['extractionservice'], delegation=False)
        has_extraction = 'extractionservice' in services and\
            getattr(services['extractionservice'][0], 'has_periodic', False)
        if not has_extraction:
            self.schema = omit(self.schema, ['publication_number'])


DEFAULTMAPPING_ACTIONS_VIEWS.update({CreateBrief: CreateBriefView})
