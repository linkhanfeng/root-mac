# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import platform
import datetime
import os
import subprocess
import urllib
import yaml
import re

# index
# 复制文件名称
# 复制文件名称带后缀
# 复制文件绝对路径
# 添加markdown文件的元信息和 TOC
# 在浏览器中打开文件
# 删除sublime项目
# 添加sublime项目
# reveal_in_side_bar加focus_side_bar如果项目不存在添加项目到siderbar
# 打开最近常用的文件和目录
# 批量创建文件或目录from选择的单行或多点编辑行
# 批量获取目录树
# 创建序号from选择的单行或多点编辑行
# 自动创建书籍目录
# 自动创建书籍目录Plus
# 1. 事件监听器
# 1.1 markdown文件链接路径自动补全 + markdown文件保存前自动更新修改时间
# 1.2 html-css-js-json保存时格式化代码
# 标签页激活时自动reveal_in_side_bar
# 粘贴时格式化文本并paste_and_indent
# 鼠标经过链接地址选择打开链接的方式
# 获取时间等信息
#
# 获取当前文件路径信息
def fileInfo(self=None, num=None, isTextCommand=None, isFilenameStr=None):
    if isFilenameStr:
        file_path = isFilenameStr
    elif isTextCommand:
        file_path = self.view.file_name()
    else:
        file_path = self.window.active_view().file_name()
    file_name_with_ext = file_path.split('/')[-1];
    file_name = file_name_with_ext[0:file_name_with_ext.rfind('.')]
    file_name_ext = file_name_with_ext.replace(file_name + '.', '')
    file_parent_path = file_path.strip(file_name_with_ext)
    fileinfos = [file_path, file_name_with_ext, file_name, file_name_ext, file_parent_path]
    if num != None:
        sublime.set_clipboard(fileinfos[num])
    return fileinfos

# /user/a.txt
def fileInfoObj(filepath):
    path_name, ext_dot = os.path.splitext(filepath)
    path, name = path_name.rsplit('/', 1)
    ext = ext_dot.replace('.', '', 1)
    return {
        'path': path,               # /user
        'name': name,               # a
        'ext_dot': ext_dot,         # .txt
        'ext': ext,                 # txt
        'name_ext': name + ext_dot, # a.txt
    }

# 复制文件名称
class CopyCurFileNameCommand(sublime_plugin.WindowCommand):
  def run(self):
    fileInfo(self,2)

# 复制文件名称带后缀
class CopyCurFileNameWithExtensionCommand(sublime_plugin.WindowCommand):
  def run(self):
    fileInfo(self,1)

# 复制文件绝对路径
class CopyCurFilePathCommand(sublime_plugin.WindowCommand):
  def run(self):
    fileInfo(self,0)

