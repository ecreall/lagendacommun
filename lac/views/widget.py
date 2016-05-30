# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import deform
import colander
from colander import null
from persistent.dict import PersistentDict
from deform.widget import default_resource_registry
from bs4 import BeautifulSoup

from pyramid.threadlocal import get_current_request
from pyramid import renderers

import html_diff_wrapper
from pontus.widget import (
    TextInputWidget,
    RichTextWidget as RichTextWidgetBase,
    SequenceWidget as OriginSequenceWidget)

from lac import _, PHONE_PATTERNS


class SimpleSequenceWidget(OriginSequenceWidget):

    template = 'lac:views/templates/sequence.pt'
    item_template = 'lac:views/templates/sequence_item.pt'


class EmailInputWidget(deform.widget.TextInputWidget):
    template = 'lac:views/templates/email_input.pt'


class TOUCheckboxWidget(deform.widget.CheckboxWidget):
    template = 'lac:views/templates/terms_of_use_checkbox.pt'
    requirements = (('toucheckbox', None), )


class LimitedTextAreaWidget(deform.widget.TextAreaWidget):
    template = 'lac:views/templates/textarea.pt'
    default_alert_template = 'lac:views/templates/textarea_default_alert.pt'
    requirements = (('jquery.maskedinput', None),
                    ('limitedtextarea', None))

    @property
    def alert_message(self):
        alert_values = {'limit': self.limit}
        template = self.default_alert_template
        if hasattr(self, 'alert_template'):
            template = self.alert_template

        if hasattr(self, 'alert_values'):
            alert_values = self.alert_values

        request = get_current_request()
        body = renderers.render(
               template, alert_values, request)
        return body


class SimpleMappingtWidget(deform.widget.MappingWidget):
    template = 'lac:views/templates/mapping_simple.pt'
    requirements = (('deform', None), ('simple_mapping', None))


class CssWidget(TextInputWidget):
    template = 'lac:views/templates/style_picker.pt'
    requirements = (('jquery.maskedinput', None),
                    ('stylepicker', None))


class DateIcalWidget(TextInputWidget):
    template = 'lac:views/templates/date_ical.pt'
    requirements = (('jquery.maskedinput', None),
                    ('date_ical', None))


def redirect_links(soup):
    a_tags = soup.find_all('a')
    for tag in a_tags:
        tag['target'] = '_blank'

    return soup


class RichTextWidget(RichTextWidgetBase):

    def deserialize(self, field, pstruct):
        text = super(RichTextWidget, self).deserialize(field, pstruct)
        if text is colander.null:
            return colander.null

        return html_diff_wrapper.normalize_text(text, {redirect_links})


class PhoneWidget(TextInputWidget):

    requirements = (('jquery.maskedinput', None),
                    ('phone_input', None))
    template = 'lac:views/templates/phone_input.pt'
    default_country = 'fr'
    countries = [(k, v[0]) for k, v in PHONE_PATTERNS.items()]

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = {
                'country': self.default_country,
                'number': ''
            }

        if isinstance(cstruct, str):
            cstruct = {
                'country': self.default_country,
                'number': cstruct
            }

        if isinstance(cstruct, (dict, PersistentDict)):
            cstruct = cstruct.copy()
            if 'country' in cstruct:
                cstruct[field.name + '_country'] = cstruct.pop('country', 'fr')

            if 'number' in cstruct:
                cstruct[field.name] = cstruct.pop('number', '')

        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        country_id = field.name+'_country'
        number_id = field.name
        if pstruct is null:
            return null
        elif not isinstance(pstruct, dict):
            raise colander.Invalid(field.schema, "Pstruct is not a dict")
        elif country_id not in pstruct or \
            number_id not in pstruct:
            raise colander.Invalid(field.schema, "Phone number is not valid")

        country = pstruct.get(country_id, 'fr')
        number = pstruct.get(number_id, '')
        if not number.strip() or number is null:
            return null

        result = {'country': country,
                  'number': number}
        return result


class PhoneValidator(object):
    """ Phone expression validator.
    """
    def __init__(self, msg=None):
        if msg is None:
            self.msg = _('${phone} phone number not valid for the selected country (${country})')
        else:
            self.msg = msg

    def __call__(self, node, value):
        country = value.get('country', 'fr')
        number = value.get('number', '')
        pattern_data = PHONE_PATTERNS.get(country, None)
        if pattern_data:
            pattern = pattern_data[1]
            if not pattern.match(number):
                raise colander.Invalid(
                    node,
                    _(self.msg,
                      mapping={'phone': number,
                               'country': pattern_data[0]}))


