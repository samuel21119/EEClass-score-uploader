#!/usr/bin/env python3
#########################################################################
# > File Name: test.py
# > Author: Samuel
# > Mail: enminghuang21119@gmail.com
# > Created Time: Mon Nov  6 00:55:19 2023
#########################################################################
import requests

def submit_score(homeworkID, reportID, ajaxAuth, grade, note, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': f'https://eeclass.nthu.edu.tw/homework/report/{reportID}/?exerciseAction=auditReport&_lock=exerciseAction&ajaxAuth={ajaxAuth}',
        'Origin': 'https://eeclass.nthu.edu.tw',
        'Connection': 'keep-alive',
        # 'Cookie': 'PHPSESSID=f49asn5q0cr8gkdlcvsa1819i4; locale=en-us; TS01e4fe74=0121fd000e38fcea1c275147f397bacff6507c09b598293f40456bccd4499cdb7f459e2e9b12f1f42a4dbf0cfdecc269c668be1c058dbbf39457a6ac8351aeadd8af17506ea1f6dd1cd7a420b8353a59fc00e332a64f48562415cfeb98917d90f640bdf3356bab33cd690920343614497a1ed454db; timezone=%2B0800; noteFontSize=100; noteExpand=0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    params = {
        '_pageMode': 'audit',
        'homeworkId': f'{homeworkID}',
        'reportId': f'{reportID}',
        '_lock': '_pageMode,homeworkId,reportId',
        'ajaxAuth': f'{ajaxAuth}',
    }

    data = {
        '_fmSubmit': 'yes',
        'formVer': '3.0',
        'formId': 'homework-audit-setting-form',
        'auditScore': f'{grade}',
        'worthWatch': '',
        'auditNote': f'{note}',
        'reportId': f'{reportID}'
    }

    response = requests.post('https://eeclass.nthu.edu.tw/homework/report/', params=params, cookies=cookies, headers=headers, data=data)
