# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid_layout.layout import layout_config

from lac.utilities.utils import to_localized_time

from lac import PHONE_PATTERNS


def deserialize_phone(phone, add_country=False):
    if isinstance(phone, dict):
        if add_country:
            country_id = phone.get('country', 'fr')
            country = PHONE_PATTERNS.get(country_id, (None, None))[0]
            if country:
                return phone.get('number', '') + ' ('+country+')'

        return phone.get('number', '')

    return phone


@layout_config(template='views/templates/master.pt')
class GlobalLayout(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def to_localized_time(
        self, date, date_from=None,
        date_only=False, format_id='digital',
        ignore_month=False, ignore_year=False,
        add_day_name=False):
        return to_localized_time(
            date, request=self.request, date_from=date_from,
            date_only=date_only, format_id=format_id,
            ignore_month=ignore_month, ignore_year=ignore_year,
            add_day_name=add_day_name, translate=True)

    def deserialize_phone(self, phone, add_country=False):
        return deserialize_phone(phone, add_country)