# 添加markdown文件的元信息和 TOC
class InsertMarkdownMetaCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # 格式化时间
        t = datetime.datetime.now()
        curIsoTime = t.isoformat(' ').split('.', maxsplit=1)[0]
        # 检测是否已经存在信息, 不存在插入信息, 存在更新时间和检测标题是否修改
        isMetaStr = self.view.substr(sublime.Region(0, 3))
        # print('InsertMarkdownMetaCommand::', isMetaStr)
        if isMetaStr == '---':
            # 从文件提取 yaml 并解析为对象
            endYamlRg = self.view.find('---', 3, sublime.LITERAL)
            yamlStr = self.view.substr(sublime.Region(3, endYamlRg.a))
            # print(endYamlRg, yamlStr)
            yamlObj = yaml.load(yamlStr)
            # print(yamlObj)
            # 更新时间
            yamlObj['updated'] = curIsoTime
            # 更新标题
            titleRg = self.view.find('# ', 0, sublime.LITERAL)
            titleLineStr = self.view.substr(self.view.line(titleRg)).replace('# ', '')
            # print(23333,titleLineStr)
            yamlObj['title'] = titleLineStr
            # yaml_d_str = yaml.dump(yamlObj)
            yaml_d_str = yaml.dump(yamlObj, allow_unicode=True, explicit_start=True, explicit_end=True)
            self.view.replace(edit, sublime.Region(0, endYamlRg.a), yaml_d_str)
            # 更新 toc
            self.view.run_command('markdowntoc_update')
        else:
            # 获取 tag, 根据目录结构在插入时
            tagsList = []
            fileInfo = fileInfoObj(self.view.file_name())
            filename = fileInfo['name']
            filePathList = fileInfo['path'].strip('/').split('/')
            noteIndex = filePathList.index('note')
            if noteIndex > -1:
                if 'mysql-doc' in filePathList:
                    # mysql_doc_Index 仅仅是mysql文档的设置不让章节目录添加到标签 (可以删除)
                    mysql_doc_Index = filePathList.index('mysql-doc')
                    for value in filePathList:
                        if filePathList.index(value) > noteIndex and filePathList.index(value) <= mysql_doc_Index:
                            tagsList.append(value)
                else:
                    for value in filePathList:
                        if filePathList.index(value) > noteIndex:
                            tagsList.append(value)

            metaObj = {
                'title': filename,
                'date': curIsoTime,
                'updated': curIsoTime,
                'tags': tagsList,
            }
            yamlStr = yaml.dump(metaObj, allow_unicode=True, explicit_start=True, explicit_end=True)
            # yamlStr = yaml.dump(metaObj).encode('utf-8').decode('unicode_escape')
            # print(yamlStr)
            self.view.insert(edit, 0, yamlStr + '---\n')
            self.view.run_command('markdowntoc_insert')
            # 添加回到主目录链接 如果有主目录的话
            def isFileExit(startpath, filename):
                parents_arr = startpath.split('/')
                parents_arr_copy = parents_arr[:]
                level = 0
                for path in parents_arr:
                    parents_arr_copy.pop()
                    indexpath = "/".join(parents_arr_copy) + '/' + filename
                    if os.path.exists(indexpath):
                        if level == 0:
                            return './' + filename
                        else:
                            return '../' * level + filename
                    level = level + 1

            indexpath = isFileExit(fileInfo['path'] + '/', 'index.md')
            if indexpath:
                self.view.insert(edit, self.view.size(), '[回到目录]({})\n\n'.format(indexpath))

# 在浏览器中打开文件
class OpenFileInBrowerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):

        path = kwargs.get('url', None)
        if not path:
            path = self.view.file_name()
        pathUrl = 'file:///' + urllib.parse.quote(path)
        sublime.run_command('open_url', {'url': pathUrl})

# 删除sublime项目
class ProjectRemoveCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.open_folders = self.window.folders()
        if len(self.open_folders) == 0:
            sublime.status_message('No open folders')
            return
        def on_done(idx):
            if idx < 0:
                return
            foldername = self.open_folders[idx]
            self.window.run_command('remove_folder', {
                'dirs': [foldername]
            })
            sublime.status_message('Removed folder {}'.format(foldername))
            # XXX Add a setting to show again for removing multiple folders.
            # self.open_folders = self.window.folders()
            # self.window.show_quick_panel(self.open_folders, on_done)
        self.window.show_quick_panel(self.open_folders, on_done)

