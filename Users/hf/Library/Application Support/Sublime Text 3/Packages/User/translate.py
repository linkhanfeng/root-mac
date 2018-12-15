import json
import urllib
import re
import os

import sublime
import sublime_plugin

# google 翻译 api
# targetUrl = 'http://translate.google.cn/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q='
targetUrl = 'http://translate.google.cn/translate_a/single'

# 使用 urllib 查询 google api

def getTranslationFromGoogle(src):
    isEn = re.findall('[a-zA-Z0-9]+',src)

    getp = {'client':'gtx', 'sl':'en', 'tl':'zh-CN', 'dt':'t', 'q':urllib.parse.quote(src)}
    if isEn:
        getp['sl'] = 'en'
        getp['tl'] = 'zh-CN'
    else:
        getp['sl'] = 'zh-CN'
        getp['tl'] = 'en'

    pstr = ''
    for k,v in getp.items():
        fixstr = ('?' if pstr == '' else '&')
        pstr =  pstr + fixstr + k +  '=' + v

    qUrl = targetUrl + pstr

    # print(6666, src.isalpha(), qUrl)
    urlP = urllib.request.Request(qUrl)
    urlP.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')

    f = urllib.request.urlopen(urlP)
    data = f.read()
    jsonResultString = data.decode()
    jsonResult = json.loads(jsonResultString)
    # print(jsonResult)
    # 得到翻译文本
    dst = jsonResult[0][0][0]
    sublime.set_clipboard(dst)
    return [dst, isEn]
# getTranslationFromGoogle('good')

# 主类
class GoogleTranslateCommand(sublime_plugin.TextCommand):
  # def run(self, edit):
  #   self.view.insert(edit, 0, "Hello, World!")

    def run(self, edit):
        selected_point = self.view.sel()[0]
        s_word = self.view.substr(selected_point)
        # print('获取选中文本::', s_word)

        def on_done(worded):
                # 查询单词
                translatedWord = getTranslationFromGoogle(worded)[0]
                self.view.window().show_input_panel('译文:', translatedWord, None, None, None)
        def on_change(worded):
            pass

        def on_cancel():
            pass

        if len(s_word) < 1:
            # print('没有选中文本')
            self.view.window().show_input_panel('请输入要翻译的文字:', '',
                            on_done,
                            on_change,
                            on_cancel)
        else:
            # 只处理第一个 Region 其它忽略
            # s_word = self.view.substr(s)
            # print(s_word)
            # 查询单词
            translationFromGoogle =  getTranslationFromGoogle(s_word)
            translatedWord = translationFromGoogle[0]
            isEn = translationFromGoogle[1]
            # print(3333333,translationFromGoogle)

            # 弹窗显示 翻译结果
            self.view.show_popup('<a href="translatedWord">' + translatedWord + '</a>', sublime.HIDE_ON_MOUSE_MOVE_AWAY, -1, 600, 500)

            if isEn:
                say_word = s_word;
            else:
                say_word = translatedWord;
            if len(say_word) < 15:
                os.system('say ' + say_word)
