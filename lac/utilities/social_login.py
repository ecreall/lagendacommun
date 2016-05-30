# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.threadlocal import get_current_registry
from pyramid.config import Configurator

from velruse.providers.facebook import add_facebook_login
from velruse.providers.twitter import add_twitter_login
from velruse.providers.google_oauth2 import add_google_login


# velruse.facebook.consumer_key = 4935216047502512
# velruse.facebook.consumer_secret = 757f30fea4f1164r53387508806ae59c
# velruse.facebook.scope = email

# velruse.twitter.consumer_key = ebyQK6ZeZbYu5kwyIHXompLo4
# velruse.twitter.consumer_secret = 4GcOd1wIwh3aKR8OTkjt<uuNVOOzJcnTKz02tHbHZ8B0SOhVPYi

# velruse.google.consumer_key = 707177007720-upcd7bd104g88fv63tuoa1xfg2g1lhocmc5.apps.googleusercontent.com
# velruse.google.consumer_secret = 8CynIw9Nq_6YjEx3b6RI6MWvW
# velruse.google.realm = http://0.0.0.0:6543

NAME_RE_MAPPING = {ord(c): None for c in '-_. '}


def get_social_login_name(id_, site):
    return id_+'-'+site.__name__.translate(NAME_RE_MAPPING)


def add_site_facebook_login(site, app):
    registry = get_current_registry()
    config = Configurator(registry=registry, autocommit=True)
    name = app.application_site_id
    add_facebook_login(
        config,
        consumer_key=getattr(app, 'consumer_key', ''),
        consumer_secret=getattr(app, 'consumer_secret', ''),
        scope=getattr(app, 'scop', ''),
        login_path='/login/'+name,
        callback_path='/login/'+name+'/callback',
        name=name)


def add_site_twitter_login(site, app):
    registry = get_current_registry()
    config = Configurator(registry=registry, autocommit=True)
    name = app.application_site_id
    add_twitter_login(
        config,
        consumer_key=getattr(app, 'consumer_key', ''),
        consumer_secret=getattr(app, 'consumer_secret', ''),
        login_path='/login/'+name,
        callback_path='/login/'+name+'/callback',
        name=name)


def add_site_google_login(site, app):
    registry = get_current_registry()
    config = Configurator(registry=registry, autocommit=True)
    name = app.application_site_id
    add_google_login(
        config,
        consumer_key=getattr(app, 'consumer_key', ''),
        consumer_secret=getattr(app, 'consumer_secret', ''),
        scope=getattr(app, 'scope', ''),
        login_path='/login/'+name,
        callback_path='/login/'+name+'/callback',
        name=name)


def init_sites_social_login(root):
    for site in root.site_folders:
        for app in getattr(site, 'applications', []):
            app.init_login()
