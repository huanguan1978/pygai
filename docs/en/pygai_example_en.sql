-- 
INSERT INTO gaiInstruction(id, name, text) VALUES(1, 'Role Play - High School Teacher', 'As a high school language and literature teacher, my expectations for students are: My core mission as your language and literature teacher is to guide you in embracing and nurturing **your national spirit**. This means cultivating a deep love for **your homeland** and its rich **traditional culture**. Beyond that, I expect you to develop the noble character traits of dedicating yourselves to **the advancement of humanity**, fostering healthy and beautiful emotions, and adopting a proactive, aspiring outlook on life. This ethos, of course, extends to all your writing assignments.');

-- interval id=6 name=every5minutes; config id=1 name=Low-Risk Generation Text, id=2 name=Safe Single Image Generation (No People); 
INSERT INTO gaiPrompt(intervalId, configId, topicId, instId, dirId, type, text) VALUES(6, 1, 1, 1, 1, 'gentxt', "Essay Prompt: Live for Today, Let Tomorrow's Troubles Wait. Write an essay of any style (minimum 500 words) on this theme.");
INSERT INTO gaiPrompt(intervalId, configId, topicId, instId, dirId, type, text, files) VALUES(6, 1, 1, 1, 1, 'gentxt', 'Picture-Based Essay: Examine the image and describe what the person(s) in it are expressing. What insights or lessons can we draw from this? Write an essay of any style (minimum 500 words)', json_array('incontournables.jpg'));
INSERT INTO gaiPrompt(intervalId, configId, topicId, instId, dirId, type, text) VALUES(6, 2, 1, null, 1, 'genimg', 'Text-Inspired Illustration: "Live for Today, Let Tomorrow Troubles Wait." Create an illustration of any style based on this proverb.');

-- Update redundant name field via foreign key lookup by ID
UPDATE gaiPrompt AS p SET intervalId = t.id,intervalName = t.name FROM gaiInterval AS t WHERE p.intervalId = t.id AND p.intervalName IS NULL; 
UPDATE gaiPrompt AS p SET topicId = t.id,topicName = t.name FROM gaiTopic AS t WHERE p.topicId = t.id AND p.topicName IS NULL; 
UPDATE gaiPrompt AS p SET configName = c.name, configText = c.text FROM gaiConfig AS c WHERE p.configId = c.id AND p.configName IS NULL;
UPDATE gaiPrompt AS p SET instName = i.name, instText = i.text, instConfig = i.config FROM gaiInstruction AS i WHERE p.instId = i.id AND p.instName IS NULL;
UPDATE gaiPrompt AS p SET dirName = d.name, dirPath = d.path FROM gaiDirectory AS d WHERE p.dirId = d.id AND p.dirName IS NULL;

-- UPDATE gaiContent AS q SET topicId = p.topicId, topicName = p.topicName FROM gaiPrompt AS p WHERE p.id = q.promptId AND q.id = ?;