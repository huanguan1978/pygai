#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, logging, sqlite3, json, shutil

from injector import injector
from setting import uploads_path
from ext import extMethod
from utils import blog_mkdocs

def publish(contentId:int, reWrite:bool=False) -> None|int:
    extPublishHandler = extMethod('gai/publish', 'publishHandler')
    return extPublishHandler(contentId, reWrite) if extPublishHandler else publishHandler(contentId, reWrite)

def publishHandler(contentId:int, reWrite:bool=False) -> None|int:
    db = injector.get_instance(sqlite3.Connection) # type: ignore
    logger = injector.get_instance(logging.Logger) # type: ignore

    id_ = contentId
    sql = f'SELECT * FROM gaiContentWithPrompt WHERE id={id_}'
    cu = db.execute(sql)
    row = cu.fetchone()
    cu.close()

    if not row:
        return None

    publishId = 0
    writetofile = row['publishFileName']
    logger.debug(f'publishHandler, contentId: {contentId} reWrite: {reWrite}, publishFileName: {writetofile}')
    if not reWrite and writetofile:
        return row['publishId']
    if reWrite and writetofile:
        localfile = os.path.join(row['dirPath'], writetofile)
        localfile = os.path.expandvars(os.path.expanduser(localfile))
        publishId = int(row['publishId'])
        if os.path.exists(localfile):
            # os.remove(localfile)
            logger.debug(f'publishHandler, publishId: {publishId} reWrite file: {localfile}')
        cursor = db.cursor()
        try:
            cursor.execute('BEGIN TRANSACTION')
            # sql1 = f'DELETE FROM gaiPublish WHERE id={publishId}'
            sql2 = f'DELETE FROM gaiPublishAttachment WHERE id={publishId}'
            # sql3 = f'UPDATE gaiContent SET publishTime=NULL, publishId=NULL, publishFileName=NULL WHERE id={id_}'
            sql3 = f"UPDATE gaiContent SET publishTime=datetime('now', 'localtime') WHERE id={id_}"            
            # cursor.execute(sql1)
            cursor.execute(sql2)
            cursor.execute(sql3)
            cursor.execute('END TRANSACTION')
            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            cursor.close()

    text = row['text']
    dirPath = row['dirPath']
    data = {'topicId': row['topicId'], 'topicName': row['topicName'], 'promptId': row['promptId'], 'contentId': row['id'], 
            'promptText': row['promptText'], 'promptFiles': row['promptFiles'], 
            'genType': row['genType'], 'isShowInContent': row['isShowInContent'],
            }

    logger.debug(f'publishHandler, contentId: {contentId}, dirPath: {dirPath}')    
    if not dirPath:
        return None
    
    promptFiles = json.loads(row['promptFiles'])    
    if row['isShowInContent'] and promptFiles:
        data['promptFiles'] = promptFiles
        for filename in promptFiles:
            srcfile = os.path.expandvars(os.path.expanduser(os.path.join(uploads_path, filename)))
            dstfile = os.path.expandvars(os.path.expanduser(os.path.join(dirPath, 'uploads', filename)))
            logger.debug(f'publishHandler, contentId: {contentId}, copyfile: {srcfile} -> {dstfile}')   
            if os.path.exists(srcfile):
                shutil.copyfile(srcfile, dstfile)


    entry = blog_mkdocs(dirPath, text, data, reWrite, writetofile)
    if publishId:
        return publishId

    if entry:        
        logger.debug(f'publishHandler, contentId: {contentId}, entry: {entry}')
        pathfile = entry[entry.find('blog/'):]
        logger.debug(f'publishHandler, contentId: {contentId}, pathfile: {pathfile}')
        cursor = db.cursor()
        try:
            cursor.execute('BEGIN TRANSACTION')
            sql = f'INSERT INTO gaiPublish(contentId, refPath, refTopicId, filename) VALUES(?,?,?,?)'
            cursor.execute(sql, [id_, dirPath, data['topicId'], pathfile])
            publishId = cursor.lastrowid
            sql = f"UPDATE gaiContent SET publishTime=datetime('now', 'localtime'), publishId=?, publishFileName=? WHERE id={id_}"
            cursor.execute(sql, [publishId, pathfile])
            cursor.execute('END TRANSACTION')
            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            cursor.close()


    return publishId if publishId else None