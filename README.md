# epubGen for Online Novels - 网络小说ePub生成工具

## 简介

本工具的目的是基于Python实现比较方便的在线小说的自动下载以及ePub生成，支持：

- 基于CSS Selector的针对站点的可配置扩展；
- 支持文章的断点续传；
- 支持文内元素的清理排除；
- 根据下载文本生成epub 文件；
- (todo) 生成文件之后的自动发信；


## 安装

请直接Clone本仓库，然后根据requirement.txt确保依赖条件满足 （推荐使用virtualenv）


## 使用

进入epubGen的目录：

`python dumpBook.py [-n] [-r] [BookID]

![dumpBook]('readme.png')

## 网站配置：

此处以[凡人修仙传](https://www.ibiquges.org/5/5395/) 这个为例

请先复制想生成epub的书的目录页地址，同时确保对应该网站的配置文件正确放入了/configs/目录中，比如此例子中的配置文件 *ibiquges.json*

 
> {     
>     "name":"香书小说",       
>     "url":"https://www.ibiquges.info",     
>     "indexKey":"#list dd a",     
>     "contentKey":"#content",     
>     "bookName":"#info h1",     
>     "authorName":"#info p:nth-child(2)",     
>     "titleKey":".bookname h1",     
>     "fetchDelay":2,     
>     "fmimg":"#fmimg img",     
>     "excludeKeys":["script","#content_tip","p"]     
> }     

各域的定义如下：

-     "name":"香书小说",                                        网站名称
-     "url":"https://www.ibiquges.info",                        域名/地址
-     "indexKey":"#list dd a",                                  目录页中各章节的CSS选择
-     "bookName":"#info h1",                                    目录页中书名的CSS选择
-     "fmimg":"#fmimg img",                                     目录页中的封面选择
-     "authorName":"#info p:nth-child(2)",                      目录页中作者名的CSS选择
-     "titleKey":".bookname h1",                                正文页中的标题选择
-     "contentKey":"#content",                                  正文页中的正文内容选择
-     "excludeKeys":["script","#content_tip","p"]               正文页中的排除元素（比如广告）
-     "fetchDelay":2,                                           文章获取中的间隔时间（避免过快访问被ban）

新的配置文件放置之后，脚本会自动识别并且需要用户选择对应站点开始操作。


### 使用 

#### 一键自动生成

第一次或者做全本下载时: 

`py dumpBook.py -n -r '/5/5395/'`


#### 断点续传

下载前刷新目录,一般是用于检查更新:

`py dumpBook.py -n '/5/5395/'`

下载前不刷新目录,一般适用于断线或者crash之后继续下载：

`py dumpBook.py -n '/5/5395/'`


#### 重新下载

基于已有目录重新下载所有的页面

`py dumpBook.py -r '/5/5395/'`


#### 基于本地文件重新生成epub

如果本地没有工作文件，会报错，此时请还是加上"-n -r" flag来重新下载。

`py dumpBook.py '/5/5395/'`


## 其余


