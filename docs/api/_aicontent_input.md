#### 生成内容后上传

- Url: 
    - POST 
    - {{host}}/aicontent/input/
- Header: 
    - Authorization: Bearer {{token}}
    - Content-Type: application/json

##### 请求数据，示例
```json
{
    "status": "success",
    "data": {
        "id": "",
        "text": "窗外的雨丝斜斜地飘着，敲打着窗棂，发出淅淅沥沥的声响。我望着窗外，思绪也随着雨丝飘忽不定。......",
        "cronId": "_CRON_每日作文之今朝有酒今朝醉",
        "histId": "L-GTXT-1731317840133187",
        "promptId": "2",
        "files": [
            "http://localhost:8080/genimgs/139473250698292130.png"
        ]
    }
}
```

##### 响应数据,成功数据,文本提示语

- Status: 200
- Body:
    
```json
{
    "status": "success",
    "data": {
        "id": 3,
        "text": ""
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


#### 响应数据,失败数据,JSON校验失败 状态码非200.

- Status: 409
- Body:
    
```json

```

#### 响应数据,失败数据,内部错误 状态码非200.

- Status: 500
- Body:
    
```json

```