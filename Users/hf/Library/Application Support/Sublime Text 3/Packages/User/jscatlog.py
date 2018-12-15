import sublime
import sublime_plugin

import re

js_catalog = ['0 入门篇 (basic)','    导论                                          bas - sum','    历史                                          bas - hist','    基本语法                                       bas - grammar',
'1 数据类型 (type)','    概述                                          typ - sum','    null，undefined 和布尔值                       typ - null','    数值                                          typ - num','    字符串　                                       typ - str','    对象                                          typ - obj','    函数                                          typ - fun','    数组                                          typ - arr',
'2 运算符 (operator)','    算术运算符                                    opr - arit (arithmetic)','    比较运算符                                    opr - compar (comparison)','    布尔运算符                                    opr - bool','    二进制位运算符                                 opr - bit','    其他运算符，运算顺序                            opr - prior (priority优先级)',
'3 语法特性 (grammar)','    数据类型的转换　                               gra - conv (conversion)','    错误处理机制　　                               gra - error','    编程风格　　　　                               gra - style','    console　控制台　                             gra - console',
'4 标准库 (stdlib)','    Object 对象                                   std - obj','    属性描述对象                                    std - attr','    Array 对象                                    std - arr','    包装对象　                                     std - wrap (wrapper)','    Boolean 对象                                  std - bool','    Number 对象                                   std - num','    String 对象                                   std - str','    Math 对象                                     std - math','    Date 对象                                     std - date','    RegExp 对象                                   std - reg (regexp)','    JSON 对象                                     std - json',
'5 面向对象编程 (oop)','    实例对象与 new 命令                             oop - new','    this 关键字                                   oop - this','    对象的继承                                     oop - proto (prototype)','    Object 对象的相关方法                           oop - object','    严格模式                                       oop - strict',
'6 异步操作 (async)','    概述                                          asy - sum','    定时器                                        asy - timer','    Promise 对象                                  asy - promise',
'7 DOM (dom)','    概述                                          dom - sum','    Node 接口                                     dom - node','    NodeList 接口，HTMLCollection 接口             dom - nodeList','    ParentNode 接口，ChildNode 接口                dom - nodeChild','    Document 节点                                 dom - doc','    Element 节点                                  dom - ele','    属性的操作                                     dom - attr','    Text 节点和 DocumentFragment 节点              dom - text','    CSS 操作                                      dom - css','    Mutation Observer API                        dom - obs (dom变动异步监视api)',
'8 事件 (event)','    EventTarget 接口                             eve - Target','    事件模型                                      eve - model','    Event 对象                                   eve - Event','    鼠标事件                                      eve - mouse','    键盘事件                                      eve - key','    进度事件                                      eve - prog (progress)','    表单事件                                      eve - form','    触摸事件                                      eve - touch','    拖拉事件                                      eve - drag','    其他常见事件                                   eve - other','    GlobalEventHandlers 接口                      eve - hand (Handler)',
'9 BOM','    浏览器模型概述                                  bom - sum','    window 对象                                   bom - window','    Navigator 对象，Screen 对象                    bom - nav (navigator)','    Cookie                                       bom - cook (cookie)','    XMLHttpRequest 对象                           bom - xml','    同源限制                                       bom - orig (same-origin)','    CORS 通信                                     bom - cors','    Storage 接口                                  bom - stor (storage)','    History 对象                                  bom - hist','    Location, URL, URLSearchParams 对象           bom - url','    ArrayBuffer 对象，Blob 对象                    bom - buf','    File 对象，FileList 对象，FileReader 对象       bom - file','    表单，FormData 对象                            bom - form',
'网页元素接口 (element)','    <a>                                          ele - a','    <img>                                        ele - image','    <form>                                       ele - form','    <input>                                      ele - input','    <button>                                     ele - button','    <option>                                     ele - option','    <video><audio>                               ele - video']

leave_two = {
    'std-obj': ['概述','Object()','Object 构造函数','Object 的静态方法','    Object.keys()，Object.getOwnPropertyNames()','    其他方法','Object 的实例方法','    Object.prototype.valueOf()','    Object.prototype.toString()','    toString() 的应用：判断数据类型','    Object.prototype.toLocaleString()','    Object.prototype.hasOwnProperty()'],
    'std-attr': ['概述','Object.getOwnPropertyDescriptor()','Object.getOwnPropertyNames()','Object.defineProperty()，Object.defineProperties()','Object.prototype.propertyIsEnumerable()','元属性','    value','    writable','    enumerable','    configurable','存取器','对象的拷贝','控制对象状态','    Object.preventExtensions()','    Object.isExtensible()','    Object.seal()','    Object.isSealed()','    Object.freeze()','    Object.isFrozen()','    局限性'],
    'std-arr': ['构造函数','静态方法','    Array.isArray()','实例方法','    valueOf()，toString()','    push()，pop()','    shift()，unshift()','    join()','    concat()','    reverse()','    slice()','    splice()','    sort()','    map()','    forEach()','    filter()','    some()，every()','    reduce()，reduceRight()','    indexOf()，lastIndexOf()','    链式使用'],
    'std-wrap': ['暂无'],
    'std-bool': ['暂无'],
    'std-num': ['暂无'],
    'std-str': ['暂无'],
    'std-math': ['暂无'],
    'std-date': ['暂无'],
    'std-reg': ['暂无'],
    'std-json': ['暂无'],
}
# std_obj = ['概述','Object()','Object 构造函数','Object 的静态方法','    Object.keys()，Object.getOwnPropertyNames()','    其他方法','Object 的实例方法','    Object.prototype.valueOf()','    Object.prototype.toString()','    toString() 的应用：判断数据类型','    Object.prototype.toLocaleString()','    Object.prototype.hasOwnProperty()']
class CatalogLanguageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(index):
            sel_str = js_catalog[index]
            sel_word_re = re.search(r'\w+\s-\s\w+', sel_str)
            sel_word = sel_word_re.group(0).replace(' - ', '-')
            sublime.set_clipboard(sel_word)

            def on_done_b(index_b):
                print('on_done_b')

            self.view.show_popup_menu(leave_two[sel_word], on_done_b)

        self.view.show_popup_menu(js_catalog, on_done)
