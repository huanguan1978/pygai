
-- 获得提示语逻辑，仅限enabled=True且lastContentId非空非零的记录
-- 1.每得到lastContentId一次时quota-1，quota为0时enabled=False
-- 2.每天清零lastContentId和lastContentTime

-- 发布逻辑，
-- 1找出gaiContent中prompt属性type为gentxt且prompt属性dirPath不为空的记录，
-- 2基于上述1, 若gaiPublish中不存在(gaiContent.id>gaiPublish.contentId)的记录，生成Markdown静态文件并将结果写入gaiPublish
-- 3基于上述2, 若prompt属性topicId不为空，则可以通过topicId来找配图

-- 
INSERT INTO gaiInstruction(id, name, text) VALUES(1, '角色代入-普通高中语文老师', '你是一名普通高级中学语文老师，你对学生的要求是：弘扬和培育民族精神，热爱祖国和中华文明，献身人类进步事业和精神品格，形成健康美好的情感和奋发向上的人生态度。作文亦是如此。');

-- interval id=6 name=every5minutes; config id=1 name=Low-Risk Generation Text, id=2 name=Safe Single Image Generation (No People); 
INSERT INTO gaiPrompt(intervalId, configId, topicId, instId, dirId, type, text) VALUES(6, 1, 1, 1, 1, 'gentxt', '命题作文:今朝有酒今朝醉,明日愁来明日忧.体裁不限,请写一篇字数不少于500字的作文.');
INSERT INTO gaiPrompt(intervalId, configId, topicId, instId, dirId, type, text, files) VALUES(6, 1, 1, 1, 1, 'gentxt', '看图作文:请看图片,图片中的人物在作表达什么,对我们有什么样的启示呢.体裁不限,请写一篇字数不少于500字的作文.', json_array('incontournables.jpg'));
INSERT INTO gaiPrompt(intervalId, configId, topicId, instId, dirId, type, text) VALUES(6, 2, 1, null, 1, 'genimg', '文本绘图:今朝有酒今朝醉,明日愁来明日忧.体裁不限,请绘一副插画.');

-- Update redundant name field via foreign key lookup by ID
UPDATE gaiPrompt AS p SET intervalId = t.id,intervalName = t.name FROM gaiInterval AS t WHERE p.intervalId = t.id AND p.intervalName IS NULL; 
UPDATE gaiPrompt AS p SET topicId = t.id,topicName = t.name FROM gaiTopic AS t WHERE p.topicId = t.id AND p.topicName IS NULL; 
UPDATE gaiPrompt AS p SET configName = c.name, configText = c.text FROM gaiConfig AS c WHERE p.configId = c.id AND p.configName IS NULL;
UPDATE gaiPrompt AS p SET instName = i.name, instText = i.text, instConfig = i.config FROM gaiInstruction AS i WHERE p.instId = i.id AND p.instName IS NULL;
UPDATE gaiPrompt AS p SET dirName = d.name, dirPath = d.path FROM gaiDirectory AS d WHERE p.dirId = d.id AND p.dirName IS NULL;

-- UPDATE gaiContent AS q SET topicId = p.topicId, topicName = p.topicName FROM gaiPrompt AS p WHERE p.id = q.promptId AND q.id = ?;