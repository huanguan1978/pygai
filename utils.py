
from io import StringIO
import os, re, textwrap
from datetime import datetime
from mimetypes import guess_type

_yml_mkdocs = \
'''
site_name: {site_name}
theme: material

extra_css:
  - stylesheets/extra.css
extra_javascript:
  - javascripts/extra.js

plugins:
  - pub-debugger
  - pub-blog
  - pub-meta
'''

_tmp_mkdoc = textwrap.dedent('''\
---
title: {title}
slug: {slug}
description: {description}
date: {date}
update: {update}
publish: {publish}
categories:
  - {topicName}
---
{prompt}
{content}
''')

_readme_mkdoc = textwrap.dedent('''\
---
publish: true
---
''')

_tmp_extra_css = textwrap.dedent('''\
article img {
  max-width: 200px;
  max-height: 200px;
  object-fit: contain;
}
''')

_tmp_extra_js = textwrap.dedent('''\
console.log("extra.js");
''')

_metadata = {
    'title': '',
    'slug': '',
    'description': '',
    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'update': '',
    'publish': 'true',
    'topicName': '',
}


def init_mkdocs(path:str):
    ''' init project, path like ~/Documents/sites/MyWebSite/docs/ '''

    dirs = [
        'blog', 'stylesheets', 'javascripts',  
        'img', '.pub_blog_temp', 'uploads',
        'img/blog', 
#        '.pub_blog_temp/archive', '.pub_blog_temp/categories', '.pub_blog_temp/tags',
    ]

    if not path.endswith(os.path.sep):
        path += os.path.sep   
    if path.endswith(f'{os.path.sep}docs{os.path.sep}'):
        root = os.path.dirname(os.path.dirname(path))
        name = os.path.basename(root)

        docPath  = path
        for d in dirs:
            dirPath = os.path.join(docPath, d)
            if not os.path.exists(dirPath):
                os.makedirs(dirPath, exist_ok=True)

        conf = os.path.join(root, 'mkdocs.yml')
        if not os.path.exists(conf):
            with open(conf, 'w') as f:
                f.write(_yml_mkdocs.format(site_name=name))

        index = os.path.join(docPath, 'README.md')
        if not os.path.exists(index):
            with open(index, 'w') as f:
                f.write(_readme_mkdoc)

        extra_css = os.path.join(docPath, 'stylesheets', 'extra.css')
        if not os.path.exists(extra_css):
            with open(extra_css, 'w') as f:
                f.write(_tmp_extra_css)
        extra_js = os.path.join(docPath, 'javascripts', 'extra.js')
        if not os.path.exists(extra_js):
            with open(extra_js, 'w') as f:
                f.write(_tmp_extra_js)

def blog_mkdocs(path:str, text:str, data:dict, reWrite:bool=False, writetofile:str='')->str:
    ''' create a blog entry, return the path of the entry '''

    entry = ''
    if not path.endswith(os.path.sep):
        path += os.path.sep
    path = os.path.expandvars(os.path.expanduser(path))

    if path.endswith(f'{os.path.sep}docs{os.path.sep}') and os.path.exists(path):        
        docBlogPath = os.path.join(path, 'blog')
        imgBlogPath = os.path.join(docBlogPath, 'img')

        topicId = data['topicId'] if 'topicId' in data else '0'
        topicName = data['topicName'] if 'topicName' in data else ''        
        # topicPath = os.path.join(docBlogPath, str(topicId))
        # if not os.path.exists(topicPath):
        #         os.makedirs(topicPath, exist_ok=True)
        promptId = data['promptId'] if 'promptId' in data else '0'
        contentId = data['contentId'] if 'contentId' in data else '0'
        now = datetime.now()
        filename = f'{topicId}-{promptId}-{contentId}-{now.strftime('%Y%m%d%H%M%S')}.md'
        if writetofile:
            filename = writetofile[5:] if writetofile.startswith('blog/') else writetofile
        # entry = os.path.join(topicPath, filename)
        entry = os.path.join(docBlogPath, filename)
        # print(f'reWrite: {reWrite}, entry: {entry}')
        if not reWrite and os.path.exists(entry):
            return entry
    
        title, introduction = extract_title_and_introduction(text)
        metadata = _metadata.copy()
        metadata['title'] = title
        metadata['slug'] = filename.replace('.md', '')
        metadata['description'] = introduction
        metadata['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        metadata['topicName'] = topicName
        if reWrite:
            metadata['update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if writetofile:
                metadata['date'] = extract_time_from_filename(writetofile)

        isShowInContent = False
        if 'isShowInContent' in data:
            isShowInContent = True if data['isShowInContent'] else False
        promptText = data.get('promptText', '').strip()
        promptFiles = data.get('promptFiles', [])
        prompt = ''
        if isShowInContent:
            with StringIO() as buffer:
                if promptText:
                    buffer.write(promptText)
                    buffer.write('\n\n')
                if promptFiles:
                    for filename in promptFiles:
                        filetext = f'[{filename}](../uploads/{filename})'
                        mime_type, _ = guess_type(filename)
                        if mime_type and mime_type.startswith('image/'):
                            filetext = f'![{filename}](../uploads/{filename})'
                        if mime_type and mime_type.startswith('audio/'):
                            filetext = f'<audio><source src="../uploads/{filename}" type="{mime_type}"></audio>'
                        if mime_type and mime_type.startswith('video/'):
                            filetext = f'<video><source src="../uploads/{filename}" type="{mime_type}"></video>'
                        buffer.write(filetext)
                        buffer.write('\n\n')            
                prompt = buffer.getvalue()

        text = insert_paragraph_after_fourth(text)
        with open(entry, 'w') as f:
            f.write(_tmp_mkdoc.format(**metadata, prompt=prompt, content=text))

    return entry

def extract_title_and_introduction(text: str) -> list:
    ''' Extract the title and the first paragraph from the given text '''
    paragraphs = text.split('\n\n')
    title = ''
    introduction = ''
    for paragraph in paragraphs:
        if paragraph.strip():
            if not title:
                title = paragraph.strip()
            elif not introduction:
                introduction = paragraph.strip()
                break
    return [title, introduction]

def insert_paragraph_after_fourth(text: str, paragraph: str='<!-- more -->') -> str:
    ''' Insert a paragraph after the fourth paragraph in the given text '''
    paragraphs = text.split('\n\n')
    if len(paragraphs) > 4:
        paragraphs.insert(4, paragraph)
    return '\n\n'.join(paragraphs)

def extract_time_from_filename(filename:str)->str:
    ''' Extract the time from the filename; 
    e.g. blog/1-1-7-20250204170225.md, return 2025-02-04 17:02:25 '''
    now = datetime.now()
    match = re.search(r'\d{14}', filename)
    if match:
        time_str = match.group()
        now = datetime.strptime(time_str, '%Y%m%d%H%M%S')
    
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    return time_str