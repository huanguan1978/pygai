#### 获取一个提示语

- Url: 
    - GET 
    - {{host}}/aiprompt/output/
- Header: 
    - Authorization: Bearer {{token}}

##### 响应数据,成功数据,文本提示语（系统指令：无）

- Status: 200
- Body:
    
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "type": "gentxt",
    "config": {
      "modelId": "geminiflash15",
      "modelName": "gemini-1.5-flash",
      "safeySetting": {
        "harassment": "low",
        "hateSpeech": "low",
        "sexuallyExplicit": "low",
        "dangerousContent": "low",
        "enabled": "true"
      },
      "generationConfig": {
        "maxOutputTokens": 4096,
        "stopSequences": [],
        "temperature": 1.0,
        "topP": 0.95,
        "enabled": "true"
      }
    },
    "instId": 1,
    "instName": "角色代入-普通高中语文老师",
    "instText": "你是一名普通高级中学语文老师，你对学生的要求是：弘扬和培育民族精神，热爱祖国和中华文明，献身人类进步事业和精神品格，形成健康美好的情感和奋发向上的人生态度。作文亦是如此。",
    "text": "命题作文:今朝有酒今朝醉,明日愁来明日忧.体裁不限,请写一篇字数不少于500字的作文.",
    "files": []
  }
}

```

##### 响应数据,成功数据,文本提示语（系统指令：有）

- Status: 200
- Body:
    
```json
{
  "status": "success",
  "data": {
    "id": 3,
    "type": "genimg",
    "config": {
      "modelId": "image3fast",
      "modelName": "imagen-3.0-fast-generate-001",
      "numberOfImages": "1",
      "aspectRatio": "1:1",
      "language": "zh",
      "safetyFilterLevel": "block_some",
      "personGeneration": "allow_adult",
      "negativePrompt": "",
      "enabled": "true"
    },
    "instId": 0,
    "instName": "",
    "instText": "",
    "text": "文本绘图:今朝有酒今朝醉,明日愁来明日忧.体裁不限,请绘一副插画.",
    "files": []
  }
}
```

##### 响应数据,成功数据, 无内容无需客户端处理

- Status: 200
- Body:
    
```json
{
  "status": "success",
  "data": {
  }
}
```

#### 响应数据,失败数据, 状态码非200.

- Status: 500
- Body:
    
```json

```