# 添加sublime项目
# class PluginTestCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         self.window.run_command('project_add', { 'file_path': "/Users/hf/Music" })
class ProjectAddCommand(sublime_plugin.WindowCommand):

    def run(self, **kwargs):
        # filename = '/Users/hf/Music'

        filename_path = kwargs.get('file_path', None)

        if filename_path != None:
            filename = filename_path

            # 检测路径是否已经在侧边栏中存在
            pathIsInProject = cur_path_is_in_project(self, filename_path)
            if pathIsInProject == 1:
                return

            if os.path.isdir(filename):
                config = {'follow_symlinks': True, 'path': filename}
                data = self.window.project_data()
                if not data:
                    data = {'folders': [config]}
                    self.window.set_project_data(data)
                else:
                    data['folders'].append(config)
                    self.window.set_project_data(data)
                sublime.status_message('Added folder {}'.format(filename))
            else:
                self.window.open_file(filename)
        else:
            self.new_window = kwargs.get('new_window', None)
            # XXX Add a user setting to chose whether to initialize the path to
            # that of the current file, or the latest path chosen.
            variables = self.window.extract_variables()
            file_path_current = variables.get('file_path', '')
            file_path_last = self.get_last_path()
            initial_path = file_path_last or file_path_current
            self.current_files = os.listdir(initial_path) \
                if initial_path and os.path.isdir(initial_path) else []
            self.window.show_input_panel(
                'Select folder', initial_path, self.on_done, self.on_change, None)

    def on_change(self, filename):
        filename = os.path.expanduser(filename)
        if filename.endswith('/'):
            if os.path.exists(filename):
                self.current_directory = filename
                self.current_files = sort_file_list(
                    os.listdir(self.current_directory))
                sublime.status_message('|'.join(self.current_files))
            else:
                sublime.status_message('No such folder {}'.format(filename))
        else:
            prefix = os.path.basename(filename)
            self.matches = [f for f in self.current_files if f.startswith(prefix)]
            msg  = '|'.join(self.matches) if self.matches else 'No matches'
            sublime.status_message(msg)

    def on_done(self, filename):
        filename = os.path.expanduser(filename)
        if not os.path.exists(filename):
            if len(self.matches) == 1:
                filename = os.path.join(self.current_directory, self.matches[0])
            else:
                sublime.status_message('No such file {}'.format(filename))
        if os.path.exists(filename):
            self.last_path = filename
            if self.new_window:
                self.on_done_new(filename)
            else:
                self.on_done_add(filename)

    def on_done_add(self, filename):
        if os.path.isdir(filename):
            config = {'follow_symlinks': True, 'path': filename}
            data = self.window.project_data()
            if not data:
                data = {'folders': [config]}
                self.window.set_project_data(data)
            else:
                data['folders'].append(config)
                self.window.set_project_data(data)
            sublime.status_message('Added folder {}'.format(filename))
        else:
            self.window.open_file(filename)

    def on_done_new(self, filename):
        if filename.endswith('.sublime-project'):
            subprocess.Popen(['subl', '--project', filename])
        else:
            subprocess.Popen(['subl', '-n', filename])

    def get_last_path(self):
        if hasattr(self, 'last_path'):
            return self.last_path
        self.last_path = None
        return self.last_path

def sort_file_list(filenames):
    hidden = [f for f in filenames if f.startswith('.')]
    regular = [f for f in filenames if not f.startswith('.')]
    return sorted(regular) + sorted(hidden)

def cur_path_is_in_project(self, cur_path):
    # 检测路径是否在 sidBar 中已经存在
    projectFolders = self.window.folders()
    for i, v in enumerate(projectFolders):
        # print(i, cur_path.find(v))
        if cur_path.find(v) > -1:
            return 1
            break
    return 0

# reveal_in_side_bar加focus_side_bar如果项目不存在添加项目到siderbar
def reveal_and_focus_in_sidebar(self):
    self.window.run_command("reveal_in_side_bar")
    self.window.run_command("focus_side_bar")

# 刷新侧边栏
def refresh_folders(self):
    data = self.window.project_data()
    set_project_json(self, {})
    set_project_json(self, data)

def set_project_json(self, data):
    return self.window.set_project_data(data)

class RevealFocusSideBarCommand(sublime_plugin.WindowCommand):
    def run(self):
        # 如果 sidebar 中不存在项目,则打开项目
        file_parent_path = fileInfo(self)[4]
        self.window.run_command('project_add', { 'file_path': file_parent_path })

        if not self.window.is_sidebar_visible():
            # refresh_folders(self)
            self.window.set_sidebar_visible(True)
            # set_project_data is asynchronous so we need settimeout for subsequent commands
            sublime.set_timeout_async(lambda: reveal_and_focus_in_sidebar(self), 250)
        else:
            sublime.set_timeout_async(lambda: reveal_and_focus_in_sidebar(self), 250)

# 打开最近常用的文件和目录
class OpenRecentCommand(sublime_plugin.WindowCommand):
    def run(self):
        items = [
            '/Users/hf/work/',
            '/Users/hf/work/github/note/',
            '/Users/hf/work/env/laradock/',
            '/Users/hf/Library/Application Support/Sublime Text 3/Packages/User',
            '/Users/hf/Library/Application Support/Sublime Text 3/Packages/User/file_action.py',
        ]
        def on_done(idx):
            # print(items[idx])
            absolute_path = items[idx]
            if os.path.isdir(absolute_path):
                self.window.run_command('project_add', { 'file_path': absolute_path })
            else:
                self.window.open_file(absolute_path)

        self.window.show_quick_panel(items, on_done)

