import datetime as dt
import dateutil.tz
import json
import math
import os
import pprint
import time

import boto3
import pybitflyer

with open('consts.json', 'r') as f:
    consts = json.load(f)

with open('config.json', 'r') as f:
    config = json.load(f)

API_KEY = os.environ['SAVE_UP_COIN_API_KEY']
API_SECRET = os.environ['SAVE_UP_COIN_API_SECRET']
SES_REGION = os.environ.get('SAVE_UP_COIN_SES_REGION', None)
MAIL_FROM = os.environ.get('SAVE_UP_COIN_MAIL_FROM', None)
MAIL_TO = os.environ.get('SAVE_UP_COIN_MAIL_TO', None)
AWS_SESSION = boto3.Session(profile_name=os.environ.get('SAVE_UP_COIN_AWS_PROFILE', None))


def mail(subject, body):
    if not (SES_REGION and MAIL_FROM and MAIL_TO):
        return
    ses = AWS_SESSION.client('ses', SES_REGION)
    lvea = ses.list_verified_email_addresses()
    if MAIL_FROM not in lvea['VerifiedEmailAddresses']:
        print(f'Not Verified: {MAIL_FROM} in {lvea["VerifiedEmailAddresses"]}')
        return
    response = ses.send_email(
        Source=MAIL_FROM,
        Destination={'ToAddresses': MAIL_TO.split(',')},
        Message={'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body}}}
    )
    return response


def order(api, prices, task, dev):
    ret = {
        'success': False,
        'time': time.time(),
        'task': task,
    }
    mk_info = consts['markets'][task['product_code']]
    if mk_info['quote_currency'] != 'JPY':
        ret['message'] = 'Not yet support trading in markets where the quote currency is not "JPY".'
        return ret

    price = prices[task['product_code']]
    amount = task['amount_jpy'] / price
    if amount < mk_info['minimum_order_size']:
        amount = mk_info['minimum_order_size']
    amount = round(amount, -1 * math.ceil(math.log10(mk_info['unit_of_size'])))

    ret.update({
        'amount': amount,
        'reference_price': price,
        'reference_jpy': price * amount,
    })

    if not dev:
        ret['response'] = api.sendchildorder(product_code=task['product_code'], child_order_type='MARKET', side='BUY', size=amount)
        if 'child_order_acceptance_id' in ret['response']:
            ret['success'] = True
    else:
        ret.update({
            'success': True,
            'respose': {'child_order_acceptance_id': 'dev'}
        })

    return ret


def main(event, context):
    dev = event.get('dev', False) if event else False
    api = pybitflyer.API(api_key=API_KEY, api_secret=API_SECRET)
    prices = {}
    results = {'tasks': []}

    try:
        results['balance'] = api.getbalance()
    except Exception:
        pass

    for task in config['tasks']:
        try:
            if task['product_code'] not in prices:
                prices[task['product_code']] = api.ticker(product_code=task['product_code'])['ltp']
            results['tasks'].append(order(api, prices, task, dev))
        except Exception as e:
            results['tasks'].append({'success': False, 'time': time.time(), 'task': task, 'response': {'error_message': f'exception: {e}'}})

    now = dt.datetime.now(tz=dateutil.tz.gettz(config['tz']))
    pp = pprint.pformat(results, sort_dicts=False, width=200)
    mail(f'[save-up-coin] {now.strftime("%Y-%m-%d %H:%M")}', pp)
    print(pp)


if __name__ == '__main__':
    main({'dev': True}, None)
