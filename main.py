import requests
from bs4 import BeautifulSoup
import threading
import json
import random
from functools import wraps

CARD_URL = 'https://www.aw-lab.com/shop/athletesworld2_minicart/cart/json'
MAIN_URL = 'https://www.aw-lab.com/'
CHECKOUT_URL = 'https://www.aw-lab.com/shop/onestepcheckout/'



def repeat(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print('Exception for {}'.format(func.__name__), e)
                continue
    
    return wrapped_func


proxy_file = 'proxies.txt'
def read_proxies():
    global proxies
    with open(proxy_file) as f:
        proxies = f.readlines()



def get_proxy():
    p = random.choice(proxies)
    p = p.replace('\n', '').strip()
    if p.startswith('https'):
        return {
            'https': 'https://' + p
        }
    elif p.startswith('ftp'):
        return {
            'ftp': 'ftp://' + p
        }
    elif p.startswith('socks5'):
        return {'http': 'socks5://' + p, 'https': 'socks5://' + p}
    else:
        return {
            'http': 'http://' + p,
            'https': 'https://' + p
        }


@repeat
def get_session():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    }
    session = requests.Session()    
    session.headers.update(headers)
    resp = session.get('https://www.aw-lab.com/shop/fanplayrcart/status/cart',
                                   headers={'X-Requested-With': 'XMLHttpRequest'})
    resp.raise_for_status()

    return session


from utils import create_form_data

class Task(threading.Thread):
    def __init__(self, id, product_data, task, session):
        super(Task, self).__init__()
        self.id = id
        self.request_num = 0
        self.product_data = product_data
        self.task = task
        self.session = session

    def log(self, text):
        print(f'TASK {self.id}: {text}.')

    def get_size(self):
        sizes = self.task['sizes']
        size = sizes[self.request_num % len(sizes)]
        return size

    def get_name(self):
        return self.get_from_list(self.task['names'])
    
    def get_surname(self):
        return self.get_from_list(self.task['surnames'])
    
    def get_email(self):
        return self.get_from_list(self.task['emails'])

    def get_from_list(self, list):
        return list[self.request_num % len(list)]


    @repeat
    def add_product_to_card(self):
        size = self.get_size()
        post_data = {
            'super_attribute[959]': size,
            'product': self.product_data['product'],
            'qty': 1,
            'related_product': ''
        }
        resp = self.session.post(
            self.product_data['add_to_card_url'],
            data=post_data,
            headers={
                'Referer': PRODUCT_URL,
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
            }
            #proxies = get_proxy()
        )
        resp.raise_for_status()
        resp_json = json.loads(resp.text)
        self.request_num = self.request_num + 1
        if not resp_json['added']:
            self.log(f'add_product_to_card error: {resp_json["return"]}')
            return False
        else:
            self.log(f'product is addess successfully')
    
        return True

    @repeat
    def get_shipping_address_id(self):
        resp = self.session.get(CHECKOUT_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        shipping_address_id = soup.find('input', attrs={'name': 'shipping[address_id]'})['value']
        return shipping_address_id
    

    @repeat
    def make_order_request(self, shipping_address_id):
        resp = self.session.post(
            CHECKOUT_URL,
            data=create_form_data(self.get_name(), self.get_surname(), self.get_email(), shipping_address_id),
            headers={
                'Content-type': 'application/x-www-form-urlencoded',
            }
        )
        resp.raise_for_status()
        return resp

    def purchase_order(self):
        shipping_address_id = self.get_shipping_address_id()
        while True:
            try:
                resp = self.make_order_request(shipping_address_id)
                if 'Grazie!' in resp.text:
                    self.log(f'purchase order is made successfull')
                    break
                else:
                    self.log(f'purchase order is not made')
                    continue
            except Exception as e:
                self.log(f'purchase order error: {e}')
                continue

        

    def run(self):
        self.log('Start running')
        while True:
            try:
                res = self.add_product_to_card()
                if not res:
                    continue
            except Exception as e:
                self.log(f'add_product_to_card error: {e}')
                continue

            self.purchase_order()
    
   


@repeat
def get_product_data(session):
    response = session.get(PRODUCT_URL)
    response.raise_for_status()
    html = BeautifulSoup(response.text, 'html.parser')
    form = html.find('form', attrs={'id': 'product_addtocart_form'})
    add_to_cart_url = form['action'].replace('checkout/cart', 'athletesworld2_minicart/ajaxCart')
    product_id = html.find('input', attrs={'name': 'product'})['value']
    return {
        'product': int(product_id),
        'qty': 1,
        'related_product': '',
        'add_to_card_url': add_to_cart_url,
    }




def main():
    read_proxies()
    data = None
    global PRODUCT_URL
    PRODUCT_URL = input('Enter product url: \n')
    session = get_session()

    product_data = get_product_data(session)

    threads = []
    with open('tasks.json', 'r') as tasks:
        tasks_json = json.loads(tasks.read())
        tasks_arr=tasks_json['tasks']
        
        for id, t in enumerate(tasks_arr):
            t = Task(id, product_data, t, session)
            threads.append(t)
            t.start()


    for t in threads:
        t.join()


if __name__== '__main__':
    main()
