#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sqlite3, logging, json, mimetypes, os.path

from bottle import Bottle, request, response, template, redirect
from beaker.session import Session

import inject

from gai.publish import publish
from setting import totalPages, uploads_path, urlOfPart, uploads_urlpart, page_size
from utils import blog_mkdocs, init_mkdocs
from jsend import success, fail, error

admin = Bottle()

@admin.route('/') # type: ignore
def index():
    session:Session = request.session
    username = session['username'] if session.has_key('username') else ''
    jwt = session['jwt'] if session.has_key('jwt') else ''

    if username:
        return template('admin/index.htm', name=username, jwt=jwt,pageTitle='AdminPage')

    return redirect('/login/', code=403)

@admin.route('/topic/') # type: ignore
def topic_list(injector:inject.Injector):
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore
    sql = 'SELECT * FROM gaiTopic ORDER BY id DESC'
    cu = db.execute(sql)
    rows = cu.fetchall()
    cu.close()

    return template('admin/topic_list.htm', pageTitle='TopicPage', topics=rows)

@admin.route('/topic/edit/', method=['HEAD', 'GET', 'POST', 'PUT', 'OPTIONS'] ) # type: ignore
def topic_edit(injector:inject.Injector):
    alert = {}
    params:dict = request.params # type: ignore
    id_ = int(params.get('id', '0'))
    row = {'id':'0', 'name':'', 'memo':''}
    tplfile = 'admin/topic_edit.htm'
    pageTitle = 'TopicPage'

    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    if request.method.upper() in ('HEAD', 'GET', 'OPTIONS') :
        if id_:
            sql = 'SELECT * FROM gaiTopic WHERE id=?'
            cu = db.execute(sql, [id_])
            one = cu.fetchone()
            cu.close()
            if one:
                row = one

        return template('admin/topic_edit.htm', pageTitle=pageTitle, topic=row)

    if request.method.upper() in ('POST', 'PUT'):
        row['name'] = params.get('name', '')
        row['memo'] = params.get('memo', '')

        if int(id_) == 0:
            sql = 'INSERT INTO gaiTopic(name, memo) VALUES(?,?)'
            cu = db.execute(sql, [row['name'], row['memo']])
            id_ = cu.lastrowid
            cu.close()
            alert['success'] = ['created topic: ' + str(id_)]
        else:
            sql = 'UPDATE gaiTopic SET name=?, memo=? WHERE id=?'
            cu = db.execute(sql, [row['name'], row['memo'], id_])
            cu.close()
            alert['success'] = ['updated topic: ' + str(id_)]

        return template('admin/topic_edit.htm', pageTitle=pageTitle, topic=row, alert=alert)


@admin.route('/instruct/') # type: ignore
def instruct_list(injector:inject.Injector):
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore
    sql = 'SELECT * FROM gaiInstruction ORDER BY id DESC'
    cu = db.execute(sql)
    rows = cu.fetchall()
    cu.close()

    return template('admin/instruct_list.htm', pageTitle='InstructPage', instruct=rows)

@admin.route('/instruct/edit/', method=['HEAD', 'GET', 'POST', 'PUT', 'OPTIONS'] ) # type: ignore
def instruct_edit(injector:inject.Injector):
    alert = {}
    params:dict = request.params # type: ignore
    id_ = int(params.get('id', '0'))
    row = {'id':'0', 'name':'', 'text':'', 'config':'', 'memo':''}
    tplfile = 'admin/instruct_edit.htm'
    pageTitle = 'InstructPage'

    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    if request.method.upper() in ('HEAD', 'GET', 'OPTIONS'):
        if id_:
            sql = 'SELECT * FROM gaiInstruction WHERE id=?'
            cu = db.execute(sql, [id_])
            one = cu.fetchone()
            cu.close()
            if one:
                row = one

        return template(tplfile, pageTitle=pageTitle, instruct =row)

    if request.method.upper() in ('POST', 'PUT'):
        row['name'] = params.get('name', '')
        row['text'] = params.get('text', '')
        row['config'] = params.get('config', '')
        row['memo'] = params.get('memo', '')

        if int(id_) == 0:
            sql = 'INSERT INTO gaiInstruction(name, text, config, memo) VALUES(?,?,?,?)'
            cu = db.execute(sql, [row['name'], row['text'], row['config'], row['memo']])
            id_ = cu.lastrowid
            cu.close()
            alert['success'] = ['created instruction: ' + str(id_)]
        else:
            sql = 'UPDATE gaiInstruction SET name=?, text=?, config=?, memo=? WHERE id=?'
            cu = db.execute(sql, [row['name'], row['text'], row['config'], row['memo'], id_])
            cu.close()
            alert['success'] = ['updated instruction: ' + str(id_)]

        return template(tplfile, pageTitle=pageTitle, instruct=row, alert=alert)


