#!/usr/bin/python2

import sys
from lxml import html
import requests
import argparse
import datetime
import smtplib
from email.mime.text import MIMEText

parser = argparse.ArgumentParser(description='App to search FCC ULS for callsign')
parser.add_argument('fccfrn',
                    help='A required FCC ULS Number')
parser.add_argument('--msgto',
                    help='Comma separated email addresses to send the notification to', required=True)
parser.add_argument('--msgfrom',
                    help='Email address to send the message from', required=True)
parser.add_argument('--msgsubject',
                    help='Email subject for the notification', required=True)
args = parser.parse_args()

urlsearch = 'http://wireless2.fcc.gov/UlsApp/UlsSearch/searchAdvanced.jsp'
urlresult = 'http://wireless2.fcc.gov/UlsApp/UlsSearch/results.jsp'
today = datetime.date.today()
todaydate = today.strftime('%-m/%d/%Y')

page = requests.get(urlsearch)

headers = {
"Cookie": page.headers["set-cookie"],
"Content-Type": "application/x-www-form-urlencoded",
"Referer": urlsearch
}

data = {
'fiUlsServiceSearchByType':100,
'fiRadioServiceMatchAllInd':'some',
'radioservicecode':'HA',
'fiUlsFRN':args.fccfrn,
'statusAll':'Y',
'ulsAuthTypeAll':'Y',
'ulsToDate':todaydate,
'feqSearchType':'any',
'fiRowsPerPage':10,
'ulsSortBy':'uls_l_callsign',
'ulsOrderBy':'ASC',
'hiddenForm':'hiddenForm',
'jsValidated':'true',
'searchType':'ULN'
}
page = requests.post(urlresult, data = data, headers = headers)
#print page.content
#print 'End Content'
tree = html.fromstring(page.content)
licenses = tree.xpath('//table[@summary="License search results"]/tr')

text = ''

for license in licenses:
  if 'align' in license.attrib.keys():
    callsign = license[1][0].text
    licenseename = license[2].text.strip()
    text = text + "\n%s %s" % (callsign, licenseename)

if text != '':
  msgto = args.msgto.split(",")
  msg = MIMEText(text)
  msg['Subject'] = args.msgsubject
  msg['From'] = args.msgfrom
  msg['To'] = ",".join(msgto)
  s = smtplib.SMTP('localhost')
  s.sendmail(msg['From'],msgto,msg.as_string())
  s.quit()
