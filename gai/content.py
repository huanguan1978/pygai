#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os.path, urllib.request
import sqlite3, logging
import inject
from ext import extMethod
from jsend import success, error

from bottle import Bottle, request, response
from injector import injector
from gai.jsonvalidate import JsonValidateResult, jsonValidate, jsendSchemaQuacking
from gai.publish import publish
import setting

aiContent = Bottle()


@aiContent.route('/index/') # type: ignore
def index():
    return 'Contenet'

@aiContent.route('/input/', method=['POST','OPTIONS'], auth='username') # type: ignore
def input(injector:inject.Injector):
   
    params:dict = request.params # type: ignore
    writetofile = True if params.get('writetofile', '') else False

    response.headers['Content-Type'] = 'application/json'
    data = {'id':0, 'text':'',}
    jsonBody:dict = request.json # type: ignore

    jsonResult:JsonValidateResult = jsonValidate(jsonBody, jsendSchemaQuacking)
    if not jsonResult.ok:
        response.status = 409
        return error(jsonResult.message)

    # jsonBody = jsend.loads(jsonBody)
    # print(jsonBody)
    inputData = jsonBody['data']

    extPromptHandler = extMethod('gai/content', 'contentHandler')
    contentId = extPromptHandler(inputData['text'], writetofile, inputData) if extPromptHandler else contentHandler(inputData['text'], writetofile, inputData)
    data['id'] = contentId

    # return 200 Success
    return success(data).stringify(ensure_ascii=False)

def _download(files:str|list[str], path:str, logger:logging.Logger) -> list[str]:
    downloads = []
    fs = []
    
    if files and isinstance(files, str):
        fs = files.split(';')
    if files and isinstance(files, list):
        fs = files
    if not fs:
        return downloads
    
    for url in fs:
        saveto = os.path.join(path, os.path.basename(url))
        if os.path.exists(saveto):
            continue
        if url.startswith('http://') or url.startswith('https://'):
            logger.debug(f'_download {url}, saveto {saveto}')
            try:
                filename, headers = urllib.request.urlretrieve(url, saveto)
                downloads.append(os.path.basename(filename))
            except Exception as e:
                logger.error(e)

    return downloads

def contentHandler(text:str, writetofile:bool=False, inputData:dict={}) -> int:
    ''' input content '''
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    promptId = inputData.get('promptId') if inputData.get('promptId', '').isdigit() else None
    uploads = inputData['files'] if 'files' in inputData  else []
    downloads = []
    if uploads:
        downloads = _download(uploads, setting.downloads_path, logger)

    sql = 'INSERT INTO gaiContent(promptId, text, histCronId, histId, histPromptId) VALUES(?,?,?,?,?)'
    values = [promptId, text, inputData.get('cronId'), inputData.get('histId'), inputData.get('promptId'),]
    cu = db.execute(sql, values)
    contentId  = cu.lastrowid if cu.lastrowid else 0
    logger.debug(f'input, lastrowid:{contentId}, inputData:{inputData}, downloads:{downloads}')
    if downloads:
        files = ','.join(downloads)
        sql = 'UPDATE gaiContent SET files=json_array(?) WHERE id=?'
        db.execute(sql, [files, contentId,])

    if promptId:
        sql = f"UPDATE gaiPrompt SET quota=quota-1, enabled=quota>0, schedTime = DATETIME('now', intervalExpr), lastContentTime = datetime('now', 'localtime'), lastContentId = {contentId}  WHERE id = {promptId}"
        db.execute(sql)

    if contentId and writetofile:
        publishId = publish(contentId)
        if publishId:
            sql = f"UPDATE gaiContent SET publishTime = datetime('now', 'localtime'), publishId = {publishId}  WHERE id = {contentId}"
            db.execute(sql)

    return contentId