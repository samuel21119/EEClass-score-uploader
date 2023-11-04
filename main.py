import re
import sys
import requests
import openpyxl

from bs4 import BeautifulSoup
from urllib.parse import urlencode

custom_url = 'https://eeclass.nthu.edu.tw/homework/report'
with open("cookie.txt") as f:
    cookie = f.read()



def submit(homeworkid, reportid, score, note, ajaxauth):
    note = note.replace('\n', '<br/>')
    
    post_data = {
        '_fmSubmit': 'yes',
        'formVer': '3.0',
        'formId': 'homework-audit-setting-form',
        'reportId': str(reportid),
        'auditScore': str(score),
        'auditNote': note
    }
    query_params = {
        'homeworkId': homeworkid,
        'reportId': reportid,
        'ajaxAuth': ajaxauth,
        '_pageMode': "audit",
        '_lock': '_pageMode,homeworkId,reportId'
    }
    query_string = urlencode(query_params)
    url = f"{custom_url}/?{query_string}"
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookie,
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Host': "eeclass.nthu.edu.tw",
        'Referer': url
    }
    response = requests.post(url, data=post_data, headers=custom_headers)
    if response.status_code == 200:
        print('Request success:', response.text)
    else:
        print('Request fail:', response.text)
        print(response.status_code)

def getSubmissionList(homeworkId):
    url = f"https://eeclass.nthu.edu.tw/homework/submitList/{homeworkId}"
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookie,
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Host': "eeclass.nthu.edu.tw",
        'Referer': url
    }

    
    response = requests.get(url, headers=custom_headers)
    print(response.status_code)
    ret = []
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析 HTML 內容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有的 <tr> 元素
        tr_elements = soup.find('table', {'id': 'submitList_table'}).find('tbody').find_all('tr')

        # 遍歷每個 <tr> 元素並列印其內容
        for tr in tr_elements:
            studentId = tr.find('div', {'class': 'fs-hint'}).text
            strtr = str(tr)
            ajaxauth_match = re.search(r'ajaxAuth=([\w\d]+)', strtr)
            report_match = re.search(r'report/\d+/', strtr)
            if report_match:
                reportID = report_match.group(0).replace("report", "").replace("/", "")

                response2 = requests.get(f"https://eeclass.nthu.edu.tw/homework/report/{reportID}", headers=custom_headers)
                if response2.status_code == 200:
                    submit_report = re.search(r'\/homework\/report/.*ajaxAuth.*\'>', response2.text)
                    report_url = submit_report.group(0)
                    report_url = "https://eeclass.nthu.edu.tw" + report_url[:report_url.index('\'')]

                    response3 = requests.get(report_url, headers=custom_headers)
                    if response3.status_code == 200:
                        soup2 = BeautifulSoup(response3.text, 'html.parser')
                        form_url = soup2.find('form', {'id': 'homework-audit-setting-form'})['action']
                        ajax = 'ajaxAuth='
                        ajaxauth = form_url[form_url.index(ajax) + len(ajax):]
                        ret.append([studentId, reportID, ajaxauth])
            else:
                print(f"Student: {studentId} error")
    return ret
            
def findStudentGrade(studentID, sheet):
    found_grade = None
    found_comment = None

    # 遍歷每一行，查找匹配的學號
    for row in sheet.iter_rows(values_only=True):
        student_id, grade, comment = row
        if str(student_id) == studentID:
            found_grade = grade
            found_comment = comment
            break  # 一旦找到匹配的學號，就停止搜尋
    return found_grade, found_comment
# getSubmissionList(26937)

def main():
    argv = sys.argv
    if len(argv) != 3:
        print("python3 main.py <homeworkID> <lab.xlsx>")
        exit(1)
    homeworkID = argv[1]
    file = argv[2]

    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active

    sub_list = getSubmissionList(homeworkID)
    for i in sub_list:
        studentID = i[0]
        reportID = i[1]
        ajaxauth = i[2]
        grade, comment = findStudentGrade(i[0], sheet)
        if (grade is None) or (comment is None):
            print(f"Student: {studentID} grade not found!")
        else:
            submit(homeworkID, reportID, grade, comment, ajaxauth)

if __name__ == "__main__":
    main()