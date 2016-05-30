# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.user_management.behaviors import (
    EditCustomerAccount)
from lac.content.person import CustomerAccount, CustomerAccountSchema
from lac import _


@view_config(
    name='editcustomeraccount',
    context=CustomerAccount,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditCustomerAccountView(FormView):

    title = _('Configure the customer account')
    schema = select(CustomerAccountSchema(factory=CustomerAccount,
                                          editable=True),
                    ['sites'])
    behaviors = [EditCustomerAccount, Cancel]
    formid = 'formeditcustomeraccount'
    name = 'editcustomeraccount'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditCustomerAccount: EditCustomerAccountView})
