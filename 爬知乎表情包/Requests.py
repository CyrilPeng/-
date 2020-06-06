from gevent import monkey
monkey.patch_all()
from gevent.queue import Queue
import gevent, os, requests, urllib.request
from time import sleep
from bs4 import BeautifulSoup


class Download_by_requests():
    def __init__(self):
        self.url = input('输入需要爬取表情包的知乎链接\n')  
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/70.0.3538.110 Safari/537.36'}      
        self.res = requests.get(url=self.url,headers=self.headers)
        self.res.encoding = 'utf-8'
        self.res = self.res.text
        # 正在爬取的jpg的序号
        self.jpg = 0
        # 正在爬取的gif的序号
        self.gif = 0
        # jpg图片总数
        self.jpg_num = 0
        # gif图片总数
        self.gif_num = 0
        # 爬取的知乎链接标题
        self.title = ''

    def mkdir(self, res:'str'):
        '''以网页标题作为名称，新建目录

        :param res: get请求返回的字符串
        
        :return: 新建目录的名称
        '''
        # 获取网页标题
        title = BeautifulSoup(res, 'html.parser').find('title').string
        # 去掉不合法文件夹命名字符
        flag = r'\/:*?"<>|'
        title = title.replace(':','：').replace('?','？')
        for i in flag:
            f = title.find(i)
            if f != -1:
                title = title.replace(title[f],'')
        # 如果目录不存在则新建
        if not os.path.isdir(title):
            os.mkdir(title)
            print('成功在本目录下新建文件夹:' + title)
        return title


    def get_anwser(self, jpgs:'list==[]', gifs:'list==[]'):
        '''如果是回答，需要进行gif判定，并且替换网址中的.jpg为.gif

        :param jpgs: jpg的源地址列表，限定为空

        :param gifs: gif的源地址列表，限定为空

        :return: jpgs是解析后的jpg源地址列表, gifs是解析后的gif源地址列表
        '''
        soup = BeautifulSoup(self.res, 'html.parser').find('div', class_='ListShortcut')
        imgs = soup.find_all('img')
        gifs_list = []
        jpgs_list = []
             
        # 判断是gif还是jpg
        for img in imgs[1::2]:
            try:
                img['data-thumbnail']
                gifs_list.append(img)       
            except:
                jpgs_list.append(img)    
   
        # 提取jpg链接
        for jpg in jpgs_list[:]:
            try:
                url = jpg['src']
            except:
                url = jpg['data-default-watermark-src']            
            jpgs.append(url)

        # 提取gif链接，并将jpg替换为gif
        for gif in gifs_list[:]:
            url = gif['data-thumbnail'].replace('jpg', 'gif')
            gifs.append(url)

        self.jpg_num = self.jpg_num + len(jpgs)
        self.gif_num = self.gif_num + len(gifs)
        print('一共在本回答找到%d个jpg表情和%d个gif动图' % (len(jpgs), len(gifs)))
        return jpgs, gifs

    def get_zhuanlan(self, jpgs:'list==[]', gifs:'list==[]'):
        '''如果是专栏就直接拿链接，前端源码里面就有

        :param jpgs: jpg的源地址列表，限定为空

        :param gifs: gif的源地址列表，限定为空

        :return: jpgs是解析后的jpg源地址列表, gifs是解析后的gif源地址列表
        '''
        print('专栏页面加载完成，正在解析图片源地址')
        soup = BeautifulSoup(self.res, 'html.parser').find('div', class_='Post-RichTextContainer')
        imgs = soup.find_all('img')
        for img in imgs[::2]:
            url = img['src']
            if '.gif' in url:
                gifs.append(url)
            else:
                jpgs.append(url)

        self.jpg_num = self.jpg_num + len(jpgs)
        self.gif_num = self.gif_num + len(gifs)
        print('一共在本专栏找到%d个jpg表情和%d个gif动图' % (len(jpgs), len(gifs)))
        return jpgs, gifs


    def save_imgs(self, jpgs:'list', gifs:'list', title:'str'):
        '''解析图片元素列表，存储图片到本地

        :param jpgs: jpg的源地址列表

        :param gifs: gif的源地址列表

        :param title: 保存的文件夹名称

        :return: None
        '''
        def _save():
            while not work.empty():
                img = work.get_nowait()
                url = img
                # 检查是否为gif
                if '.gif' in url:
                    self.gif += 1
                    pathName = "./%s/动图%d.gif"%(title, self.gif)
                    print('jpg-已完成%d张，共%d张；gif-已完成%d张，共%d张。'%(self.jpg, self.jpg_num, self.gif, self.gif_num))
                    urllib.request.urlretrieve(url, pathName)       
                else:
                    self.jpg += 1
                    pathName = "./%s/图片%d.jpg"%(title, self.jpg)
                    print('jpg-已完成%d张，共%d张；gif-已完成%d张，共%d张。'%(self.jpg, self.jpg_num, self.gif, self.gif_num))
                    urllib.request.urlretrieve(url, pathName)

        # 建立队列
        work = Queue()
        # 建立图片原地址列表
        for url in jpgs:
            work.put_nowait(url)
        for url in gifs:
            work.put_nowait(url)

        # 添加任务到队列并开始执行
        tasks_list = []  
        for x in range(4):
            task = gevent.spawn(_save)
            tasks_list.append(task)
        gevent.joinall(tasks_list)
        print('一共爬取了%d个jpg表情和%d个gif动图' % (self.jpg, self.gif))

    def main(self):
        while 'question' in self.url and 'answer' not in self.url:
            print('不要粘贴问题的网址啊，图片太多会爆炸的，只能粘贴回答和专栏的网址')
            self.url = input('请重新输入需要爬取表情包的知乎链接\n')

        self.title = self.mkdir(self.res)
        # 新建空列表用于存储网页元素信息
        jpgs = []
        gifs = []
        # 检查是专栏还是问题
        if 'answer' in self.url:
            print('回答页面加载完成，正在解析图片源地址')
            jpgs, gifs = self.get_anwser(jpgs, gifs)
        elif 'zhuanlan' in self.url:
            print('专栏页面加载完成，正在解析图片源地址')
            jpgs, gifs = self.get_zhuanlan(jpgs, gifs)
        elif 'question' in self.url:
            input('不要粘贴问题的链接啊，图片太多会爆炸的，只能粘贴回答和专栏的链接，按任意键退出')
            return
        else:
            print('网址输入有问题，请检查')
            return  
        self.save_imgs(jpgs, gifs, self.title)      
        print('全部爬取完成，稍后自动退出')


if __name__ == "__main__":
    test = Download_by_requests()
    test.main()
