# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import deform
import colander
import math
from pyramid.view import view_config

from dace.util import get_obj
from dace.objectofcollaboration.principal.util import get_current
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView
from pontus.view_operation import MultipleView
from pontus.form import FormView
from pontus.schema import Schema, omit

from lac.content.processes.base_review_management.behaviors import (
    PayReview)
from lac.core import (
    BaseReview)
from lac import _
from lac.content.processes import get_states_mapping



class PayReviewViewStudyReport(BasicView):
    title = _('Pay the cultural event')
    name = 'payreview'
    behaviors = [PayReview]
    template = 'lac:views/base_review_management/templates/pay_review.pt'
    viewid = 'payreview'

    def update(self):
        user = get_current()
        services = user.get_all_services(
            context=self.context,
            validate=False,
            delegation=False)
        sites = [get_obj(s) for s in getattr(self.context, 'sumited_to', [])]
        for site in sites:
            site_services = site.get_all_services(context=self.context,
                                                  validate=True,
                                                  delegation=False)
            if 'moderation' in site_services:
                moderations = site_services['moderation']
                if 'moderation' in services:
                    services['moderation'].extend(moderations)
                else:
                    services['moderation'] = list(moderations)

                services['moderation'] = list(set(
                    services['moderation']))

        result_servicesbody = {}
        for service in services:
            result_servicesbody[service] = []
            for obj in services[service]:
                object_values = {'object': obj,
                                 'state': get_states_mapping(user, obj,
                                    getattr(obj, 'state_or_none', [None])[0])}
                body = self.content(args=object_values,
                                    template=obj.templates['default'])['body']
                result_servicesbody[service].append(body)

        result = {}
        #TDOD generation du formulaire de payment
        values = {'services': result_servicesbody,
                  'math': math}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PaySchema(Schema):

    signature = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title=_('Signature')
        )


class PayReviewView(FormView):
    title = _('Submit')
    name = 'payreviewform'
    formid = 'formpayreview'
    schema = omit(PaySchema(), ['_csrf_token_'])
    behaviors = [PayReview]
    validate_behaviors = False
    action = 'https://paiement.systempay.fr/vads-payment/'

    def update(self):
        payment_confirmation = self.params('payment_confirmation')
        if payment_confirmation:
            #@TODO traitement du paiment
            pass
        else:
            return super(PayReviewView, self).update()

    def before_update(self):
        formwidget = deform.widget.FormWidget(css_class='compareform')
        formwidget.template = 'lac:views/templates/pay_form.pt'
        cancel_url = self.request.resource_url(self.context, '@@index')
        formwidget.cancel_url = cancel_url
        self.schema.widget = formwidget

    def default_data(self):
        #@TODO calcul de la signature et des valeur du formulaire
        return {'signature': 'testsignature'}


@view_config(
    name='payreview',
    context=BaseReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PayReviewViewMultipleView(MultipleView):
    title = _('Pay the cultural event')
    name = 'payreview'
    viewid = 'payreview'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (PayReviewViewStudyReport, PayReviewView)
    validators = [PayReview.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PayReview: PayReviewViewMultipleView})
