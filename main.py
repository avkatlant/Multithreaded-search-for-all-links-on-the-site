import random
from time import sleep
from threading import Lock
from queue import Queue
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
}


scaned_urls = set()

# DOMAIN = 'www.ds35.pupils.ru'
# DOMAIN = 'www.uzo.ru'
# DOMAIN = '45kdm.ru'
DOMAIN = 'www.transcards.ru/'

locker = Lock()  # !!! IMPORTANT define globally


def worker(queue):
    global scaned_urls
    session = HTMLSession()
    while True:
        if queue.qsize() == 0:
            sleep(5)
            if queue.qsize() == 0:
                break
        try:
            url = queue.get()
            resp = session.get(url, headers=HEADERS, timeout=3)
            # title = resp.html.xpath('//title/text()')[0].strip()

            with locker:  # !!! IMPORTANT before the blocking action
                with open('my_file.txt', 'a') as f:
                    # f.write(f'{url}\t{title}\n')
                    f.write(f'{url}\n')

                for link in resp.html.absolute_links:
                    if link in scaned_urls:
                        continue
                    elif DOMAIN not in link:
                        continue
                    else:
                        queue.put(link)
                        scaned_urls.add(link)

        except Exception as e:
            print(type(e), e)

        sleep(0.5)


def main():
    qu = Queue()
    session = HTMLSession()
    url = f'http://{DOMAIN}/'
    resp = session.get(url, headers=HEADERS, timeout=3)

    for link in resp.html.absolute_links:
        if DOMAIN not in link:
            continue
        qu.put(link)  # tuple
        scaned_urls.add(link)  # set

    print('Queue size', qu.qsize())

    with ThreadPoolExecutor(max_workers=50) as ex:
        for _ in range(50):
            ex.submit(worker, qu)


if __name__ == '__main__':
    main()
