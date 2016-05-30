# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import deform
from deform.widget import default_resource_registry


class SearchFormWidget(deform.widget.FormWidget):
    template = 'lac:views/lac_view_manager/templates/search_form.pt'


class SearchTextInputWidget(deform.widget.TextInputWidget):
    template = 'lac:views/lac_view_manager/templates/search_textinput.pt'
    requirements = (('search_text', None),)


default_resource_registry.set_js_resources('search_text', None,
           'lac:static/js/search_text.js')

default_resource_registry.set_css_resources('search_text', None,
              'pontus:static/select2/dist/css/select2.min.css')
