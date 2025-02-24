CREATE TABLE IF NOT EXISTS gaiTopic (
  id		     		INTEGER    		NOT NULL PRIMARY KEY AUTOINCREMENT,
  name				  VARCHAR(255)	NOT NULL UNIQUE				,
  memo				  TEXT			    NULL							,
  lastModified	DATETIME		NOT NULL DEFAULT (datetime('now', 'localtime'))
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai,Topic';


CREATE TABLE IF NOT EXISTS gaiInterval (
  id		     		INTEGER    		NOT NULL PRIMARY KEY AUTOINCREMENT,
  name				  VARCHAR(255)	NOT NULL UNIQUE				,
  expr          VARCHAR(255)	NOT NULL 				                 , -- COMMENT sqlite3 datetime interval expression
  memo				  TEXT			    NULL							,
  lastModified	DATETIME		  NOT NULL DEFAULT (datetime('now', 'localtime'))
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai,Interval';


CREATE TABLE IF NOT EXISTS gaiInstruction (
  id		     		INTEGER    		NOT NULL PRIMARY KEY AUTOINCREMENT,
  name				  VARCHAR(255)	NOT NULL UNIQUE					,
  text				  TEXT			    NULL							,
  config				TEXT			    NULL							,
  memo				  TEXT			    NULL							,
  lastModified	DATETIME		  NOT NULL DEFAULT (datetime('now', 'localtime'))
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai,Instruction';


CREATE TABLE IF NOT EXISTS gaiConfig (
  id		     		INTEGER    		NOT NULL PRIMARY KEY AUTOINCREMENT,
  type				  VARCHAR(255)	NOT NULL NOT NULL CHECK(type IN ('gentxt', 'genimg')) ,
  name				  VARCHAR(255)	NOT NULL UNIQUE				    ,
  text				  JSON			    NOT NULL						            , -- COMMENT JOSNTEXT
  lastModified	DATETIME		  NOT NULL DEFAULT (datetime('now', 'localtime'))
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai,Config';


CREATE TABLE IF NOT EXISTS gaiDirectory (
  id		     		  INTEGER    		NOT NULL PRIMARY KEY AUTOINCREMENT,
  name				    VARCHAR(255)	NOT NULL UNIQUE					,
  path			      VARCHAR(255)	NOT NULL						,           -- COMMENT Output localPath
  tmpl			      VARCHAR(255)	NOT NULL DEFAULT 'default'		, -- COMMENT Output template
  lastModified	  DATETIME		  NOT NULL DEFAULT (datetime('now', 'localtime'))
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai, Directory';


CREATE TABLE IF NOT EXISTS gaiPrompt (
  id		     		  INTEGER    		    NOT NULL PRIMARY KEY AUTOINCREMENT,
  enabled				  BOOLEAN	    	    NOT NULL DEFAULT TRUE			      , -- COMMENT available?
  isShowInContent BOOLEAN	    	    NOT NULL DEFAULT FALSE			    , -- COMMENT show in content?
  quota           INTEGER           NOT NULL DEFAULT 10             , -- COMMENT quota of this prompt
  schedTime       DATETIME          NULL                            , -- schedTime = startTime + intervalExpr, startTime = lastContentTime??lastModified
  intervalId			INTEGER	UNSIGNED  NULL    					        REFERENCES gaiInterval(id) ON DELETE CASCADE ON UPDATE CASCADE,
  intervalExpr		VARCHAR(255)		  NULL    	 	 					          , -- COMMENT Redundant, gaiInterval.expr  
  intervalName		VARCHAR(255)		  NULL	 	 					              , -- COMMENT Redundant, gaiInterval.name  

  topicId				  INTEGER	UNSIGNED  NULL					            REFERENCES gaiTopic(id) ON DELETE CASCADE ON UPDATE CASCADE,
  topicName			  VARCHAR(255)		  NULL	 	 					              , -- COMMENT Redundant, gaiTopic.name
  configId			  INTEGER	UNSIGNED  NULL            					REFERENCES gaiConfig(id) ON DELETE CASCADE ON UPDATE CASCADE,
  configName			VARCHAR(255)		  NULL	 	 					              , -- COMMENT Redundant, gaiConfig.name
  configText      JSON			        NULL                            , -- COMMENT Redundant, qaiConfig.text
  instId			    INTEGER	UNSIGNED  NULL            					REFERENCES gaiInstruction(id) ON DELETE CASCADE ON UPDATE CASCADE,
  instName			  VARCHAR(255)		  NULL	 	 					              , -- COMMENT Redundant, gaiInstruction.name
  instText        TEXT			        NULL                            , -- COMMENT Redundant, gaiInstruction.text
  instConfig      TEXT			        NULL                            , -- COMMENT Redundant, gaiInstruction.config
  dirId			      INTEGER	UNSIGNED  NULL            					REFERENCES gaiDirectory(id) ON DELETE CASCADE ON UPDATE CASCADE,
  dirName			    VARCHAR(255)		  NULL	 	 					              , -- COMMENT Redundant, gaiDirectory.name
  dirPath         TEXT			        NULL                            , -- COMMENT Redundant, gaiDirectory.path
  dirTmpl			    VARCHAR(255)		  NULL	 	 					              , -- COMMENT Redundant, gaiDirectory.tmpl

  type				    VARCHAR(255)	    NOT NULL CHECK(type IN ('gentxt', 'genimg')),
  text				    TEXT			        NOT NULL						            , -- COMMENT Prompt Text
  files				    JSON			        NULL							              , -- COMMENT Prompt Files
  memo            TEXT			        NULL							              , -- COMMENT user memo

  lastContentId		INTEGER	UNSIGNED  NULL							              , -- COMMENT prompt gen last content id
  lastContentTime	DATETIME			    NULL                            , -- COMMENT prompt gen last content time
  lastModified    DATETIME			    NOT NULL DEFAULT (datetime('now', 'localtime'))
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai, prompt';

/*
DROP TRIGGER IF EXISTS gaiPrompt_quota_trigger;
CREATE TRIGGER gaiPrompt_quota_trigger
AFTER UPDATE OF lastContentId ON gaiPrompt
FOR EACH ROW
WHEN NEW.lastContentId IS NOT NULL AND NEW.lastContentId != 0 AND NEW.lastContentId != OLD.lastContentId
BEGIN
    UPDATE gaiPrompt SET quota = quota - 1, enabled = quota>0  WHERE rowid = NEW.rowid;
    UPDATE gaiPrompt SET schedTime = DATETIME('now', intervalExpr) WHERE rowid = NEW.rowid AND intervalExpr IS NOT NULL;    
END;
*/

CREATE TABLE IF NOT EXISTS gaiContent (
  id		     	    INTEGER    			  NOT NULL PRIMARY KEY AUTOINCREMENT,
  promptId		    INTEGER	UNSIGNED  NULL					REFERENCES gaiPrompt(id) ON DELETE CASCADE ON UPDATE CASCADE,

  histCronId		  VARCHAR(255)		  NULL						, -- COMMENT HttpPostData, CronID
  histId			    VARCHAR(255)		  NULL						, -- COMMENT HttpPostData, HistId
  histPromptId	  VARCHAR(255)		  NULL						, -- COMMENT HttpPostData, PromptId(isdigit is gaiPromptId.id)

  text			      TEXT				      NOT NULL				, -- COMMENT gen content
  files			      JSON				      NULL						, -- COMMENT gen files

  publishId       INTEGER	UNSIGNED  NULL					  , -- COMMENT last gaiPublish.id
  publishTime		  DATETIME			    NULL            , -- COMMENT last gaiPublish.created
  publishFileName	VARCHAR(255)		  NULL						, -- COMMENT last gaiPublish.fileName

  created			    DATETIME			    NOT NULL DEFAULT (datetime('now', 'localtime'))
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai,content';

DROP INDEX IF EXISTS idx_gaiContent_histCronId; CREATE INDEX idx_gaiContent_histCronId ON gaiContent(histCronId);
DROP INDEX IF EXISTS idx_gaiContent_histId; CREATE INDEX idx_gaiContent_histId ON gaiContent(histId);
DROP INDEX IF EXISTS idx_gaiContent_histPromptId; CREATE INDEX idx_gaiContent_histPromptId ON gaiContent(histPromptId);

DROP VIEW IF EXISTS gaiContentWithPrompt;
CREATE VIEW gaiContentWithPrompt AS
  SELECT 
    gc.*,
    gp.type AS genType,
    gp.text as promptText,
    gp.files as promptFiles,
    gp.isShowInContent,
    gp.topicId,
    gp.topicName,
    gp.dirId,
    gp.dirName,
    gp.dirPath,
    gp.dirTmpl
  FROM 
    gaiContent gc
  LEFT JOIN gaiPrompt gp ON gc.promptId = gp.id;


CREATE TABLE IF NOT EXISTS gaiPublish (
  id		     	INTEGER    			  NOT NULL PRIMARY KEY AUTOINCREMENT,
  contentId		INTEGER	UNSIGNED  NOT	NULL					REFERENCES gaiContent(id) ON DELETE CASCADE ON UPDATE CASCADE,
  refPath		  TEXT				      NOT NULL						  , -- COMMENT output path, Redundant, gaiContentWithPrompt.dirPath as gcp where gcp.id = contentId
  refTopicId	INTEGER	UNSIGNED  NULL					        , -- COMMENT ref topic, Redundant, gaiContentWithPrompt.topicId as gcp where gcp.id = contentId
  filename		TEXT				      NOT NULL						  , -- COMMENT output local filename

  created			DATETIME			    NOT NULL DEFAULT (datetime('now', 'localtime'))
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai, publish';


CREATE TABLE IF NOT EXISTS gaiPublishAttachment (
  id		     	INTEGER    			  NOT NULL          REFERENCES gaiPublish(id) ON DELETE CASCADE ON UPDATE CASCADE,
  contentId		INTEGER	UNSIGNED  NOT	NULL					REFERENCES gaiContent(id) ON DELETE CASCADE ON UPDATE CASCADE,
  files		    JSON				      NOT NULL						  , -- COMMENT Redundant, gaiContent.files

  PRIMARY KEY(id, contentId)
);  -- ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='gai, publishAttachment';


INSERT INTO gaiConfig(id, type, name, text) VALUES(1, 'gentxt', 'Low-Risk Generation Text', json('{"modelId":"geminiflash158B","modelName":"gemini-1.5-flash-8b","safeySetting":{"harassment":"low","hateSpeech":"low","sexuallyExplicit":"low","dangerousContent":"low","enabled":"true"},"generationConfig":{"maxOutputTokens":4096,"stopSequences":[],"temperature":1.0,"topP":0.95,"enabled":"true"}}'));
INSERT INTO gaiConfig(id, type, name, text) VALUES(2, 'genimg', 'Safe Single Image Generation (No People)', json('{"modelId":"image3fast","modelName":"imagen-3.0-fast-generate-001","numberOfImages":"1","aspectRatio":"1:1","language":"","safetyFilterLevel":"block_some","personGeneration":"dont_allow","negativePrompt":"", "enabled":"true"}'));

INSERT INTO gaiInterval(id, name, expr, memo) VALUES
  (1, 'hourly', '+1 hours', '0 * * * *'), (2, 'daily', '+1 days', '0 0 * * *'), (3, 'weekly', '+1 week', '0 0 * * 0'), (4, 'monthly', '+1 month', '0 0 1 * *'), (5, 'yearly', '+1 year', '0 0 1 1 *'), 
  (6, 'every5minutes', '+5 minutes', '*/5 * * * *'), (7, 'every10minutes', '+10 minutes', '*/10 * * * *'), (8, 'every15minutes', '+15 minutes', '*/15 * * * *'), (9, 'every30minutes', '+30 minutes', '*/30 * * * *'), 
  (10, 'every2hours', '+2 hours', '0 */2 * * *'), (11, 'every4hours', '+4 hours', '0 */4 * * *')
  ;

INSERT INTO gaiTopic(id, name) VALUES(1, 'Wordsmith');

--  mkdir -p ~/Documents/sites; mkdocs new ~/Documents/sites/MyWebSite
INSERT INTO gaiDirectory(id, name, path) VALUES(1, 'MyWebSite', '~/Documents/sites/MyWebSite/docs/');