from json import loads as load_json
from urllib.parse import unquote

from bs4 import BeautifulSoup
from htmlmin import minify
from requests import get as get_response
from time import sleep


class GetArticle(object):
    def __init__(self, username: str = None) -> None:
        """获取知乎文章并将其转换为Markdown格式

        Args:
            username (str, optional): 你的知乎用户名. Defaults to None.
        """
        super().__init__()
        self.username = username
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
        }

    def __minify(self, s: str) -> str:
        """压缩HTML代码

        Args:
            s (str): 要压缩的代码

        Returns:
            str: 压缩后的代码
        """
        return minify(s, remove_optional_attribute_quotes=False)

    def parse(self, url: str) -> dict:
        """获取知乎文章，并解析为Markdown

        Args:
            url (str): 知乎文章的链接

        Returns:
            dict: 处理后的结果
        """
        response = get_response(url, headers=self.headers)
        bs4 = BeautifulSoup(response.text, 'html.parser')
        html = self.__minify(str(bs4.find('div', class_='Post-RichText')))
        title = str(bs4.find('h1', class_='Post-Title').text)
        markdown = '# %s\n' % title
        html = html.replace(
            '<div class="RichText ztext Post-RichText">', '').replace('</div>', '')
        while html != '':
            if html.startswith('</') or html.startswith('/'):
                html = html.strip('</')
                try:
                    html = '<' + html.split('<', 1)[1]
                except:
                    html = ''
            elif html.startswith('<p></p>'):
                markdown += '\n'
                html = html.replace('<p></p>', '', 1)
            elif html.startswith('<p>'):
                _h = BeautifulSoup(html, 'html.parser')
                markdown += '\n%s\n' % str(_h.find('p')
                                           ).strip('<p>').strip('</p>').split('<')[0]
                html = html.replace(str(list(_h.find('p').strings)[0]), '', 1).replace(
                    '<p>', '', 1).replace('</p>', '', 1)
            elif html.startswith('<p class="ztext-empty-paragraph">'):
                markdown += '\n'
                html = html.replace(
                    '<p class="ztext-empty-paragraph"><br></p>', '', 1)
            elif html.startswith('<ul>'):
                _h = BeautifulSoup(html, 'html.parser')
                for li in _h.findAll('li'):
                    markdown += '- %s\n' % li.text
                markdown += '\n'
                html = html.replace(self.__minify(str(_h.find('ul'))), '')
            elif html.startswith('<ol>'):
                _h = BeautifulSoup(html, 'html.parser')
                i = 1
                for li in _h.findAll('li'):
                    markdown += '%d. %s\n' % (i, li.text)
                    i += 1
                markdown += '\n'
                html = html.replace(self.__minify(str(_h.find('ol'))), '')
            elif html.startswith('<a'):
                _h = BeautifulSoup(html, 'html.parser')
                link = str(_h.find('a')['href'])
                if _h.find('a').text.strip() != '':
                    markdown += '[%s](%s)\n' % (_h.find('a').text.strip(), link)
                else:
                    markdown += '[%s](%s)\n' % (link, link)
                if link.startswith('https://link.zhihu.com/?target='):
                    link = unquote(link.split(
                        'https://link.zhihu.com/?target=')[1])
                if html.find(str(_h.find('a'))) != -1:
                    html = html.replace(self.__minify(str(_h.find('a'))), '')
                else:
                    html = html.split('</a>', 1)[1]
            elif html.startswith('<hr>'):
                markdown += '***'
                html = html.replace('<hr>', '', 1)
            elif html.startswith('<i>'):
                _h = BeautifulSoup(html, 'html.parser')
                markdown += '*%s*' % str(_h.find('i').text)
                html = html.replace(str(_h.find('i')), '', 1)
            elif html.startswith('<div class="highlight">'):
                _h = BeautifulSoup(html, 'html.parser')
                language = _h.find('code')['class'][0].replace('language-', '')
                if language == 'python3':
                    language = 'python'
                elif 'html' in language:
                    language = 'html'
                code = _h.find('pre').text
                markdown += '```%s\n%s\n```' % (language, code)
                html = html.replace(str(_h.find('pre')), '', 1).replace(
                    '<div class="highlight">', '', 1)
            elif html.startswith('<figure'):
                _h = BeautifulSoup(html, 'html.parser')
                try:
                    src = _h.find('img')['data-original']
                except KeyError:
                    src = _h.find('img')['src']
                markdown += '![%s](%s)\n' % (src, src)
                html = html.replace(self.__minify(str(_h.find('figure'))), '')
            elif html.startswith('<h2>'):
                _h = BeautifulSoup(html, 'html.parser')
                markdown += '\n## %s\n' % _h.find('h2').text
                html = html.replace(self.__minify(str(_h.find('h2'))), '')
            else:
                markdown += '%s\n' % html.split('<', 1)[0]
                html = html.replace(html.split('<', 1)[0], '', 1)
            # with open('test.md', 'w') as f:
            #     f.write(markdown)
            # with open('test.html', 'w') as f:
            #     f.write(html)
        markdown = markdown.strip('\n')
        markdown += '\n'
        return {
            'title': title,
            'markdown': markdown
        }

    def save_article(self, title: str, markdown: str, path: str) -> None:
        """保存文章Markdown

        Args:
            title (str): 文章的标题，也是Markdown文件的名称
            markdown (str): 文章的Markdown格式的内容
            path (str): 文章保存路径
        """
        with open('%s/%s.md' % (path, title), 'w', encoding='utf-8') as f:
            f.write(markdown)

    def zhihu_to_md(self, save_path: str, url: str) -> None:
        """主函数，转换知乎文章为Markdown格式的文件并保存

        Args:
            save_path (str): 要保存的路径
            url (str): 要保存的知乎文章链接
        """
        result = self.parse(url)
        self.save_article(result['title'], result['markdown'], save_path)
    
    def get_my_articles(self) -> list:
        """获取已给定的用户名在知乎中的文章URL

        Returns:
            list: 获取的文章链接列表，用户名为None则返回[]
        """
        if self.username is None:
            return []
        return self.get_articles(self.username)
        
    def get_articles(self, username: str) -> list:
        """获取知乎上指定作者的所有文章

        Args:
            username (str): 作者名称，即在个人主页URL中的`https://www.zhihu.com/people/名称`

        Returns:
            list: 获取到的文章URL列表
        """
        response = get_response('https://www.zhihu.com/people/%s/posts' %
                                username, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        script = str(
            soup.find('script', id='js-initialData')).split('>', 1)[1].rsplit('</', 1)[0]
        data = load_json(script)
        articles = data['initialState']['entities']['articles']
        data = []
        for article in articles:
            data.append(articles[article]['url'])
        return data


if __name__ == '__main__':
    # 获取某一篇文章的Markdown
    # url = input('URL: ')
    # obj = GetArticle(url)
    # try:
    #     result = obj.zhihu_to_md('./blog', url)
    # except Exception as error:
    #     print('获取失败:', error)
    # else:
    #     print('获取成功！')
    # 获取一整个账号所发表文章的Markdown
    obj = GetArticle(input('Username: '))
    for url in obj.get_my_articles():
        print('- %s...' % url, end=' ', flush=True)
        sleep(0.5)
        obj.zhihu_to_md('./blog', url)
        print('done')
    print('完成！')
    
