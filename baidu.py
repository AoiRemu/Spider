import requests
import time
from bs4 import BeautifulSoup
import json
import random

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def get_html(url):
    retry_count = 5
    while retry_count > 0:
        try:
            proxy = get_proxy().get("proxy")
            html = requests.get(url, proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            html.raise_for_status()
            html.encoding = html.apparent_encoding
            if(html.text.find('百度安全') > -1):
                print('百度安全验证')
                continue
            return html.text
        except Exception:
            retry_count -= 1
        finally:
            # 删除代理池中代理
            delete_proxy(proxy)
    return None

def get_post_list(url):
    post_list = []
    html = get_html(url)
    if(html == None):
        return post_list
    soup = BeautifulSoup(html, 'lxml')
    liTags = soup.find_all('li', attrs={'class': 'j_thread_list'})
    # liTags = soup.select('li')
    # 通过循环找到每个帖子里的我们需要的信息：
    for li in liTags:
        # 初始化一个字典来存储文章信息
        post = {}
        # 这里使用一个try except 防止爬虫找不到信息从而停止运行
        try:
            # 开始筛选信息，并保存到字典中
            post['title'] = li.find(
                'a', attrs={'class': 'j_th_tit'}).text.strip()

            if is_invalid_title(post['title']):
                continue

            post['link'] = "http://tieba.baidu.com/" + \
                li.find('a', attrs={'class': 'j_th_tit'})['href']
            post['name'] = li.find(
                'span', attrs={'class': 'tb_icon_author'}).text.strip()
            post['time'] = li.find(
                'span', attrs={'class': 'pull-right'}).text.strip()
            post['replyNum'] = li.find(
                'span', attrs={'class': 'threadlist_rep_num'}).text.strip()
            post['post_id'] = li['data-tid']
            post_list.append(post)
        except:
            print('出了点小问题')

    return post_list

def get_post_detail(post_id):
    comments = []
    html = get_html(build_post_url(post_id))
    if html == None:
        return comments
    soup = BeautifulSoup(html, 'lxml')
    commentDivs = soup.find_all('div', attrs={'class': 'l_post l_post_bright j_l_post clearfix'})
    for commentDiv in commentDivs:
        comment = {}
        comment['replyNum'] = 0
        comment['content'] = commentDiv.find('div', attrs={'class': 'd_post_content'}).text.strip()
        if comment['content'] in ['', '3']:
            continue

        replyDiv = commentDiv.find('div', attrs={'class': 'j_lzl_container core_reply_wrapper'})
        if replyDiv:
            replyJson = json.loads(replyDiv['data-field'])
            comment['replyNum'] = int(replyJson['total_num'])
        comments.append(comment)

    return comments

def build_post_url(post_id):
    return f'https://tieba.baidu.com/p/{post_id}?pn=1'

def main():
    result = []
    range_num = 5
    start_page_index = 4
    base_url = 'https://tieba.baidu.com/f?kw=%E5%BC%B1%E6%99%BA&ie=utf-8'
    for index in range(range_num):
        page_index = start_page_index + index
        url = f'{base_url}&pn={page_index * 50}'
        post_list = get_post_list(url)
        for post in post_list:
            if int(post['replyNum']) > 10:
                comments = get_post_detail(post['post_id'])
                # 从回复中找到回复数量最多的回复
                top_3 = sorted(comments, key=lambda x:x['replyNum'], reverse=True)[:3]
                answers = [top['content'] for top in top_3]
                result_item = {
                    'question': post['title'],
                    'answers': answers
                }
                result.append(result_item)
                print(result_item)
                random_sleep()
        print(f'第{page_index + 1}页爬取完毕')
        random_sleep()
    
    print(f'一共{len(result)}条帖子')
    with open(f'result_{start_page_index}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

def is_invalid_title(title):
    invalid_words = ['水楼', '神回复', '活动', '年度']
    for word in invalid_words:
        if word in title:
            return True
    return False

def random_sleep():
    random_num = random.randint(3, 10)
    time.sleep(random_num)

if __name__ == '__main__':
    main()