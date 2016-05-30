# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.schema import select
from pontus.default_behavior import Cancel

from lac.content.processes.service_definition_process.behaviors import (
  EditServiceDefinition)
from lac.content.service_definition import (
    ServiceDefinitionSchema, ServiceDefinition)
from lac import _


@view_config(
    name='editservicedefinition',
    context=ServiceDefinition,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditServiceDefinitionView(FormView):

    title = _('Edit service definition')
    schema = select(ServiceDefinitionSchema(editable=True),
                    ['description',
                     'details',
                     'subscription'])
    behaviors = [EditServiceDefinition, Cancel]
    formid = 'formeditservicedefinition'
    name = 'editservicedefinition'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditServiceDefinition: EditServiceDefinitionView})
