import argparse
import pendulum
import pyjq
import requests
import sys

parser = argparse.ArgumentParser('Check availability for classes in The Gym - Ealing')
parser.add_argument('datesFile', metavar='file', type=str,
                    help='A file with dates. Each date should be in in a format '
                    'YYYY-MM-DDTHH:mm:ss, i.e., 2019-04-15T18:50:00. One per line.')
datesFile = parser.parse_args().datesFile

with open(datesFile, "r") as f:
    datesFileContent = f.readlines()

allDates = [d.strip() for d in datesFileContent]

now = pendulum.now('Europe/London')
dates = [d for d in allDates
         if now < pendulum.from_format(d, 'YYYY-MM-DDTHH:mm:ss')]
if len(dates) != len(allDates):
    with open(datesFile, "w") as f:
        f.write('\n'.join(dates))
        f.write('\n')
if not dates:
    sys.exit(0)

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

available = [pyjq.first('.sessions[] '
                        '| select(.startTime == "{}") '
                        '| select(.bookedMax - .capacityBooked > 0)' \
                        .format(date),
                        resp.json())
             for date in dates]

missingDates = [d for d in dates
                if d not in [a['startTime'] for a in available if a]]

if len(missingDates) == len(dates):
    sys.exit(0)

with open(datesFile, "w") as f:
    f.write('\n'.join(missingDates))
    f.write('\n')


available = [(a['startTime'],
              a['name'],
              a['instructorName'],
              a['bookedMax'] - a['capacityBooked'])
             for a in available if a]
out = '\n'.join(['Date: {0[0]}, '
                 'name: {0[1]}, '
                 'instructor: {0[2]}, '
                 'available spots: {0[3]}'.format(a)
                 for a in available])


print('There are available classes at The Gym - Ealing')
print('To book go to: https://www.thegymgroup.com/classes/?branchId=d05f12fc-924a-4940-b35a-6be0266a077d')
print('Available classes:')
print(out)
sys.exit(1)
