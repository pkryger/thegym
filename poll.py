import argparse
import pendulum
import requests
import sys

from netrc import netrc
from smtplib import SMTP_SSL

def get_args():
    parser = argparse.ArgumentParser('Check availability for classes in The Gym - Ealing')
    parser.add_argument('datesFile', metavar='file', type=str,
                        help='A file with dates. Each date should be in in a format '
                        'YYYY-MM-DDTHH:mm:ss, i.e., 2019-04-15T18:50:00. One per line.')
    return parser.parse_args()

def get_dates_and_update_file(datesFile):
    with open(datesFile, "r") as f:
        datesFileContent = f.readlines()

    allDates = [d.strip() for d in datesFileContent if d.strip()]
    now = pendulum.now('Europe/London')
    now = now.add(minutes=20)
    def is_valid_and_after_now(date):
        try:
            return now < pendulum.from_format(date,
                                              'YYYY-MM-DDTHH:mm:ss',
                                              tz='Europe/London')
        except ValueError:
            return False

    dates = [d for d in allDates
             if is_valid_and_after_now(d)]
    if len(dates) != len(allDates):
        with open(datesFile, "w") as f:
            f.write('\n'.join(dates))
    return dates

def get_sessions():
    url = 'https://www.thegymgroup.com/MemberBookClassBlock/GetClasses'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*',
        'Host': 'www.thegymgroup.com',
        'Accept-Language': 'en-gb',
        'Accept-Encoding': 'br, gzip, deflate',
        'Origin': 'https://www.thegymgroup.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
        'Referer': 'https://www.thegymgroup.com/classes/?branchId=d05f12fc-924a-4940-b35a-6be0266a077d',
        'DNT': '1',
        'Content-Length': '86',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = {
        'branchId': 'd05f12fc924a4940b35a6be0266a077d',
        'date': pendulum.now('Europe/London').format('YYYY-MM-DDTHH:mm:ss'),
        'classType': 'Class',
    }
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code != 200:
        return None
    return resp.json()['sessions']

def get_classes_and_not_available(dates, sessions):
    available = [s for s in sessions
                 if s['startTime'] in dates \
                 and s['bookedMax'] - s['capacityBooked']]

    not_available = [d for d in dates
                     if d not in [a['startTime'] for a in available if a]]

    classes = [(a['startTime'],
                a['name'],
                a['instructorName'],
                a['bookedMax'] - a['capacityBooked'])
               for a in available]
    return classes, not_available

def get_text(classes):
    c = '\n'.join(['- Date: {0[0]}, '
                   'class: {0[1]}, '
                   'instructor: {0[2]}, '
                   'available spots: {0[3]}'.format(c)
                   for c in classes])
    return '''\
There are available classes at The Gym - Ealing

To book go to: https://www.thegymgroup.com/classes/?branchId=d05f12fc-924a-4940-b35a-6be0266a077d

Available classes:
{}'''.format(c)

def send_mail(text):
    login, _, password = netrc().authenticators('smtp.gmail.com')
    to = [login]
    email ='''\
From: {}
To: {}
Subject: Classes at The Gym - Ealing

{}
'''.format(login, ', '.join(to), text)
    with SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.ehlo()
        smtp.login(login, password)
        smtp.sendmail(login, to, email)

def do_poll(args):
    datesFile = args.datesFile
    dates = get_dates_and_update_file(datesFile)
    if not dates:
        return 0

    sessions = get_sessions()
    if not sessions:
        return 0

    classes, not_available = get_classes_and_not_available(dates, sessions)
    if len(not_available) == len(dates):
        return 0

    with open(datesFile, "w") as f:
        f.write('\n'.join(not_available))

    text = get_text(classes)
    send_mail(text)
    return 1

if __name__ == '__main__':
    args = get_args()
    rc = do_poll(args)
    sys.exit(rc)
