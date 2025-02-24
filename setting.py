#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
from math import ceil
from urllib.parse import urljoin
from bottle import default_app
from ast import literal_eval

app_path :str = os.path.dirname(os.path.realpath(__file__))
ext_path :str = os.path.join(os.path.dirname(app_path), 'pygaiext') # app_path/../pygaiext
public_path :str = os.path.join(app_path,'public')
tmpl_path :str = os.path.join(public_path, 'tpl')
uploads_path :str = os.path.join(public_path, 'uploads')
downloads_path :str = os.path.join(public_path, 'downloads')
uploads_urlpart :str = '/uploads/'
downloads_urlpart :str = '/downloads/'

mkdocs_default_path = '~/Documents/sites'
mkdocs_default_site = 'MyWebSite'

page_size :int = 10 # pagination, admin page size
cache_control :str  = '' # html static file cache control

default_app = default_app()
default_app.config.load_config(os.path.join(app_path,'config', 'setting.ini'))
app_setting = default_app.config
# print(app_setting)

mkdocs_default_path = os.path.expandvars(os.path.expanduser(mkdocs_default_path))
if app_setting.get('mkdocs.default_path'):
    mkdocs_default_path :str = os.path.expandvars(os.path.expanduser(app_setting.get('mkdocs.default_path')))
if app_setting.get('mkdocs.default_site'):
    mkdocs_default_site :str = app_setting.get('mkdocs.default_site')

if app_setting.get('staticfile.cache_control'):
    cache_control :str = app_setting.get('staticfile.cache_control')
if app_setting.get('media.uploads_path'):
    uploads_path :str = os.path.expandvars(os.path.expanduser(app_setting.get('media.uploads_path')))
if app_setting.get('media.downloads_path'):
    downloads_path :str = os.path.expandvars(os.path.expanduser(app_setting.get('media.downloads_path')))
if app_setting.get('media.uploads_urlpart'):
    uploads_urlpart :str = app_setting.get('media.uploads_urlpart')
if app_setting.get('media.downloads_urlpart'):
    downloads_urlpart :str = app_setting.get('media.downloads_urlpart')

session_path = os.path.join(app_path, 'session')
session_path_savedata = os.path.join(session_path, 'data')
session_path_savelock = os.path.join(session_path, 'lock')
cache_path = os.path.join(app_path, 'cache')
cache_path_savedata = os.path.join(cache_path, 'data')
cache_path_savelock = os.path.join(cache_path, 'lock')

if app_setting.get('session.path'):
    session_path = os.path.expandvars(os.path.expanduser(app_setting.get('session.path')))
if not os.path.exists(session_path):
    os.makedirs(session_path, exist_ok=True)
if not os.path.exists(session_path_savedata):
    os.makedirs(session_path_savedata, exist_ok=True)    
if not os.path.exists(session_path_savelock):
    os.makedirs(session_path_savelock, exist_ok=True)    
if app_setting.get('cache.path'):
    cache_path = os.path.expandvars(os.path.expanduser(app_setting.get('cache.path')))
if not os.path.exists(cache_path):
    os.makedirs(cache_path, exist_ok=True)
if not os.path.exists(cache_path_savedata):
    os.makedirs(cache_path_savedata, exist_ok=True)    
if not os.path.exists(cache_path_savelock):
    os.makedirs(cache_path_savelock, exist_ok=True)

session_opts = {
    'session.type': app_setting.get('session.type'),
    'session.cookie_expires': app_setting.get('session.cookie_expires'),
    'session.data_dir': session_path_savedata,
    'session.lock_dir': session_path_savelock,
    'session.auto': True if literal_eval(app_setting.get('session.auto')) else False,
}
if app_setting.get('session.cookie_domain'):
    session_opts['session.cookie_domain'] = app_setting.get('session.cookie_domain')

cache_opts = {
    'cache.type': app_setting.get('cache.type'),
    'cache.data_dir': cache_path_savedata,
    'cache.lock_dir': cache_path_savelock,
}
if app_setting.get('cache.expire'):
    session_opts['cache.expire'] = app_setting.get('cache.expire')


def urlOfPart(file:str, urlpart:str, urlbase:str) -> str:
    ''' urlOfPart(file, urlpart, urlbase) -> url
        urlpart is Downloads or Uploads
        urlbase is the base url of the server    
    '''
    if urlpart.lower().startswith('http'):
        return urljoin(urlpart, file)
    return urljoin(urlbase, urljoin(urlpart, file))

def totalPages(totalRecords:int, pageSize:int) -> int:
    ''' totalPages, 5/10 -> 1, 13/10 -> 2'''
    return ceil(totalRecords / pageSize)