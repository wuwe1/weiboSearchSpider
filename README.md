本repo会包含几个（目前是2个）用于爬取微博搜索页面的爬虫
包括模拟登陆和页面解析，代码都是顺序的，比较方便理解和学习

参考https://www.jianshu.com/p/816594c83c74实现的微博模拟登陆
里面抓包并分析的步骤非常的重要
文中用的抓包工具是http analyzer，我用的火狐
登陆后使用beautiful soup对抓取的页面进行解析

50_recent_pages.py是我最初使用的爬取https://s.weibo.com/weibo?q=%s&nodup=1&page=%d
这个文件只能爬去某关键字的最新的50页微博（而且我没有解析被转发微博）

weiboCustomSearch.py爬取的是指定区间的时间端的微博（最多50页）

本人比较喜欢直接在python的repl里面运行代码，所以代码写的相当随性
建议有兴趣的同学直接在repl里面运行我的代码
