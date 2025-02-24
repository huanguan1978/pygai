
import logging, logging.config
import sqlite3
import inject


from setting import app_setting

logging.config.fileConfig('./config/logging.ini')
loggerName = app_setting.get('logging.name')
logger = logging.getLogger(loggerName)
logger.debug(f'loggerName: {loggerName}')

def inject_generativemodel_config(binder:inject.Binder):

  dbfile:str = app_setting.get('db.dbfile')
  logger.debug(f'dbfile: {dbfile}')
  db = sqlite3.connect(dbfile, autocommit=True)
  db.row_factory = sqlite3.Row

  binder.bind(sqlite3.Connection, db)
  binder.bind(logging.Logger, logger)

injector:inject.Injector = inject.configure(inject_generativemodel_config, once=True, bind_in_runtime=False)

"""
print(dir(injector))
gm_flash = injector.get_instance('gm_flash')
print(gm_flash)
"""