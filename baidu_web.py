# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager

# path = ChromeDriverManager().install()
# print(path)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json

def random_sleep():
    random_num = random.randint(3, 10)
    time.sleep(random_num)

def link_to_comment(post_ele):
    title_ele = post_ele.find_element(By.CSS_SELECTOR, 'a.j_th_tit')
    title_ele.click()
    wait.until(EC.number_of_windows_to_be(2))
    random_sleep()
    switch_to_new_tab()
    close_login_dialog()


def get_comment_info():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#j_p_postlist .l_post.l_post_bright')))
    comment_list = []
    comment_ele_list = driver.find_elements(By.CSS_SELECTOR, '#j_p_postlist .l_post.l_post_bright')
    for comment_ele in comment_ele_list:
        try:
            comment = {}
            comment['replyNum'] = 0
            comment['content'] = comment_ele.find_element(By.CSS_SELECTOR, '.d_post_content.j_d_post_content ').text
            if comment['content'] in ['', '3']:
                continue

            replyDiv = comment_ele.find_element(By.CSS_SELECTOR, '.j_lzl_container.core_reply_wrapper')
            if replyDiv:
                replyData = replyDiv.get_attribute('data-field')
                if replyData:
                    replyJson = json.loads()
                    comment['replyNum'] = int(replyJson['total_num'])
            comment_list.append(comment)
        except:
            pass
    
    driver.close()
    driver.switch_to.window(origin_window)
    random_sleep()
    return comment_list

def close_login_dialog():
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.tieba-login-wrapper .close-btn')))
        close_ele = driver.find_element(By.CSS_SELECTOR, '.tieba-login-wrapper .close-btn').click()
    except:
        pass
    random_sleep()

def switch_to_new_tab():
    # 循环执行，直到找到一个新的窗口句柄
    for window_handle in driver.window_handles:
        if window_handle != origin_window:
            driver.switch_to.window(window_handle)
            break

def to_next_page():
    next_ele = driver.find_element(By.CSS_SELECTOR, '#frs_list_pager a.next.pagination-item').click()
    random_sleep()

def is_invalid_title(title):
    invalid_words = ['水楼', '神回复', '活动', '年度']
    for word in invalid_words:
        if word in title:
            return True
    return False

def save_to_json(results, end_page_index):
    with open(f'./results/result_{end_page_index}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

def build_url(start_page_index):
    return f'https://tieba.baidu.com/f?kw=%E5%BC%B1%E6%99%BA&ie=utf-8&pn={start_page_index * 50}'

options = Options()
options.add_argument('--headless')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
options.page_load_strategy = 'eager'

s = Service('./webdrivers/chromedriver.exe')
driver = webdriver.Chrome(service=s, options=options)

start_page_index = 1242
driver.get(f'https://tieba.baidu.com/f?kw=%E5%BC%B1%E6%99%BA&ie=utf-8&pn={build_url(start_page_index)}')
wait = WebDriverWait(driver, 10)
origin_window = driver.current_window_handle
random_sleep()
close_login_dialog()



range_num = 1000
results = []
end_page_index = start_page_index

try:
    for page_index in range(range_num):
        post_li_ele_list = driver.find_elements(By.CSS_SELECTOR,'li.j_thread_list.clearfix')
        for post_ele in post_li_ele_list:
            result_item = {}
            post = {}
            title_ele = post_ele.find_element(By.CSS_SELECTOR, 'a.j_th_tit')
            post['title'] = title_ele.text
            if is_invalid_title(post['title']):
                continue

            post['reply_num'] = post_ele.find_element(By.CSS_SELECTOR, '.threadlist_rep_num').text
            if post['reply_num'] and int(post['reply_num']) < 10:
                continue

            link_to_comment(post_ele)
            comments = get_comment_info()
            # 从回复中找到回复数量最多的回复
            top_3 = sorted(comments, key=lambda x:x['replyNum'], reverse=True)[:3]
            answers = [top['content'] for top in top_3]
            result_item = {
                'question': post['title'],
                'answers': answers
            }
            results.append(result_item)
            
        end_page_index += 1
        print(f'第{page_index + 1}页爬取完成, 网址：{driver.current_url}')
        to_next_page()
        random_sleep()
except Exception as err:
    print(err)
    pass

save_to_json(results, end_page_index)
time.sleep(1000)