# 批量创建文件或目录from选择的单行或多点编辑行
# 如果创建目录需要在 行的末尾 添加 "/" 符号
# 如果想在创建文件时,附加内容,请用大于符号分割, 例如: a.txt>这里是文件内容
class NewFileFromSelCommand(sublime_plugin.WindowCommand):
    def run(self):
        parentPath = fileInfo(self)[4]
        selList = self.window.active_view().sel()
        for selRegion in selList:
            selPath = self.window.active_view().substr(selRegion)
            selContent = ''
            if '>' in selPath:
                selpatharr = selPath.split('>',1)
                selContent = selpatharr[1].strip()
                file_abs_path = os.path.normpath( parentPath + selpatharr[0].strip() )
            else:
                file_abs_path = os.path.normpath( parentPath + selPath )

            # print(selPath +'::' + file_abs_path + '::' +selContent)

            if selPath[-1] == '/':
                os.makedirs(file_abs_path, exist_ok=True)
                continue

            if not os.path.isfile(file_abs_path):
                os.makedirs(os.path.dirname(file_abs_path), exist_ok=True)
                with open(file_abs_path, 'w', encoding="utf-8") as fp:
                    if selContent != '':
                        fp.write(selContent)
                    else:
                        pass
                continue
                # print(path)
                # self.window.run_command('fm_creater', {'abspath': path, 'input_path': path, 'is_open': False})

# 创建序号from选择的单行或多点编辑行
class SerialNumberFromSelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selList = self.view.sel()
        sNum = 0
        for selRegion in selList:
            # tTxt = self.view.substr(selRegion)
            # self.view.replace(edit, sublime.Region(tagsStrRg.a), "updated: '{0}'\n".format(curIsoTime))
            sNum += 1
            if sNum < 10:
                strNum = str(0) + str(sNum)
            else:
                strNum = str(sNum)
            self.view.insert(edit, selRegion.a, strNum)