@admin.route('/directory/') # type: ignore
def directory_list(injector:inject.Injector):
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore
    sql = 'SELECT * FROM gaiDirectory ORDER BY id DESC'
    cu = db.execute(sql)
    rows = cu.fetchall()
    cu.close()

    return template('admin/directory_list.htm', pageTitle='DirectoryPage', directories=rows)

@admin.route('/directory/edit/', method=['HEAD', 'GET', 'POST', 'PUT', 'OPTIONS'] ) # type: ignore
def directory_edit(injector:inject.Injector):
    alert = {}
    params:dict = request.params # type: ignore
    id_ = int(params.get('id', '0'))
    row = {'id':'0', 'name':'', 'path':'', 'tmpl':'default'}
    tplfile = 'admin/directory_edit.htm'
    pageTitle = 'DirectoryPage'

    tmpls = {'default':'mkdocs'}

    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    if request.method.upper() in ('HEAD', 'GET', 'OPTIONS'):
        if id_:
            sql = 'SELECT * FROM gaiDirectory WHERE id=?'
            cu = db.execute(sql, [id_])
            one = cu.fetchone()
            cu.close()
            if one:
                row = one

        return template(tplfile, pageTitle=pageTitle, directory=row, tmpls=tmpls)

    if request.method.upper() in ('POST', 'PUT'):
        row['name'] = params.get('name', '')
        row['path'] = params.get('path', '')
        row['tmpl'] = params.get('tmpl', '')

        valid = False
        path:str  = row['path']
        if not path.endswith(os.path.sep):
            path += os.path.sep
        logger.debug(f'/directory/edit/, path: {path}')
        if path.endswith(f'{os.path.sep}docs{os.path.sep}') and os.path.exists(os.path.expandvars(os.path.expanduser(path))):
            init_mkdocs(path)
            valid = True

        if valid:
            if int(id_) == 0:
                sql = 'INSERT INTO gaiDirectory(name, path, tmpl) VALUES(?,?,?)'
                cu = db.execute(sql, [row['name'], row['path'], row['tmpl']])
                id_ = cu.lastrowid
                cu.close()
                alert['success'] = ['created directory: ' + str(id_)]
            else:
                sql = 'UPDATE gaiDirectory SET name=?, path=?, tmpl=? WHERE id=?'
                cu = db.execute(sql, [row['name'], row['path'], row['tmpl'], id_])
                cu.close()
                alert['success'] = ['updated directory: ' + str(id_)]
        else:
            alert['danger'] = ['invalid mkdocs project path. ']

        return template(tplfile, pageTitle=pageTitle, directory=row, tmpls=tmpls, alert=alert)


@admin.route('/config/') # type: ignore
def config_list(injector:inject.Injector):
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore
    sql = 'SELECT * FROM gaiConfig ORDER BY id DESC'
    cu = db.execute(sql)
    rows = cu.fetchall()
    cu.close()

    tplfile = 'admin/config_list.htm'
    pageTitle = 'ConfigPage'
    return template(tplfile, pageTitle=pageTitle, configs=rows)

