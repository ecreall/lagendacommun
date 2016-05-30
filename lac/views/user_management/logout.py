# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.user_management.behaviors import (
    LogOut)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _

@view_config(
    name='logout',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class LogoutView(BasicView):
    title = _('Log out')
    name = 'logout'
    behaviors = [LogOut]
    viewid = 'logout'

    def update(self):
        self.execute(None)
        headers = forget(self.request)
        return HTTPFound(
            location=self.request.resource_url(self.request.context),
            headers=headers)


DEFAULTMAPPING_ACTIONS_VIEWS.update({LogOut: LogoutView})
