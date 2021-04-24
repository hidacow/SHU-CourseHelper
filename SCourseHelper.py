import base64
import getpass
import time
from collections import namedtuple
import lxml.etree
from os import system, name
import requests
import rsa


# Settings
QUERY_DELAY = 5
CHK_SELECT_TIME_DELAY = 5
WARN_DIFF_CAMPUS = True

# Variables
Termlist = []
Courselist = []

# Declaration
Termitem = namedtuple("Term", ["termid", "name"])
Courseinfo = namedtuple("CourseInfo", [
    "courseid", "coursename", "teacherid", "teachername", "capacity", "number",
    "restriction"
])
Courseitem = namedtuple("CourseItem", ["courseid", "teacherid"])
Selectionresult = namedtuple(
    "SelectionResult",
    ["courseid", "coursename", "teacherid", "teachername", "msg", "isSuccess"])

# Base Urls
_baseurl = "http://xk.autoisp.shu.edu.cn/"
_termindex = "Home/TermIndex"
_termselect = "Home/TermSelect"
_fastinput = "CourseSelectionStudent/FastInput"
_querycourse = "StudentQuery/QueryCourseList"
_selectcourse = "CourseSelectionStudent/CourseSelectionSave"
_diffcampus = "CourseSelectionStudent/VerifyDiffCampus"
_selectedcourse = "CourseSelectionStudent/QueryCourseTable"
_dropcourse = "CourseReturnStudent/CourseReturnSave"

# SSO Pubkey
_keystr = '''-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OLOU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plWf5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSRwTBNePOk1H+LRQokgQIDAQAB
    -----END PUBLIC KEY-----'''


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux
    else:
        _ = system('clear')


def encryptPass(passwd):
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(_keystr.encode('utf-8'))
    encryptpwd = base64.b64encode(rsa.encrypt(passwd.encode('utf-8'),
                                              pubkey)).decode()
    return encryptpwd


def getTerms(text):
    html = lxml.etree.HTML(text)
    termslist = html.xpath("//table/tr[@name='rowterm']")
    terms = []
    for term in termslist:
        termid = int(term.attrib["value"])
        name = term.xpath("./td/text()")[0].strip()
        terms.append(Termitem(termid, name))
    return terms


def getCourseInfo(cid, tid, sess):
    params = {
        "PageIndex": 1,
        "PageSize": 1,
        "FunctionString": "Query",
        "CID": cid,
        "CourseName": "",
        "IsNotFull": "False",
        "CourseType": "B",
        "TeachNo": tid,
        "TeachName": "",
        "Enrolls": "",
        "Capacity1": "",
        "Capacity2": "",
        "CampusId": "",
        "CollegeId": "",
        "Credit": "",
        "TimeText": ""
    }
    r = sess.post(_baseurl + _querycourse, params)
    if "未查询到符合条件的数据！" in r.text:
        raise RuntimeError(3, f"Course Not Exist")
    html = lxml.etree.HTML(r.text)
    td = html.xpath("//table[@class='tbllist']/tr/td")
    return Courseinfo(courseid=td[0].text.strip(),
                      coursename=td[1].text.strip(),
                      teacherid=td[3].text.strip(),
                      teachername=td[4].xpath("./span/text()")[0],
                      capacity=int(td[7].text.strip()),
                      number=int(td[8].text.strip()),
                      restriction=td[10].text.strip() if td[10].text else "")


def canSelect(cinfo):
    if cinfo.restriction:
        return False
    #if cinfo.capacity==0:return False
    #if cinfo.capacity == cinfo.number:
    #    return False
    #if cinfo.capacity < cinfo.number:
    #    return False  # First round selection
    return True


def checkDiffCampus(param, sess):
    r = sess.post(_baseurl + _diffcampus, param)
    if not "没有非本校区课程" in r.text:
        print("Warning: The location of some courses are in another campus")
        print("Course Selection will proceed anyway")
    return


def selectCourse(courses, sess):
    params = {}
    i = 0
    for course in courses:
        if not canSelect(course):
            continue
        params["cids[%d]" % i] = course.courseid
        params["tnos[%d]" % i] = course.teacherid
        i += 1
    for j in range(i, 9):
        params["cids[%d]" % j] = ""
        params["tnos[%d]" % j] = ""
    if (WARN_DIFF_CAMPUS):
        checkDiffCampus(params, sess)
    r = sess.post(_baseurl + _selectcourse, params)
    html = lxml.etree.HTML(r.text)
    table_rows = html.xpath("//table/tr/td/..")
    if len(table_rows) <= 1:
        raise RuntimeWarning("Cannot analyze return results")

    del table_rows[-1]  # 最后一行是 "关闭" 按钮
    result = []
    for tb_item in table_rows:
        tb_datas = tb_item.xpath("td/text()")
        tb_datas = [x.strip() for x in tb_datas]
        if len(tb_datas) == 6:
            item_result = Selectionresult(courseid=tb_datas[1],
                                          coursename=tb_datas[2],
                                          teacherid=tb_datas[3],
                                          teachername=tb_datas[4],
                                          msg=tb_datas[5],
                                          isSuccess="成功" in tb_datas[5])
            result.append(item_result)
        else:
            raise RuntimeError("Cannot analyze return results")
    return result


