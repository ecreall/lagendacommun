# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.util import get_obj, getSite
from pontus.view import BasicView

from lac.content.processes.services_processes.\
    newsletter_management.behaviors import (
        UserUnsubscribeNewsletter)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _, log


@view_config(
    name='userunsubscribenewsletter',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class UserUnsubscribeNewsletterView(BasicView):

    title = _('Unsubscribe')
    behaviors = [UserUnsubscribeNewsletter]
    name = 'userunsubscribenewsletter'

    def update(self):
        oid = self.params('oid')
        if oid:
            try:
                newsletter = get_obj(int(oid))
                user = self.params('user')
                result = self.execute({'newsletter': newsletter, 'user': user})
                return result[0]
            except Exception as error:
                log.warning(error)

        root = getSite()
        return HTTPFound(self.request.resource_url(root, ""))


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {UserUnsubscribeNewsletter: UserUnsubscribeNewsletterView})