@admin.route('/config/edit/', method=['HEAD', 'GET', 'POST', 'PUT', 'OPTIONS'] ) # type: ignore
def config_edit(injector:inject.Injector):
    alert = {}
    params:dict = request.params # type: ignore
    id_ = int(params.get('id', '0'))
    row = {'id':'0', 'type':'gentxt', 'name':'', 'text':''}
    tplfile = 'admin/config_edit.htm'
    pageTitle = 'ConfigPage'

    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    if request.method.upper() in ('HEAD', 'GET', 'OPTIONS'):
        if id_:
            sql = 'SELECT * FROM gaiConfig WHERE id=?'
            cu = db.execute(sql, [id_])
            one = cu.fetchone()
            cu.close()
            if one:
                row = one
        return template(tplfile, pageTitle=pageTitle, config =row)

    if request.method.upper() in ('POST', 'PUT'):
        row['type'] = params.get('type', '')
        row['name'] = params.get('name', '')
        row['text'] = params.get('text', '')

        if int(id_) == 0:
            sql = 'INSERT INTO gaiConfig(type, name, text) VALUES(?,?)'
            cu = db.execute(sql, [row['type'], row['name'], row['text']])
            id_ = cu.lastrowid
            cu.close()
            alert['success'] = ['created config: ' + str(id_)]
        else:
            sql = 'UPDATE gaiConfig SET type=?, name=?, text=? WHERE id=?'
            cu = db.execute(sql, [row['type'], row['name'], row['text'], id_])
            cu.close()
            alert['success'] = ['updated config: ' + str(id_)]

        return template(tplfile, pageTitle=pageTitle, config=row, alert=alert)


@admin.route('/prompt/') # type: ignore
def prompt_list(injector:inject.Injector):
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    params:dict = request.params # type: ignore
    page = int(params.get('page', '1')) # current page
    type = params.get('type', '') # search type
    keyword = params.keyword # type: ignore # search keyword
    logger.debug(f'page: {page}, type: {type}, keyword: {keyword}')
    where = ''
    if type and keyword:
        where = f' WHERE {type} LIKE ?'
    parameters = [f'%{keyword}%'] if where else []

    totalRecords = 0
    pages:int = 0
    sql = f'SELECT count(*) AS total FROM gaiPrompt {where}'
    logger.debug(sql)
    cu = db.execute(sql, parameters)
    row = cu.fetchone()
    totalRecords = row['total']
    if totalRecords > 0:
        pages = totalPages(totalRecords, page_size)

    sql = f'SELECT * FROM gaiPrompt {where} ORDER BY id DESC LIMIT {page_size} OFFSET {(page-1)*page_size}'
    logger.debug(sql)
    cu = db.execute(sql, parameters)
    rows = cu.fetchall()
    cu.close()

    tplfile = 'admin/prompt_list.htm'
    pageTitle = 'PromptPage'
    return template(tplfile, pageTitle=pageTitle, prompts=rows, page=page, pages=pages, type=type, keyword=keyword)

