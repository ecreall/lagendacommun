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
    EditBrief)
from lac.content.brief import (
    BriefSchema, Brief)
from lac import _
from lac.utilities.utils import get_site_folder


@view_config(
    name='editbrief',
    context=Brief,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditBriefView(FormView):

    title = _('Edit the news flash')
    schema = select(BriefSchema(factory=Brief,
                                editable=True,
                                omit=('metadata', )),
                    ['title', 'picture', 'tree', 'details',
                     'informations', 'publication_number',
                     ('metadata', ['accessibility', 'object_labels', 'connections_to'])])
    behaviors = [EditBrief, Cancel]
    formid = 'formeditbrief'
    name = 'editbrief'

    def before_update(self):
        site = get_site_folder(True)
        services = site.get_all_services(
            kinds=['extractionservice'], delegation=False)
        has_extraction = 'extractionservice' in services and\
            getattr(services['extractionservice'][0], 'has_periodic', False)
        if not has_extraction:
            self.schema = omit(self.schema, ['publication_number'])

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditBrief: EditBriefView})