def isSelectTime(sess):
    r = sess.get(_baseurl + _fastinput)
    if "非本校区提示" in r.text:
        return True
    else:
        return False


def selectTerm(term, sess):
    r = sess.post(_baseurl + _termselect, {"termId": term})
    if "姓名" in r.text:
        print("-------------------------")
    else:
        raise RuntimeError(2, f"Login Failed")
    return sess


def login(username, encryptpwd):
    print("Logging in...")
    session = requests.Session()
    '''
    session.verify = r'./FiddlerRoot.pem'
    session.proxies = {
        "http": "http://127.0.0.1:1452",
        "https": "http:127.0.0.1:1452"
    }'''
    r = session.get(_baseurl)
    '''if r.url.startswith(_baseurl):
        return session'''
    if not r.url.startswith(
            ("https://oauth.shu.edu.cn/", "https://newsso.shu.edu.cn/")):
        raise RuntimeError(1, f"Unexpected Result")
    request_data = {"username": username, "password": encryptpwd}
    r = session.post(r.url, request_data)
    if not r.url.endswith(_termindex):
        raise RuntimeError(2, f"Login Failed")
    else:
        print("Login Successful:" + username)
        print("-------------------------")
        Termlist = getTerms(r.text)
        if len(Termlist) > 1:  # User Selection if exists multiple terms
            print("Available Terms:")
            i = 1
            for tmp in Termlist:
                print(str(i) + ': ' + tmp.name)
                i += 1
            s = 0
            while not (1 <= s <= i - 1):
                s = int(input("Select Term[1-" + str(i - 1) + "]:"))
            print("Selected Term: " + Termlist[s - 1].name)
            return selectTerm(Termlist[s - 1].termid, session)
        else:  # Automatically Select the only term
            print("Selected Term: " + Termlist[0].name)
            return selectTerm(Termlist[0].termid, session)


print("SCourseHelper V1.0")

username = input("User:")
password = getpass.getpass("Password:")

s = login(username, encryptPass(password))
if not isSelectTime(s):
    i = 0
    print("Not Selection Time...Wait %d sec..." % CHK_SELECT_TIME_DELAY)
    while True:
        print("Retry Times: " + str(i), end='\r')
        time.sleep(CHK_SELECT_TIME_DELAY)
        i += 1
        if isSelectTime(s):
            break

print("Selection Time OK")
inputlist = []
inputlist = eval(input("Enter the course list:"))
print("Checking Courses", end="\n\n")
print("-------------------------")
for pair in inputlist:
    if len(Courselist) == 9:
        print("Max 9 items supported, items exceeding limits will be ignored")
        break
    course = getCourseInfo(pair.courseid, pair.teacherid, s)
    Courselist.append(course)
    print("%s(%s) by %s(%s) : %d/%d" %
          (course.coursename, course.courseid, course.teachername,
           course.teacherid, course.number, course.capacity))
print("-------------------------", end="\n\n")
SubmitList = []
i = 0
First = True
while True:
    if First:
        First = False
    else:
        clear()
        print("Retry:%d" % i)
        print("-------------------------")
        for index in range(len(Courselist)):
            course = getCourseInfo(
                course.courseid, course.teacherid, s)  # refresh info
            Courselist[index] = Courselist[index]._replace(
                number=course.number)
            Courselist[index] = Courselist[index]._replace(
                capacity=course.capacity)
            print("%s(%s) by %s(%s) : %d/%d" %
                  (course.coursename, course.courseid, course.teachername,
                   course.teacherid, course.number, course.capacity))
        print("-------------------------", end="\n\n")

    SubmitList.clear()
    for course in Courselist:
        if canSelect(course):
            print("%s(%s) by %s(%s) can be selected!!" %
                  (course.coursename, course.courseid, course.teachername,
                   course.teacherid))
            SubmitList.append(course)
    if len(SubmitList) > 0:
        print("Trying to select the courses above...", end="\n\n")
        result = selectCourse(SubmitList, s)
        for selection in result:
            print("%s(%s) by %s(%s) : %s" %
                  (selection.coursename, selection.courseid,
                   selection.teachername, selection.teacherid, selection.msg))
            if selection.isSuccess or ("已选此课程" in selection.msg) or ("课时冲突" in selection.msg):
                for index, item in enumerate(Courselist):
                    if (item.courseid == selection.courseid) and (
                            item.teacherid == selection.teacherid):
                        break
                else:
                    raise ValueError("Unexpected Result")
                del Courselist[index]
                if "已选此课程" in selection.msg:
                    print(
                        "Please return the course %s manually, and add it again"
                        % selection.coursename)
                if "课时冲突" in selection.msg:
                    print(
                        "Please change courses conflicting with %s manually, and add it again"
                        % selection.coursename)
            print()
        if len(Courselist) == 0:
            print("Task done!")
            break
        else:
            print("%d course(s) remaining...Wait %d sec..." %
                  (len(Courselist), QUERY_DELAY))
    else:
        print("No course can be selected...")
        print("%d course(s) remaining...Wait %d sec..." %
              (len(Courselist), QUERY_DELAY))
    i += 1
    time.sleep(QUERY_DELAY)
