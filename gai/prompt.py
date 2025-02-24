#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sqlite3, logging, json
from bottle import Bottle, response, request
from bottle import urljoin  # type: ignore
import inject
from jsend import success
from setting import urlOfPart, uploads_urlpart
from injector import injector
from ext import extMethod

aiPrompt = Bottle()

@aiPrompt.route('/index/', method='GET') # type: ignore
def index():
    return 'Prompt'

@aiPrompt.route('/output/', method=['GET','OPTIONS'], auth='username') # type: ignore
def output(injector:inject.Injector):
    ''' output prompt data '''
    # print(request.url)
    urlbase = request.urlparts.scheme+'://'+request.urlparts.netloc # type: ignore
    # imgfile = urlOfPart('abc.jpg', uploads_urlpart, urlbase)
    # print(imgfile)
    
    qs:dict = request.query; # type: ignore
    id_ = int(qs.get('id', '0'))
    intervalId = int(qs.get('intervalId', '0'))
    topicId = int(qs.get('topicId', '0'))
    dirId = int(qs.get('dirId', '0'))

    extPromptHandler = extMethod('gai/prompt', 'promptHandler')
    data = extPromptHandler(id_, intervalId, topicId, dirId) if extPromptHandler else promptHandler(id_, intervalId, topicId, dirId)

    rtun = {}
    if data and {'id', 'type', 'text'}.issubset(data):
        if data.get('files'):
            files = [
                url if url.lower().startswith('http') else urlOfPart(url, uploads_urlpart, urlbase)
                    for url in data.get('files',[]) 
            ]                    
            data['files'] = files
        rtun = data

    # return 200 Success
    # response.status = 200 if data else 204
    response.headers['Content-Type'] = 'application/json'
    return success(rtun)
    return success(rtun).stringify(ensure_ascii=False)

@aiPrompt.route('/reset/', method=['GET','OPTIONS'], auth='username') # type: ignore
def reset(injector:inject.Injector):
    ''' Daily reset, reset lastContentId '''
    # db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore    

    extResetHandler = extMethod('gai/prompt', 'resetHandler')
    ok = extResetHandler() if extResetHandler else resetHandler()
    logger.debug(f'resetHandler, {ok}')

    data = {}
    # return 200 Success
    response.headers['Content-Type'] = 'application/json'
    return success(data)

def resetHandler() -> bool:
    ''' reset schedTime '''
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    sql = f"UPDATE gaiPrompt SET schedTime = DATETIME('now', t.expr), lastContentId = NULL AND lastContentTime = NULL WHERE enabled=1"
    db.execute(sql)
    
    return True

def promptHandler(promptId:int=0, intervalId:int=0, topicId:int=0, dirId:int=0) -> None|dict:
    ''' prompt data, required: id, type, text; optional: files, config, instText '''
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    sql = 'SELECT * FROM gaiPrompt WHERE enabled=1'
    if promptId:
        sql += f' AND id={promptId}'
    if intervalId:
        sql += f' AND intervalId={intervalId}'
    if topicId:
        sql += f' AND topicId={topicId}'
    if dirId:
        sql += f' AND dirId={dirId}'

    sql += " AND schedTime < datetime('now', 'localtime')"    
    sql += " ORDER BY CASE type WHEN 'genimg' THEN 0 WHEN 'gentxt' THEN 1 END, id DESC LIMIT 1"
    cu = db.execute(sql)
    row = cu.fetchone()
    cu.close()

    data = {}
    if row:
        config = json.loads(row['configText']) if row['configText'] else {}
        instConfig = json.loads(row['instConfig']) if row['instConfig'] else {}
        files = json.loads(row['files']) if row['files'] else []
        # if files:
        #     files = [urlOfPart(filename, uploads_urlpart, urlbase) for filename in files ]
        data = {
            'id':row['id'],
            'type':row['type'],
            'config': instConfig if instConfig else config,
            'instId':row['instId'] if row['instId'] else 0,
            'instName':row['instName'] if row['instName'] else '',
            'instText':row['instText'] if row['instText'] else '',
            'intervalName':row['intervalName'] if row['intervalName'] else '',
            'schedTime':row['schedTime'] if row['schedTime'] else '',
            'topicName':row['topicName'] if row['topicName'] else '',
            'text':row['text'],
            'files': files,
        }

    if {'id', 'type', 'text'}.issubset(data):
        return data

    return None