# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import json
from PIL import Image as PILImage
from pyramid.view import view_config
#from pyramid import traversal
from pyramid.httpexceptions import HTTPFound
from pyramid_layout.layout import layout_config

from substanced.util import get_oid

from dace.objectofcollaboration.principal.util import (
    get_current, has_any_roles, grant_roles)
from dace.objectofcollaboration.entity import Entity
from dace.util import getSite, get_obj
from pontus.view import BasicView
from pontus.file import Image


_imagetypes = ['gif', 'jpg', 'jpeg', 'png']


@layout_config(name='filemanager_layout',
               template='lac:views/lac_view_manager/templates/filemanager_layout.pt')
class FileManagerLayout(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request


@view_config(
    name='resolveimg',
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ImgResolver(BasicView):
    title = ''
    name = 'resolveimg'
    viewid = 'resolveimg'

    def update(self):
        img_id = self.params('img_id')
        if not img_id:
            return HTTPFound(self.request.resource_url(self.request.root, ''))

        img = get_obj(int(img_id))
        if img:
            url = img.url
            return HTTPFound(url)

        return HTTPFound(self.request.resource_url(self.request.root, ''))


def get_file(path):
    try:
        oid = path.split('img_id=')[-1]
        return get_obj(int(oid))
    except:
        return None


def get_file_url(file_, request):
    try:
        return request.resource_url(
            request.root, 'resolveimg', query={'img_id': get_oid(file_)})
    except:
        return request.resource_url(request.root)


@view_config(name='filemanager_index',
             context=Entity,
             renderer='lac:web_services/templates/grid.pt',
             layout='filemanager_layout')
class FileManagementIndex(BasicView):
    title = ''
    name = 'filemanager_index'
    template = 'lac:views/lac_view_manager/templates/filemanager_index.pt'

    def update(self):
        result = {}
        body = self.content(args={}, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


@view_config(name='file_management',
             context=Entity,
             xhr=True,
             renderer='json')
class FileManagement(BasicView):

    def getinfo(self, file_=None, getsize=True):
        """Returns a JSON object containing information about the given file."""
        path = self.params('path')
        operation_name = self.params('mode')
        if path is not None and operation_name == 'getinfo':
            #file_ = traversal.traverse(self.context, path).get('context', None)
            file_ = get_file(path)

        thefile = {}
        if file_:
            url = get_file_url(file_, self.request)
            thefile = {
                'Filename': file_.title,
                'File Type': '',
                'Preview': 'images/fileicons/_Open.png',
                'Path': url,
                'OID': str(get_oid(file_)),
                'Error': '',
                'Code': 0,
                'Properties': {
                    'Date Created': '',
                    'Date Modified': '',
                    'Width': '',
                    'Height': '',
                    'Size': ''
                    }
                }
            if isinstance(file_, Image):
                filenameparts = file_.filename.split('.')
                fileext = filenameparts[-1].lower()
                thefile['File Type'] = fileext if len(filenameparts) > 1 and\
                    fileext in _imagetypes else 'png'
                if getsize:
                    try:
                        img = PILImage.open(file_.fp)
                        thefile['Properties']['Width'] = img.size[1]
                        thefile['Properties']['Height'] = img.size[0]
                        file_.fp.seek(0)
                    except:
                        thefile['Properties']['Width'] = 0
                        thefile['Properties']['Height'] = 0
            else:
                thefile['File Type'] = 'dir'

            thefile['Preview'] = url
            thefile['Properties']['Date Created'] = str(file_.created_at)
            thefile['Properties']['Date Modified'] = str(file_.modified_at)
        else:
            thefile['Error'] = 'File does not exist.'

        return thefile

    def getfolder(self):
        getsizes = False if self.params('getsizes') is False else True
        user = get_current()
        if hasattr(user, 'files'):
            images = user.files
        else:
            root = getSite()
            images = root.files

        result = []
        for img in images:
            result.append(self.getinfo(img, getsize=getsizes))

        return result

    def delete(self):
        user = get_current()
        path = self.params('path')
        file_ = None
        if path is not None:
            #file_ = traversal.traverse(self.context, path).get('context', None)
            file_ = get_file(path)

        if file_ and has_any_roles(
            user=user, roles=(('Owner', file_), 'Admin')):
            root = file_.__parent__
            root.delfromproperty('files', file_)
            return {'Path': self.request.resource_url(root, ''),
                    'Code': 0}

        return {'Error': 'There was an error renaming the file.'}

    def add(self):
        user = get_current()
        path = self.params('path')
        dir_ = None
        if path is not None:
            #dir_ = traversal.traverse(self.context, path).get('context', None)
            dir_ = get_file(path)

        if dir_ is None:
            dir_ = user

        field_storage = self.params('newfile')
        new_img = Image(
            fp=field_storage.file,
            title=field_storage.filename)
        new_img.mimetype = field_storage.type
        new_img.fp.seek(0)
        if hasattr(dir_, 'files'):
            dir_.addtoproperty('files', new_img)
        else:
            root = getSite()
            root.addtoproperty('files', new_img)

        grant_roles(user=user, roles=(('Owner', new_img), ))
        result = {
            'Path': get_file_url(new_img, self.request),
            'Name': new_img.title,
            'Code': 0
            }
        return '<textarea>'+json.dumps(result)+'</textarea>'

    def addfolder(self):
        #TODO
        return {}

    def download(self):
        path = self.params('path')
        file_ = None
        if path is not None:
            #file_ = traversal.traverse(self.context, path).get('context', None)
            file_ = get_file(path)

        if file_:
            return get_file_url(file_, self.request)

        return {}

    def __call__(self):
        operation_name = self.params('mode')
        if operation_name is not None:
            operation = getattr(self, operation_name, None)
            if operation is not None:
                return operation()

        return {}