@admin.route('/prompt/edit/', method=['HEAD', 'GET', 'POST', 'PUT', 'OPTIONS'] ) # type: ignore
def prompt_edit(injector:inject.Injector):
    alert = {}
    params:dict = request.params # type: ignore
    id_ = int(params.get('id', '0'))
    row = {'id':0, 'enabled':1, 'isShowInContent':0, 'quota':10, 'intervalId':'2', 'topicId':'', 'configId':'', 'instId':'', 'dirId':'', 'type':'gentxt', 'text':'', 'memo':'', 'files':''}
    tplfile = 'admin/prompt_edit.htm'
    pageTitle = 'PromptPage'

    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    intervals = _option(db, 'gaiInterval')
    topics = _option(db, 'gaiTopic')
    configs = _option(db, 'gaiConfig')
    instructions = _option(db, 'gaiInstruction')
    paths = _option(db, 'gaiDirectory')

    if request.method.upper() in ('HEAD', 'GET', 'OPTIONS'):
        if id_:
            sql = 'SELECT * FROM gaiPrompt WHERE id=?'
            cu = db.execute(sql, [id_])
            one = cu.fetchone()
            cu.close()
            if one:
                row = one
        return template(tplfile, pageTitle=pageTitle, prompt =row, topics=topics, intervals=intervals, configs=configs, instructions=instructions, paths=paths)

    if request.method.upper() in ('POST', 'PUT'):
        for key in row.keys():
            row[key] = params.get(key, '')
        logger.debug(f'save row: {row}')

        if id_ == 0:
            sql = 'INSERT INTO gaiPrompt(enabled, isShowInContent, quota, intervalId, topicId, configId, instId, dirId, type, text, memo) VALUES(?,?,?,?, ?,?,?,?, ?,?,?)'
            cu = db.execute(sql, [row['enabled'], row['isShowInContent'], row['quota'], row['intervalId'], row['topicId'], row['configId'], row['instId'], row['dirId'], row['type'], row['text'], row['memo']])
            id_ = cu.lastrowid
            cu.close()
            alert['success'] = ['created prompt: ' + str(id_)]
        else:
            sql = 'UPDATE gaiPrompt SET enabled=?, isShowInContent=?, quota=?, intervalId=?, topicId=?, configId=?, instId=?, dirId=?, type=?, text=?, memo=? WHERE id=?'
            cu = db.execute(sql, [row['enabled'], row['isShowInContent'], row['quota'], row['intervalId'], row['topicId'], row['configId'], row['instId'], row['dirId'], row['type'], row['text'], row['memo'], id_])
            cu.close()
            alert['success'] = ['updated prompt: ' + str(id_)]

        sql = 'UPDATE gaiPrompt SET intervalId = 0, intervalName = NULL WHERE id=?'
        if row['intervalId'] != '':
            row['intervalId'] = int(row['intervalId'])
            sql = "UPDATE gaiPrompt AS p SET schedTime = DATETIME('now', t.expr), intervalExpr = t.expr, intervalName = t.name FROM gaiInterval AS t WHERE p.id = ? AND p.intervalId = t.id"
        cu = db.execute(sql, [id_])
        cu.close()

        sql = 'UPDATE gaiPrompt SET topicId = 0, topicName = NULL WHERE id=?'
        if row['topicId'] != '':
            row['topicId'] = int(row['topicId'])
            sql = 'UPDATE gaiPrompt AS p SET topicName = t.name FROM gaiTopic AS t WHERE p.id = ? AND p.topicId = t.id'
        cu = db.execute(sql, [id_])
        cu.close()

        sql = 'UPDATE gaiPrompt SET configId = NULL, configName = NULL WHERE id=?'
        if row['configId'] != '':
            row['configId'] = int(row['configId'])
            sql = 'UPDATE gaiPrompt AS p SET configName = c.name, configText = c.text FROM gaiConfig AS c WHERE p.id = ? AND p.configId = c.id'
        cu = db.execute(sql, [id_])
        cu.close()

        sql = 'UPDATE gaiPrompt SET instId = NULL, instName = NULL, instText = NULL WHERE id=?'
        if row['instId'] != '':
            row['instId'] = int(row['instId'])
            sql = 'UPDATE gaiPrompt AS p SET instName = i.name, instText = i.text FROM gaiInstruction AS i WHERE  p.id = ? AND p.instId = i.id'
        cu = db.execute(sql, [id_])
        cu.close()

        sql = 'UPDATE gaiPrompt SET dirId = NULL, dirName = NULL, dirPath = NULL, dirTmpl = NULL WHERE id=?'
        if row['dirId'] != '':
            row['dirId'] = int(row['dirId'])
            sql = 'UPDATE gaiPrompt AS p SET dirName = d.name, dirPath = d.path, dirTmpl = d.Tmpl FROM gaiDirectory AS d WHERE  p.id = ? AND p.dirId = d.id'
        cu = db.execute(sql, [id_])
        cu.close()

        # TODO: files
        return template(tplfile, pageTitle=pageTitle, prompt=row, alert=alert, intervals=intervals, topics=topics, configs=configs, instructions=instructions, paths=paths)

