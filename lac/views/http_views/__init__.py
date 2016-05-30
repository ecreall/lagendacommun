# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPInternalServerError

from pontus.view import (
    BasicView, ViewError, ViewErrorView)

from lac import _


@view_config(
    context=HTTPNotFound,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class NotFoundView(BasicView):
    title = _('Document not found!')
    name = 'notfound'
    template = 'lac:views/http_views/templates/404.pt'
    css_class = "open-folder"
    container_css_class = 'home'
    wrapper_template = 'lac:views/admin_process/templates/folder_blocs_view_wrapper.pt'

    def update(self):
        urls_storage = self.request.root.get('urls_storage', None)
        if urls_storage:
            response = urls_storage.redirect_url(self.request, '@@index')
            response = response if response else \
                urls_storage.redirect_url(self.request, 'index')
            if response:
                return response

        self.title = self.request.localizer.translate(self.title)
        result = {}
        body = self.content(args={}, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        self.request.response.status = 404
        return result


@view_config(
    context=HTTPInternalServerError,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class InternalServerError(BasicView):
    title = _('An error has occurred!')
    name = 'internalservererror'
    template = 'lac:views/http_views/templates/500.pt'
    css_class = "open-folder"
    container_css_class = 'home'
    wrapper_template = 'lac:views/admin_process/templates/folder_blocs_view_wrapper.pt'

    def update(self):
        self.title = self.request.localizer.translate(self.title)
        result = {}
        body = self.content(args={}, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        self.request.response.status = 500
        return result


@view_config(
    context=ViewError,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ViewErrorToLoginView(ViewErrorView):
    title = _('An error has occurred!')
    name = 'internalservererror'
    css_class = 'folder-bloc'
    container_css_class = 'home'
    wrapper_template = 'lac:views/http_views/templates/simple_wrapper.pt'

    def update(self):
        urls_storage = self.request.root.get('urls_storage', None)
        if urls_storage:
            response = urls_storage.redirect_url(self.request, '@@index')
            response = response if response else \
                urls_storage.redirect_url(self.request, 'index')
            if response:
                return response

        return super(ViewErrorToLoginView, self).update()