class ArticleRichTextWidget(RichTextWidget):

    template = 'lac:views/templates/richtext.pt'

    default_options = (('height', 240),
                   ('width', 0),
                   ('skin', 'lightgray'),
                   ('fontsize_formats', "8pt 9pt 10pt 11pt 12pt"
                                        " 13pt 14pt 15pt 26pt 36pt"),
                   ('toolbar', "preview print | undo redo"
                               " | styles_article styles_folders fontselect fontsizeselect"
                               " | forecolor backcolor | bold italic | alignleft "
                               "aligncenter alignright alignjustify | "
                               "bullist numlist outdent indent"),
                   ('theme', 'modern'),
                   ('mode', 'exact'),
                   ('strict_loading_mode', True),
                   ('remove_linebreaks', False),
                   ('theme_advanced_resizing', True),
                   ('theme_advanced_toolbar_align', 'left'),
                   ('theme_advanced_toolbar_location', 'top'))

    requirements = (('tinymce', None),
                    ('article', None))

    def deserialize(self, field, pstruct):
        article = super(ArticleRichTextWidget, self).deserialize(field, pstruct)
        if article is colander.null:
            return colander.null

        soup = BeautifulSoup(article, 'lxml')
        clear_style_btns = soup.find_all('button', 'clear-style')
        newparagraph_style_btns = soup.find_all('button', 'newparagraph-style')
        for tag in clear_style_btns:
            tag.extract()

        for tag in newparagraph_style_btns:
            tag.extract()

        text = ''.join([str(t) for t in soup.body.contents])
        return html_diff_wrapper.normalize_text(text, {redirect_links})


class BootstrapIconInputWidget(deform.widget.TextInputWidget):
    template = 'lac:views/templates/bootstrap_icon_input.pt'
    requirements = (('bootstrap_icon', None),)

    def serialize(self, field, cstruct, **kw):
        if cstruct is null:
            cstruct = ''
        elif isinstance(cstruct, dict):
            cstruct = cstruct.get('icon_class')+','+cstruct.get('icon')
        return super(BootstrapIconInputWidget, self).serialize(
                                                  field, cstruct, **kw)

    def deserialize(self, field, pstruct):
        row = super(BootstrapIconInputWidget, self).deserialize(field, pstruct)
        if row is null:
            return null

        data = row.split(',')
        try:
            return {'icon_class': data[0],
                    'icon': data[1]}
        except:
            return data


default_resource_registry.set_js_resources('bootstrap_icon', None,
           'lac:static/bootstrap-iconpicker/bootstrap-iconpicker/js/iconset/iconset-all.min.js',
           'lac:static/bootstrap-iconpicker/bootstrap-iconpicker/js/bootstrap-iconpicker.js',
           'lac:static/js/bootstrap_iconpicker.js')

default_resource_registry.set_css_resources('bootstrap_icon', None,
              'lac:static/bootstrap-iconpicker/bootstrap-iconpicker/css/bootstrap-iconpicker.min.css')


default_resource_registry.set_js_resources('simple_mapping', None,
               'lac:static/js/simple_mapping.js')

default_resource_registry.set_js_resources('toucheckbox', None,
               'lac:static/js/toucheckbox.js')

default_resource_registry.set_js_resources('article', None,
               'lac:static/js/article_tinymce.js')

default_resource_registry.set_js_resources('limitedtextarea', None,
               'lac:static/limitedtextarea/limitedtextarea.js')

default_resource_registry.set_css_resources('limitedtextarea', None,
              'lac:static/limitedtextarea/limitedtextarea.css')

default_resource_registry.set_js_resources('stylepicker', None,
               'lac:static/bgrins-spectrum/spectrum.js',
               'lac:static/js/style_picker.js')

default_resource_registry.set_css_resources('stylepicker', None,
              'lac:static/bgrins-spectrum/spectrum.css')

default_resource_registry.set_js_resources('date_ical', None,
               'lac:static/js/date_ical.js')

default_resource_registry.set_css_resources('date_ical', None,
              'lac:static/css/date_ical.css')


default_resource_registry.set_css_resources('phone_input', None,
              'lac:static/css/phone_input.css')