def _option(db:sqlite3.Connection, tableName:str) ->dict:
    option = {}
    sql = 'SELECT id, name FROM ' + tableName + ' ORDER BY name'
    cu = db.execute(sql)
    rows = cu.fetchall()
    cu.close()
    for row in rows:
        option[row['id']] = row['name']

    return option

@admin.route('/prompt/files/<id:int>', method=['HEAD', 'GET', 'POST', 'PUT', 'OPTIONS'] ) # type: ignore
def prompt_files(injector:inject.Injector, id:int):
    ''' files of prompt, new or delete'''
    alert = {}
    params:dict = request.params # type: ignore
    id_ = id
    files:list[str] = []
    urlfiles:list[str] = []
    tplfile = 'admin/prompt_files.htm'
    pageTitle = 'FilePage'
    urlbase = request.urlparts.scheme+'://'+request.urlparts.netloc # type: ignore
    # imgfile = urlOfPart('abc.jpg', uploads_urlpart, urlbase)

    if id_ == 0:
        alert['warning'] = ['prompt not found: ' + str(id_)]
        return template(tplfile, pageTitle=pageTitle, id_=id_, files=files, urlfiles=urlfiles, alert=alert)

    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    sql = 'SELECT files FROM gaiPrompt WHERE id=?'
    cu = db.execute(sql, [id_])
    row = cu.fetchone()
    cu.close()

    if row and row['files']:
        files = json.loads(row['files'])

    # load prompt files, or delete after load
    if request.method.upper() in ('HEAD', 'GET', 'OPTIONS'):
        delete = params.get('delete', '')
        index = params.get('index', '')
        if delete and index.isdigit():
            filename = files[int(index)]
            logger.debug(f'request index:{index}, delete: {delete}')

            del files[int(index)]
            jsonfiles = json.dumps(files, ensure_ascii=False)
            sql = 'UPDATE gaiPrompt SET files=? WHERE id=?'
            cu = db.execute(sql, [jsonfiles, id_])
            cu.close()

            localfile = os.path.join(uploads_path, filename)
            if os.path.exists(localfile):
                os.remove(localfile)
                logger.debug(f'remove file: {localfile}')
            alert['success'] = ['deleted file: ' + filename]

        if files:
            urlfiles = [urlOfPart(filename, uploads_urlpart, urlbase) for filename in files ]
        return template(tplfile, pageTitle=pageTitle, id_=id_, files = files, urlfiles=urlfiles, alert=alert)

    # new prompt file, upload
    if request.method.upper() in ('POST', 'PUT'):
        upload     = request.files.get('upload') # type: ignore
        if upload:
            # print(vars(upload))
            filename = os.path.basename(upload.raw_filename)
            logger.debug(f'upload file: {filename}')
            content_type:str = upload.content_type.lower()
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename) # type: ignore
            # allow image, video, audio, pdf
            if content_type.startswith('image') or content_type.startswith('video') or content_type.startswith('audio') or content_type.startswith('application/pdf'):
                save_file = os.path.join(uploads_path, filename)
                upload.save(save_file, overwrite=True) # appends upload.filename automatically

                files.append(filename)
                jsonfiles = json.dumps(files, ensure_ascii=False) # ensure_ascii=False, not escape unicode, eg. chinese
                sql = 'UPDATE gaiPrompt SET files=? WHERE id=?'
                cu = db.execute(sql, [jsonfiles, id_])
                cu.close()
                alert['success'] = ['uploaded file: ' + filename]
            else:
                alert['danger'] = ['file type not supported: ' + filename]

        if files:
            urlfiles = [urlOfPart(filename, uploads_urlpart, urlbase) for filename in files ]
        return template(tplfile, pageTitle=pageTitle,  id_=id_, files=files, urlfiles=urlfiles, alert=alert)


