import requests
import re
from bs4 import BeautifulSoup as bs
import os
import time
import random

URL = 'https://www.gutenberg.org/browse/languages/zh'
SOURCE_PATH = 'source'
RESULT_PATH = 'project_gutenberg'

def load_book_list_page():
    res = requests.get(URL)
    text = res.text
    return text

def parser_book_list(text):
    soup = bs(text, "lxml")
    a_list = soup.select('li[class=pgdbetext] > a')
    return a_list

def handle_book_list(a_list):
    book_dict = {}

    # 初步整理
    # 1. 刪除全英文書名
    # 2. 將重複書名增加編號

    for a in a_list:
        book_name = a.get_text()
        # 刪除檔名符號
        book_name = re.sub(r'[\—\-\.\=\,\n\r]', '', book_name)

        # 刪除全英文書名
        re_book_name = re.sub(r'[0-9a-zA-Z :/\—\-\.\=\,\(\)\n\r]', '', book_name)
        if re_book_name == '':
            continue

        # 同書名加上編號
        for i in range(1, 100):
            if i == 1 and book_name not in book_dict:
                break
            else:
                new_book_name = f'{book_name}_{i}'
                if new_book_name not in book_dict:
                    book_name = new_book_name
                    break

        # 處理書本ID
        book_id = re.search(r'\/(\d+)', a['href'])[1]

        # 無編號不爬取
        if book_id:
            book_dict[book_name] = {'book_id': book_id}
    return book_dict

def load_book_page(book_dict):
    # 進度確認
    total = len(book_dict)
    now_page_number = 1

    for book_name, book_obj in book_dict.items():
        print(f'目前進度：{now_page_number}/{total}')
        now_page_number += 1

        # if now_page_number > 200:
        #     break

        file_name = f'{SOURCE_PATH}/{book_name}.txt'
        if os.path.isfile(file_name):
            continue

        book_id = book_obj['book_id']
        # book_page_url = f'https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt'
        book_page_url = f'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt'

        res = requests.get(book_page_url)
        with open(file_name, 'w', encoding='utf8') as f:
            f.write(res.text)

        time.sleep(random.randint(1,3))

def handle_book_page():
    files = os.listdir(SOURCE_PATH)
    for file in files[:]:
        filename = f'{SOURCE_PATH}/{file}'
        if os.path.isfile(filename) and 'txt' in file:
            with open(filename, 'r', encoding='utf8') as f:
                txt = f.read()

            # 去除開頭結尾英文
            result = re.split(r'\*\*\*.*?\*\*\*', txt)[1]

            # 去除其他英文、符號
            result = re.sub(r'[a-zA-Z:\-\(\)]', '', result)

            # 去除開頭結尾換行
            result = result.strip()

            with open(f'{RESULT_PATH}/{file}', 'w', encoding='utf8') as f:
                f.write(result)

def main():
    # 建立資料夾
    if not os.path.exists(SOURCE_PATH):
        os.mkdir(SOURCE_PATH)

    if not os.path.exists(RESULT_PATH):
        os.mkdir(RESULT_PATH)

    text = load_book_list_page()

    a_list = parser_book_list(text)

    book_dict = handle_book_list(a_list)

    load_book_page(book_dict)

    handle_book_page()

if __name__ == '__main__':
    main()
