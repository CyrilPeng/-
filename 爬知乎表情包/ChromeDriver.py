import requests, os
from time import sleep
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver

class Download_by_chrome():
    def __init__(self):
        self.url = input('输入需要爬取表情包的知乎链接\n')
        # 打开chrome，设置无界面运行
        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_headless()
        # 取消chrome正在自动化测试
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

    def mkdir(self):
        '''以网页标题作为名称，新建目录
        
        :return: 新建目录的名称
        '''
        # 获取网页标题
        title = self.driver.title
        # 去掉不合法文件夹命名字符
        flag = r'\/:*?"<>|'
        title = title.replace(':','：').replace('?','？')
        for i in flag:
            f = title.find(i)
            if f != -1:
                title = title.replace(title[f],'')
        print(title)
        # 如果目录不存在则新建
        if not os.path.isdir(title):
            os.mkdir(title)
        self.title = title

    def get_imgs(self):
        '''获取当前网页图片元素，并将元素存入列表

        :return: 静态图元素列表，动图元素列表
        '''
        def _get_question(html, jpgs, gifs):
            '''如果是问题，需要进行gif判定，并且替换网址中的.jpg为.gif
            '''
            print('问题页面加载完成，正在解析图片源地址')
            soup = BeautifulSoup(html, 'html.parser').find('div', class_='ListShortcut')
            imgs = soup.find_all('img')
            gifs_list = []
            jpgs_list = []
            # 判断是gif还是jpg
            for img in imgs[::2]:
                if 'ztext-gif' in img['class']:
                    gifs_list.append(img)           
                elif 'AuthorInfo-avatar' in img['class']:
                    # 去掉作者头像
                    pass
                else:
                    jpgs_list.append(img)

            # 提取jpg链接
            for jpg in jpgs_list[:]:
                try:
                    url = jpg['data-original']
                except:
                    try:
                        url = jpg['data-actualsrc']
                    except:
                        try:
                            url = jpg['data-thumbnail']
                        except:
                            url = jpg['src']
                jpgs.append(url)

            # 提取gif链接，并将jpg替换为gif
            for gif in gifs_list[:]:
                try:
                    url = gif['data-original']
                except:
                    try:
                        url = gif['data-actualsrc']
                    except:
                        try:
                            url = gif['data-thumbnail']
                        except:
                            url = gif['src']
                url = url.replace('jpg', 'gif')
                gifs.append(url)
                
            return jpgs, gifs

        def _get_zhuanlan(html, jpgs, gifs):
            '''如果是专栏就直接拿链接，前端源码里面就有
            '''
            print('专栏页面加载完成，正在解析图片源地址')
            soup = BeautifulSoup(html, 'html.parser').find('div', class_='Post-RichTextContainer')
            imgs = soup.find_all('img')
            for img in imgs[::2]:
                url = img['src']
                if '.gif' in url:
                    gifs.append(url)
                else:
                    jpgs.append(url)
            return jpgs, gifs

        # 新建空列表用于存储网页元素信息
        jpgs = []
        gifs = []

        # 获取页面
        html = self.driver.page_source

        # 检查是专栏还是问题
        if 'question' in self.url:
             _get_question(html, jpgs, gifs)
        elif 'zhuanlan' in self.url:
            _get_zhuanlan(html, jpgs, gifs)
        else:
            print('网址输入有问题，请检查')
            return

        print('一共在本页面找到%d个jpg表情和%d个gif动图' % (len(jpgs), len(gifs)))
        return jpgs, gifs

    def save_imgs(self, jpgs, gifs):
        '''解析图片元素列表，存储图片到本地

        :param title: 存储的文件夹名称

        :param jpgs: jpg的源地址列表

        :param gifs: gif的源地址列表

        :return: None
        '''
        i = 0
        for url in jpgs[:]:
            i += 1   
            pathName = "./%s/图片%d.jpg"%(self.title, i)
            urllib.request.urlretrieve(url, pathName)
            print('正在爬第%d张jpg图片，一共%d张jpg图片'%(i,len(jpgs)))

        i = 0
        for url in gifs[:]:
            i += 1 
            pathName = "./%s/动图%d.gif"%(self.title, i)
            urllib.request.urlretrieve(url, pathName)
            print('正在爬第%d张gif动图，一共%d张gif动图'%(i,len(gifs)))

    def main(self):
        # 跳转到表情包页面      
        self.driver.get(self.url)
        self.mkdir()
        jpgs = []
        gifs = []
        jpgs, gifs = self.get_imgs()
        self.save_imgs(jpgs, gifs)
        print('全部爬取完成，5秒后自动退出')
        sleep(5)
        self.driver.quit()

if __name__ == "__main__":
    test = Download_by_chrome()
    test.main()