@admin.route('/content/') # type: ignore
def content_list(injector:inject.Injector):
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    params:dict = request.params # type: ignore
    page = int(params.get('page', '1')) # current page

    topicId = int(params.get('topicId', '0')) # search topic
    dirId = int(params.get('dirId', '0')) # search directory
    logger.debug(f'page: {page}, topicId: {topicId}, dirId: {dirId}')

    where = 'WHERE'
    if topicId > 0:
        where += f' topicId={topicId} AND '
    if dirId > 0:
        where += f' dirId={dirId} AND '
    where += ' 1=1 '

    totalRecords = 0
    pages:int = 0
    sql = f'SELECT count(*) AS total FROM gaiContentWithPrompt {where}'
    logger.debug(sql)
    cu = db.execute(sql )
    row = cu.fetchone()
    totalRecords = row['total']
    if totalRecords > 0:
        pages = totalPages(totalRecords, page_size)

    sql = f'SELECT * FROM gaiContentWithPrompt {where} ORDER BY id DESC LIMIT {page_size} OFFSET {(page-1)*page_size}'
    logger.debug(sql)
    cu = db.execute(sql)
    rows = cu.fetchall()
    cu.close()

    topics = _option(db, 'gaiTopic')
    paths = _option(db, 'gaiDirectory')

    tplfile = 'admin/content_list.htm'
    pageTitle = 'ContentPage'
    return template(tplfile, pageTitle=pageTitle, contents=rows, page=page, pages=pages, topics=topics, paths=paths, topicId=topicId, dirId=dirId)


@admin.route('/content/view/<id:int>', method=['HEAD', 'GET', 'POST', 'PUT', 'OPTIONS']) # type: ignore
def content_view(injector:inject.Injector, id:int):
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    params:dict = request.params # type: ignore
    id_ = id

    row = {'id':id_, 'promptId':'', 'promptText':'', 'promptFiles':'', 'text':'', 'files':''}
    tplfile = 'admin/content_view.htm'
    pageTitle = 'ViewPage'

    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    one = None
    if id_:
        sql = f'SELECT * FROM gaiContentWithPrompt WHERE id={id_}'
        cu = db.execute(sql)
        one = cu.fetchone()
        cu.close()

    if one:
        row['promptId'] = one['promptId']
        row['promptText'] = one['promptText']
        row['promptFiles'] = one['promptFiles']
        row['text'] = one['text']
        row['files'] = one['files']

    return template(tplfile, pageTitle=pageTitle, content =row)

@admin.route('/content/delete/<id:int>', method=['GET', 'POST']) # type: ignore
def content_delete(injector:inject.Injector, id:int):
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    params:dict = request.params # type: ignore
    id_ = id
    if id_ == 0:
        response.status = 400
        return error('invalid content id').stringify(ensure_ascii=False)

    deleted = False
    cursor = db.cursor()
    try:
        cursor.execute('BEGIN TRANSACTION')
        sql2 = f'DELETE FROM gaiPublishAttachment WHERE contentId={id_}'        
        sql1 = f'DELETE FROM gaiPublish WHERE contentId={id_}'
        sql3 = f'DELETE FROM gaiContent WHERE id={id_}'
        cursor.execute(sql1)
        cursor.execute(sql2)
        cursor.execute(sql3)
        cursor.execute('END TRANSACTION')
        db.commit()
        deleted = False
    except Exception as e:
        db.rollback()
    finally:
        cursor.close()

    data = {'contentId': id_, 'deleted': deleted}
    return success(data).stringify(ensure_ascii=False)


@admin.route('/content/publish/<id:int>', method=['HEAD', 'GET', 'POST', 'PUT', 'OPTIONS']) # type: ignore
def content_publish(injector:inject.Injector, id:int):
    # db = injector.get_instance(sqlite3.Connection) # type: ignore
    # logger = injector.get_instance(logging.Logger) # type: ignore

    params:dict = request.params # type: ignore
    id_ = id
    if id_ == 0:
        response.status = 400
        return error('invalid content id').stringify(ensure_ascii=False)

    reWrite = True if params.get('reWrite', '') else False
    publishId = publish(id_, reWrite)
    if not publishId:
        response.status = 500
        return error('publish failed').stringify(ensure_ascii=False)

    data = {'contentId': id_, 'publishId': publishId, 'reWrite': reWrite}
    # return 200 Success
    return success(data).stringify(ensure_ascii=False)