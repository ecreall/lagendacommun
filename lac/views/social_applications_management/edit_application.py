# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView

from lac.content.processes.social_applications_management.behaviors import (
    EditApplication)
from lac.content.social_application import (
    Application)
from lac.core import SOCIAL_APPLICATIONS
from lac import _


@view_config(
    name='editapplication',
    context=Application,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditApplicationView(FormView):

    title = _('Edit the application')
    behaviors = [EditApplication, Cancel]
    formid = 'formeditapplication'
    name = 'editapplication'

    def before_update(self):
        self.schema = SOCIAL_APPLICATIONS[self.context.__class__]

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditApplication: EditApplicationView})