# 批量获取目录树 startpath: /Users/hf/work
def files_tree(startpath, yamlstr=True, yamlobj=None, isprint=None):
    tree_yaml_str = ''
    if not isprint:
        for root, dirs, files in sorted(os.walk(startpath)):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            dir_str = '{}- {}:'.format(indent, os.path.basename(root))
            tree_yaml_str = tree_yaml_str + dir_str + '\n'
            subindent = ' ' * 4 * (level + 1)  + '- '
            for f in sorted(files):
                file_str = '{}{}'.format(subindent, f)
                tree_yaml_str = tree_yaml_str + file_str + '\n'
        if yamlstr:
            return tree_yaml_str
        if yamlobj:
            return yaml.load(tree_yaml_str)[0]
    else:
        for root, dirs, files in sorted(os.walk(startpath)):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level) + '- '
            print('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)  + '- '
            for f in sorted(files):
                print('{}{}'.format(subindent, f))
        return ''

class GetDirToClipboardCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fileinfo = fileInfoObj(self.view.file_name())
        ftree = files_tree(fileinfo['path'])
        sublime.set_clipboard(ftree)
        sublime.message_dialog('目录树已经复制到剪贴版中')

# 根据一组字典替换字符串
# replaceStr('add bee', {'a': 'A', 'b': 'B'})
def replaceStr(text, replace_rule):
    def repl(m):
        mstr = m.group()
        # return 'FFF'
        return replace_rule[mstr]

    rule_old_str = "".join(replace_rule.keys())
    reg = r"[" + re.escape(rule_old_str) + "]"
    newText = re.sub(reg, repl, text)
    # print(newText)
    return newText

# 粘贴时格式化文本并paste_and_indent
symbol_rule = {'。': '.', '，': ',', '　': ' ', '／': '/', '？': '?', '；': ';', '：': ':', '‘': "'", '’': "'", '＼': '\\', '、': ',', '｜': '|', '¦': '|', '｀': '`', '～': '~', '！': '!', '＠': '@', '＃': '#', '％': '%', '￥': '$', '＆': '&', '＊': '*', '（': '(', '）': ')', '－': '-', '＋': '+', '＝': '=', '「': '[', '【': '[', '［': '[', '」': ']', '】': ']', '］': ']', '『': '{', '〖': '{', '｛': '{', '』': '}', '〗': '}', '｝': '}'}

def str_replace_translate(text, replace_rule):
    tran_old = "".join(replace_rule.keys())
    tran_new = "".join(replace_rule.values())

    translate_table = str.maketrans(tran_old, tran_new)
    trans_new = text.translate(translate_table)
    return trans_new

class FormatPasteAndIndentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        clipboardTxt = sublime.get_clipboard()
        clipboardTxt_new = str_replace_translate(clipboardTxt, symbol_rule)
        # print(clipboardTxt, clipboardTxt_new)
        sublime.set_clipboard(clipboardTxt_new)

# 从sel替换一些字符
class FormatFromSelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selList = self.view.sel()
        clipboardTxt = sublime.get_clipboard()
        print(clipboardTxt)

# 自动创建书籍目录
class AutoMakeCatlogCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fileinfo = fileInfoObj(self.view.file_name())
        parentPath = fileinfo['path'] + '/'
        catlogDict = {}

        for filename in os.listdir(parentPath):
            if not filename.startswith('.'):
                f = open(parentPath + filename, 'r', encoding="utf-8")
                data = f.read()
                if filename == 'index.md':
                    catalogStr = re.findall("```yaml(.*)```",data, re.S)
                    catalogOrder = yaml.load(catalogStr[0])
                    continue
                titleArr = re.findall("^#.*",data, re.M)
                fileObj = {
                    'name': filename,
                    'titles': titleArr
                }
                catlogDict[filename] = fileObj
        catlogStr = ""
        for items in catalogOrder:
            filenameen = items[0]
            if filenameen in catlogDict:
                titles = catlogDict[filenameen]['titles']
                thisFileName = catlogDict[filenameen]['name']
                formatTitles = ''
                for title in titles:
                    if title.startswith('# '):
                        formatTitles = formatTitles + '-   [{0}](./{1})'.format(title.replace('# ', ''), thisFileName) + "\n"
                    elif title.startswith('## '):
                        thisTitle = title.replace('## ', '')
                        thisTitle_encode = urllib.parse.quote(thisTitle)
                        formatTitles = formatTitles + '    -   [{0}](./{1}#{2})'.format(thisTitle, thisFileName, thisTitle_encode) + "\n"
                    else:
                        continue

                catlogStr += formatTitles

        startToc = self.view.find('<!-- MarkdownTOCs -->', 0, sublime.LITERAL)
        endToc = self.view.find('<!-- /MarkdownTOCs -->', 0, sublime.LITERAL)

        # yamlStr = self.view.substr(sublime.Region(3, endYamlRg.a))
        self.view.replace(edit, sublime.Region(startToc.b, endToc.a), '\n\n' + catlogStr + '\n')
        sublime.message_dialog('书籍目录创建成功')

# 自动创建书籍目录Plus
class AutoMakeCatlogPlusCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        curfileName = self.view.file_name()
        fileinfo = fileInfoObj(curfileName)
        startpath = fileinfo['path']

        treeArr = []
        for root, dirs, files in sorted(os.walk(startpath)):
            relative_path = root.replace(startpath, '')
            level = relative_path.count(os.sep)
            relative_path_sub = '.' + relative_path + '/'
            if level == 0: continue
            subindent_index = ' ' * 4 * (level-1) + '- '
            subindent = ' ' * 4 * (level) + '- '
            for f in sorted(files):
                if not f.startswith('.'):
                    if f.startswith('index_'):
                        treeArr.append([subindent_index, f, relative_path_sub])
                    else:
                        treeArr.append([subindent, f, relative_path_sub])
        # print(treeArr)

        f = open(curfileName, 'r', encoding="utf-8")
        data = f.read()
        index_yaml_str = re.findall("```yaml(.*)```",data, re.S)
        index_yaml_arr = yaml.load(index_yaml_str[0])

        tree_sort = ''
        for metainfo in index_yaml_arr:
            for tree_branch in treeArr:
                if tree_branch[1] == metainfo[0]:
                    tree_sort = tree_sort + '{}[{}]({}{} "{}")\n'.format(tree_branch[0], metainfo[1], tree_branch[2], tree_branch[1], metainfo[2])
                    break
        # print(tree_sort)

        startToc = self.view.find('<!-- MarkdownTOCs -->', 0, sublime.LITERAL)
        endToc = self.view.find('<!-- /MarkdownTOCs -->', 0, sublime.LITERAL)
        self.view.replace(edit, sublime.Region(startToc.b, endToc.a), '\n\n' + tree_sort + '\n')
        sublime.message_dialog('书籍目录创建成功')

# 获取时间等信息
class GetInfoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        t = datetime.datetime.now()
        curIsoTime = t.isoformat(' ').split('.', maxsplit=1)[0]
        selList = self.view.sel()
        for selRegion in selList:
            self.view.insert(edit, selRegion.a, curIsoTime)
# # 事件监听器
# # markdown文件链接路径自动补全 + markdown文件保存前自动更新修改时间# # 事件监听器
class AutoFilePathMarkdown(sublime_plugin.EventListener):
    def on_selection_modified(self,view):
        sel = view.sel()[0]
        isMarkdownFile = view.match_selector(sel.a, "text.html.markdown")
        if not isMarkdownFile:
            return
        if not view.window():
            return
        if sel.empty():
            if view.substr(sel.a-1) == '/':
                view.run_command('auto_complete',{'disable_auto_insert': True, 'next_completion_if_showing': False})

    # markdown文件保存前自动更新修改时间
    def on_pre_save(self,view):
        # print('onsave META')
        # filename = fileInfoList[2]
        # filePathList = fielpath.split('/')

        ## 检测文件类型
        fielpath, ext = os.path.splitext(view.file_name())
        ext = ext.lower()
        # print(fielpath, ext)
        if not ext in ['.md', '.markdown']:
            return
        # 检测是否修改
        if not view.is_dirty():
            return
        if not view.window():
            return
        # print('AutoInsertUpdateMarkdownMeta')
        view.run_command('insert_markdown_meta')

# html-css-js-json保存时格式化代码
class AutoDoSameThingOnSave(sublime_plugin.EventListener):
    def on_post_save(self,view):
        ## 检测文件类型
        fielpath, ext = os.path.splitext(view.file_name())
        ext = ext.lower()
        # print(fielpath, ext)
        if not ext in [".html", ".css", ".js", ".json", ".htm", ".xhtml", ".shtml", ".xml", ".svg", ".vue", ".scss", ".sass", ".less", ".jsx"]:
            return
        # 检测是否修改
        if not view.is_dirty():
            return
        if not view.window():
            return
        view.run_command('htmlprettify')

# 标签页激活时自动reveal_in_side_bar
class AutoDoSameThingOnSave(sublime_plugin.EventListener):
    def on_activated_async(self,view):
        if not view.window():
            return
        view.window().run_command("reveal_in_side_bar")

# 鼠标经过链接地址选择打开链接的方式
class SmartOpenLink(sublime_plugin.ViewEventListener):
    def on_hover(self, point, hover_zone):
        if hover_zone != sublime.HOVER_TEXT:
            return

        line = self.view.line(point)
        point_scope_name = self.view.scope_name(point)
        if not ('underline.link.markdown' in point_scope_name):
            return

        if 'underline.link.markdown' in point_scope_name:
            line_str = self.view.substr(line)
            fullurl = re.findall("(.*)\\[(.*)\\]\\((.*)\\)",line_str)[0]
            urlandtitle = re.findall("(.*) ['\"](.*)['\"]", fullurl[2])[0]
            relative_path = urlandtitle[0]
            curPaths = fileInfoObj(self.view.file_name())
            absolute_path = os.path.normpath(curPaths['path'] + '/' + relative_path)

            url = {
                'desc': fullurl[1],
                'link': urlandtitle[0],
                'absolute': absolute_path,
                'title': urlandtitle[1],
            }
            items = ['In Browser', 'In Sublime', 'In Finder']

            def on_done(index):
                if index == 0:
                    self.view.run_command('open_file_in_brower', {'url': url['absolute']})
                if index == 1:
                    self.view.window().open_file(url['absolute'])
                if index == 2:
                    if os.path.isdir(absolute_path):
                        self.view.window().run_command('open_dir', {'dir': absolute_path})
                    else:
                        self.view.window().run_command("open_dir", {"dir": os.path.dirname(absolute_path), "file": os.path.basename(absolute_path)})

            self.view.show_popup_menu(items, on_done)


