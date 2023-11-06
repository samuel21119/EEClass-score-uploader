import re
import sys
import asyncio
import requests
import openpyxl

from bs4 import BeautifulSoup
from urllib.parse import urlencode
from submit import submit_score

custom_url = 'https://eeclass.nthu.edu.tw/homework/report'
with open("cookie.txt", encoding="utf-8") as f:
    cookie_file = f.read()

cookie_file = cookie_file.split(';')
cookie = {}
for i in cookie_file:
    name, value = i.split('=')
    name = name.lstrip()
    cookie[name] = value.replace("\n", "")
print(cookie)


def submit(homeworkid, reportid, score, note, ajaxauth):
    note = note.replace('\n', '<br/>')
    submit_score(homeworkid, reportid, ajaxauth, score, note)
    

async def getAjax(studentID, reportID, headers, cookie):
    print(studentID)
    response2 = requests.get(f"https://eeclass.nthu.edu.tw/homework/report/{reportID}", headers=headers, cookies=cookie, timeout=10)
    if response2.status_code == 200:
        submit_report = re.search(r'\/homework\/report/.*ajaxAuth.*\'>', response2.text)
        report_url = submit_report.group(0)
        report_url = "https://eeclass.nthu.edu.tw" + report_url[:report_url.index('\'')]

        response3 = requests.get(report_url, headers=headers, cookies=cookie, timeout=10)
        if response3.status_code == 200:
            soup2 = BeautifulSoup(response3.text, 'html.parser')
            form_url = soup2.find('form', {'id': 'homework-audit-setting-form'})['action']
            ajax = 'ajaxAuth='
            ajaxauth = form_url[form_url.index(ajax) + len(ajax):]
            print([studentID, reportID, ajaxauth])
            return [studentID, reportID, ajaxauth]
        else:
            print(f"Student: {studentID} error")
            return []
    else:
        print(f"Student: {studentID} error")


async def getSubmissionList(homeworkID, page=1):
    url = f"https://eeclass.nthu.edu.tw/homework/submitList/{homeworkID}?order=account&precedence=ASC&page={page}"
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Host': "eeclass.nthu.edu.tw",
        'Referer': url
    }
    async def process_tr_elements(tr_elements):
        tasks = []
        for tr in tr_elements:
            studentID = tr.find('div', {'class': 'fs-hint'}).text
            strtr = str(tr)
            ajaxauth_match = re.search(r'ajaxAuth=([\w\d]+)', strtr)
            report_match = re.search(r'report/\d+/', strtr)
            if report_match:
                reportID = report_match.group(0).replace("report", "").replace("/", "")
                task = getAjax(studentID, reportID, custom_headers, cookie)
                tasks.append(task)
            else:
                print(f"Student: {studentID} error")
        results = await asyncio.gather(*tasks)
        return results
    
    response = requests.get(url, headers=custom_headers, cookies=cookie)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tr_elements = soup.find('table', {'id': 'submitList_table'}).find('tbody').find_all('tr')

        ret = list(await process_tr_elements(tr_elements))
        # print(ret)
        if (len(ret) % 50 == 0):
            next_ret = await getSubmissionList(homeworkID, page+1)
            ret.extend(next_ret)
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

    sub_list = asyncio.run(getSubmissionList(homeworkID))
    for i in sub_list:
        studentID = i[0]
        reportID = i[1]
        ajaxauth = i[2]
        grade, comment = findStudentGrade(i[0], sheet)
        if (grade is None) or (comment is None):
            print(f"Student: {studentID} grade not found!")
        else:
            if grade > 100:
                print(f"Student {studentID} grade = {grade} > 100. Only score 100 is submited!!!")
                grade = 100
            submit(homeworkID, reportID, grade, comment, ajaxauth)

if __name__ == "__main__":
    main()
