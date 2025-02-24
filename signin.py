#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import inject
from jsend import error

from bottle import Bottle, request, response, template, redirect
from bottlejwt import JwtPlugin
from beaker.session import Session

import setting

signIn = Bottle()

@signIn.route('/', method=['HEAD', 'GET', 'POST', 'OPTIONS'] ) # type: ignore
def index(injector:inject.Injector):
    logger = injector.get_instance(logging.Logger) # type: ignore

    if request.method.upper() in ('GET', 'HEAD', 'OPTIONS'):
        tmpl = template('login.htm', pageTitle='LoginPage')
        return tmpl
    
    formData:dict = request.forms # type: ignore
    username = formData.get('username')
    password = formData.get('password')
    # logger.debug('%s %s', username, password)

    account = {}
    allitems = setting.app_setting.items()
    prefix = 'user.'
    for key, val in allitems:
        if key.startswith(prefix): 
            key = key[len(prefix):]
            account[key] = val
    # logger.info(account)
    if username and password and (username in account) and (password == account[username]):
        logger.debug('--ok--')
        jwt = JwtPlugin.encode({'username':username})

        session:Session = request.session
        session['username'] = username
        session['jwt'] = jwt
        session.save()

        redirect('/admin/')
        # return json.dumps(jsend.success(data))
    
    response.status = 403
    return error('invalid username and password')