#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sqlite3
from beaker.middleware import SessionMiddleware, CacheMiddleware
from beaker.cache import CacheManager, Cache
from beaker.session import Session

# from beaker.util import parse_cache_config_options
import jsend

# fix: RuntimeError: Bottle requires gevent.monkey.patch_all() (before import)
# import gevent.monkey; gevent.monkey.patch_all()
import bottle

from bottle import Bottle, request, response, run, redirect
from bottle import template, TEMPLATE_PATH, static_file, install
from bottle_sqlite import SQLitePlugin
from bottlejwt import JwtPlugin
# from bottle_cors_plugin import cors_plugin

from bottle_injector import InjectorPlugin
import setting
tmpl_path = setting.tmpl_path
uploads_path = setting.uploads_path
downloads_path = setting.downloads_path
img_path :str = os.path.join(setting.public_path, 'img')
css_path :str = os.path.join(setting.public_path, 'css')
js_path :str = os.path.join(setting.public_path, 'js')
cache_control = setting.cache_control
session_path = setting.session_path
cache_path = setting.cache_path

TEMPLATE_PATH.insert(0, tmpl_path)
WHITELIST_USER = {}
WHITELIST_USERNAME = ''

root = Bottle()
app_session = SessionMiddleware(root, setting.session_opts)
app_cache = CacheMiddleware(app_session, setting.cache_opts)
apps = app_cache

# website hook, before_request
@root.hook('before_request')
def setup_request():

    request.session = request.environ['beaker.session']
    request.cache = request.environ['beaker.cache']

    cacheManager: CacheManager = request.cache
    request.dbmcache = cacheManager.get_cache('dbmcache', type='dbm')
    request.memcache = cacheManager.get_cache('memcache', type='memory')
    request.filecache = cacheManager.get_cache('filecache', type='file')

    if request.urlparts.path.startswith('/admin'): # type: ignore
        if not request.session.has_key('username'):
            redirect('/login/')


# website img
@root.route('/img/<filename:path>') # type: ignore
def img(filename:str):
    response = static_file(filename, root=img_path)
    if cache_control:
        response.set_header('Cache-Control', cache_control)
    return response

# website css
@root.route('/css/<filename:path>') # type: ignore
def css(filename:str):
    response = static_file(filename, root=css_path)
    if cache_control:
        response.set_header('Cache-Control', cache_control)
    return response    

# website js
@root.route('/js/<filename:path>') # type: ignore
def js(filename:str):
    response = static_file(filename, root=js_path)
    if cache_control:
        response.set_header('Cache-Control', cache_control)
    return response        

# website uploads
@root.route('/uploads/<filename:path>') # type: ignore
def uploads(filename:str):
    response = static_file(filename, root=uploads_path)
    if cache_control:
        response.set_header('Cache-Control', cache_control)
    return response 

# website uploads
@root.route('/downloads/<filename:path>') # type: ignore
def downloads(filename:str):
    resposne = static_file(filename, root=downloads_path)
    if cache_control:
        response.set_header('Cache-Control', cache_control)
    return response

# website index
@root.route('/') # type: ignore
def index():
    return 'index'

# website submit username and password, generate JWT
@root.route('/signin', method='POST') # type: ignore
def signin():
    response.headers['Content-Type'] = 'application/json'
    params:dict[str:str|None] = request.params;  # type: ignore
    username = params.get('username')
    password = params.get('password')
    # print(username)
    # print(password)
    if username and password and (username in WHITELIST_USER) and (password == WHITELIST_USER[username]):
        jwt = JwtPlugin.encode({'username':username})        
        data = {'jwt':jwt}
        return jsend.success(data).stringify()

    response.status = 409
    return jsend.error('invalid username and password').stringify()



# website jwtinfo
@root.route('/jwtinfo', auth='username') # type: ignore
def jwtinfo(auth):
    response.headers['Content-Type'] = 'application/json'
    return auth

# website testdb
@root.route('/testdb') # type: ignore
def testdb(db:sqlite3.Connection):
    sql = 'SELECT sqlite_version() AS version'
    cx = db.execute(sql)
    row = cx.fetchone()

    output = row['version']
    return output

# website testcache
@root.route('/testcache') # type: ignore
def testcache():
    memcache:Cache = request.memcache
    memcache.put('test1', 'value1')
    memcache.put('test2', 'value2')
    test1 = memcache.get('test1')
    test2 = memcache.get('test2')

    output = {
        'test1':test1,
        'test2':test2
    }
    return output

# website testsess
@root.route('/testsess') # type: ignore
def testsess():
    session:Session = request.session
    if not session.has_key('counter'):
        request.session['counter'] = 0
    else:
        request.session['counter'] += 1
    session.save()

    counter = session.get('counter')
    output = {
        'counter':counter,
    }
    return output


@root.route('/hello/<name>') # type: ignore
def hello(name:str)->str:
    tmpl = template('index.tpl', name=name, pageTitle='HelloPage')
    return tmpl


# website JWT validation callback
def jwtValidation(auth:dict, name:str)->bool:
    username = auth.get(name)
    if username in WHITELIST_USER:
        return True
    return False

if __name__ == '__main__':

    if not os.path.exists(uploads_path):
        os.makedirs(uploads_path)
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)

    mkdocs_default_docs = os.path.join(setting.mkdocs_default_path, setting.mkdocs_default_site, 'docs')
    from utils import init_mkdocs
    init_mkdocs(mkdocs_default_docs)

    from gai import prompt as gaiPrompt
    from gai import content as qaiContent
    from injector import injector as my_injector

    dbfile = setting.app_setting.get('db.dbfile')
    jwtkey = setting.app_setting.get('jwt.secret')

    allitems = setting.app_setting.items()
    prefix = 'user.'
    for key, val in allitems:
        if key.startswith(prefix): 
            key = key[len(prefix):]
            WHITELIST_USER[key] = val

    root.install(SQLitePlugin(dbfile=dbfile))
    '''
    prompt.prompt.install(SQLitePlugin(dbfile=dbfile))
    content.content.install(SQLitePlugin(dbfile=dbfile))
    '''
    # root.install(cors_plugin('*'))
    '''
    prompt.prompt.install(cors_plugin('*'))
    content.content.install(cors_plugin('*'))
    '''
    root.install(JwtPlugin(jwtValidation, jwtkey))
    gaiPrompt.aiPrompt.install(JwtPlugin(jwtValidation, jwtkey))
    qaiContent.aiContent.install(JwtPlugin(jwtValidation, jwtkey))

    gaiPrompt.aiPrompt.install(InjectorPlugin(my_injector))
    qaiContent.aiContent.install(InjectorPlugin(my_injector))
    root.mount('/aiprompt', gaiPrompt.aiPrompt)
    root.mount('/aicontent', qaiContent.aiContent)

    from signin import signIn
    signIn.install(InjectorPlugin(my_injector))    
    root.mount('/login', signIn)

    from admin.index import admin
    admin.install(InjectorPlugin(my_injector))    
    root.mount('/admin/', admin)
    
    host = setting.app_setting.get('wsgi.host')
    port = setting.app_setting.get('wsgi.port')
    debug = setting.app_setting.get('wsgi.port')
    reloader = setting.app_setting.get('wsgi.reloader')    
    run(app=apps, host=host, port=port, debug=debug, reloader=reloader)
