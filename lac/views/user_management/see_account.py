# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import math
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current
from pontus.view import BasicView

from lac.content.processes.user_management.behaviors import (
    SeeCustomerAccount)
from lac.content.person import CustomerAccount
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)
from lac.content.processes import get_states_mapping


@view_config(
    name='seecustomeraccount',
    context=CustomerAccount,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeCustomerAccountView(BasicView):
    title = ''
    name = 'seecustomeraccount'
    behaviors = [SeeCustomerAccount]
    template = 'lac:views/user_management/templates/see_account.pt'
    viewid = 'seecustomeraccount'

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        user = get_current()
        sites = self.context.sites
        result_sitesbody = []
        for obj in sites:
            object_values = {'object': obj}
            body = self.content(args=object_values,
                                template=obj.templates['default'])['body']
            result_sitesbody.append(body)

        services = self.context.services
        result_servicesbody = []
        for obj in services:
            object_values = {'object': obj,
                             'state': get_states_mapping(user, obj,
                                   getattr(obj, 'state_or_none', [None])[0])}
            body = self.content(args=object_values,
                                template=obj.templates['default'])['body']
            result_servicesbody.append(body)

        result_ordersbody = []
        for obj in self.context.orders:
            object_values = {'object': obj,
                             'state': get_states_mapping(user, obj,
                                   getattr(obj, 'state_or_none', [None])[0])}
            body = self.content(args=object_values,
                                template=obj.templates['default'])['body']
            result_ordersbody.append(body)

        values = {'navbar_body': navbars['navbar_body'],
                  'row_len_services': math.ceil(len(services)/4),
                  'row_len_sites': math.ceil(len(sites)/6),
                  'services': result_servicesbody,
                  'orders': result_ordersbody,
                  'sites': result_sitesbody}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeCustomerAccount: SeeCustomerAccountView})
