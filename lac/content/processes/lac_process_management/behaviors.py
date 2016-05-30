# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.httpexceptions import HTTPFound
from elasticsearch.helpers import bulk

from dace.util import getSite
from dace.objectofcollaboration.principal.util import (
    has_role)
from dace.processinstance.activity import (
    InfiniteCardinality)

from lac.tests.data.cities import (
    cities_directory, departments_directory, countries_directory)
from lac.content.resources import normalize_value
from lac.content.interface import ICreationCulturelleApplication
from lac import _, log


def populate_rm(root):
    resourcemanager = root.resourcemanager
    rm_populated = resourcemanager.create_index()
    if not rm_populated:
        try:
            es = resourcemanager.index
            departement_mapping = {
                        'department_suggest': {"type": "completion",
                                            "index_analyzer": "default",
                                            "search_analyzer": "default",
                                            "payloads": True
                                    },
                        'department_normalized_name':
                               {'type': 'string', 'index': 'not_analyzed'},
                        'country_normalized_name':
                               {'type': 'string', 'index': 'not_analyzed'},
                        'country_alias':
                               {'type': 'string', 'index': 'not_analyzed'},
                        'department_alias':
                               {'type': 'string', 'index': 'not_analyzed'}}

            country_mapping = {
                        'country_suggest': {"type": "completion",
                                        "index_analyzer": "default",
                                        "search_analyzer": "default",
                                        "payloads": True
                                    },
                        'country_normalized_name':
                               {'type': 'string', 'index': 'not_analyzed'},
                        'country_alias':
                               {'type': 'string', 'index': 'not_analyzed'}}

            city_mapping = {
                        'city_suggest': {"type": "completion",
                                        "index_analyzer": "default",
                                        "search_analyzer": "default",
                                        "payloads": True
                                    },
                       'city_normalized_name':
                               {'type': 'string', 'index': 'not_analyzed'},
                       'department_normalized_name':
                               {'type': 'string', 'index': 'not_analyzed'},
                       'country_normalized_name':
                               {'type': 'string', 'index': 'not_analyzed'},
                       'city_alias':
                               {'type': 'string', 'index': 'not_analyzed'},
                       'department_alias':
                               {'type': 'string', 'index': 'not_analyzed'},
                       'country_alias':
                               {'type': 'string', 'index': 'not_analyzed'}}

            geo_location_mapping = {
                "oid": {
                  "type": "string"
                },
                "location": {
                  "type": "geo_point"
                }
            }

            es.indices.put_mapping(
                index='lac',
                doc_type="geo_location",
                body={
                        "geo_location": {
                            'properties': geo_location_mapping
                        } 
                }
            )

            es.indices.put_mapping(
                index='lac',
                doc_type="department",
                body={
                        "department": {
                            'properties': departement_mapping
                        } 
                }
            )

            es.indices.put_mapping(
                index='lac',
                doc_type="country",
                body={
                        "country": {
                            'properties': country_mapping
                        } 
                }
            )

            es.indices.put_mapping(
                index='lac',
                doc_type="city",
                body={
                        "city": {
                            'properties': city_mapping
                        }
                }
            )

            def get_actions():
                for value in departments_directory.values():
                    action = {
                            "_op_type": 'index',
                            "_index": "lac",
                            "_type": "department",
                            "_source": normalize_value(value)
                            }
                    yield action


                for value in countries_directory.values():
                    action = {
                            "_op_type": 'index',
                            "_index": "lac",
                            "_type": "country",
                            "_source": normalize_value(value)
                            }
                    yield action

                for value in cities_directory.values():
                    action = {
                            "_op_type": 'index',
                            "_index": "lac",
                            "_type": "city",
                            "_source": normalize_value(value)
                            }
                    yield action


            bulk(es,
                index="lac",
                actions=get_actions(),
                chunk_size=50,
                refresh=False)
        except Exception as e:
            log.exception(e)


def update_roles_validation(process, context):
    return has_role(role=('Admin',))


class Update(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-repeat'
    style_order = 10
    submission_title = _('Update')
    context = ICreationCulturelleApplication
    roles_validation = update_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        populate_rm(root)
        runtime = root['runtime']
        processes = list(runtime.processes)
        if self.process in processes:
            processes.remove(self.process)

        [runtime.delfromproperty('processes', p)
         for p in processes if getattr(p.definition, 'isUnique', False)]
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, ""))


#TODO behaviors
