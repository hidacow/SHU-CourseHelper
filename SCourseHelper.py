import base64
import configparser
import getpass
import time
from collections import namedtuple
import lxml.etree
from os import system, name
import requests
import rsa



# Settings
query_delay = 1.5
chk_select_time_delay = 5
warn_diff_campus = True
CONFIGPATH="courses.txt"

# Variables
Termlist = []
Courselist = []
inputlist=[]
username=""
password=""
encryptedpassword=""
sterm=0

# Declaration
Termitem = namedtuple("Term", ["termid", "name"])
Courseinfo = namedtuple("CourseInfo", ["courseid", "coursename", "teacherid", "teachername", "capacity", "number","restriction"])
Courseitem = namedtuple("CourseItem", ["courseid", "teacherid"])
Selectionresult = namedtuple("SelectionResult",["courseid", "coursename", "teacherid", "teachername", "msg", "isSuccess"])

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
_baseerror = "Base/Error"

# SSO Pubkey
_keystr = '''-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OLOU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plWf5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSRwTBNePOk1H+LRQokgQIDAQAB
    -----END PUBLIC KEY-----'''

def initconfig():   #write a default config
    config=configparser.ConfigParser(allow_no_value=True)
    config["Userinfo"]={}
    config["Userinfo"]["user"]=""
    config["Userinfo"]["password"]=""
    config["Userinfo"]["encryptpassword"]=""
    config["Settings"]={}
    config["Settings"]["term"]=""
    config["Settings"]["querydelay"]="1.5"
    config["Settings"]["checkselectdelay"]="5"
    config["Settings"]["warndiffcampus"]="1"
    config["Courses"]={}
    for i in range(1,10):
        config["Courses"]["course%d"%i]=""
    
    try:
        with open(CONFIGPATH, 'w') as configfile:
            config.write(configfile,space_around_delimiters=False)
        print("Default config file is saved")
    except:
        print("Unable to initialize config")

def readconfig():   #read config from file
    config=configparser.ConfigParser(allow_no_value=True)
    try:
        config.read(CONFIGPATH)
        userinfo=config["Userinfo"]
        settings=config["Settings"]
    except KeyError:
        print("Warning: Config is corrupted")
        initconfig()
        return
    courses=config["Courses"]
    global username,password,encryptedpassword,sterm,query_delay,chk_select_time_delay,warn_diff_campus,inputlist #use global in order to modify global values
    username=userinfo.get("user","")
    password=userinfo.get("password","")
    encryptedpassword=userinfo.get("encryptpassword","")
    sterm=settings.get("term","")
    try:
        query_delay = float(settings.get("querydelay","1.5"))
    except:
        print("Warning: config of querydelay is invalid, set to default..")
        query_delay = 1.5
    try:
        chk_select_time_delay = float(settings.get("checkselectdelay","5"))
    except:
        print("Warning: config of checkselectdelay is invalid, set to default..")
        chk_select_time_delay = 5
    try:
        warn_diff_campus = bool(int(settings.get("warndiffcampus","1")))
    except:
        print("Warning: config of warndiffcampus is invalid, set to default..")
        warn_diff_campus = True
    
    for i in range(1,10):
        s=courses.get("course%d"%i,"")
        if s!="":
            a=s.split(",")
            if len(a)!=2 or len(a[0])!=8 or len(a[1])!=4:
                print(s+" is not a valid course format")
            else:
                inputlist.append(Courseitem._make(s.split(",")))
        
def writeepwd():    #write encrypted password to config
    config=configparser.ConfigParser(allow_no_value=True)
    config.read(CONFIGPATH)
    config["Userinfo"]["user"]=username
    config["Userinfo"]["encryptpassword"]=encryptedpassword
    config["Userinfo"]["password"]=""
    try:
        with open(CONFIGPATH, 'w') as configfile:
            config.write(configfile,space_around_delimiters=False)
    except:
        print("Error: Unable to write config")

def writeterm():    #write current termid to config
    config=configparser.ConfigParser(allow_no_value=True)
    config.read(CONFIGPATH)
    config["Settings"]["term"]=sterm
    try:
        with open(CONFIGPATH, 'w') as configfile:
            config.write(configfile,space_around_delimiters=False)
    except:
        print("Error: Unable to write config")


def clear():    #cross-platform clear screen function
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

def getTerms(text): #analyze terms from text
    html = lxml.etree.HTML(text)
    termslist = html.xpath("//table/tr[@name='rowterm']")
    terms = []
    for term in termslist:
        termid = term.attrib["value"]
        name = term.xpath("./td/text()")[0].strip()
        terms.append(Termitem(termid, name))
    return terms

def deletecoursefromlist(cid,tid):  #delete an item from list
    global Courselist
    for index, item in enumerate(Courselist):
        if (item.courseid == cid) and (item.teacherid == tid):
            break
        else:
            raise ValueError("Unexpected Result")
    del Courselist[index]

def getCourseInfo(cid, tid, sess):  #query course info by cid and tid
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


def canSelect(cinfo):   #judge whether a course can be selected
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


def returnCourse(course, sess): #return one course at a time
    params = {}
    params["cids"] = course.courseid
    params["tnos"] = course.teacherid
    r = sess.post(_baseurl + _dropcourse, params)
    return ("退课成功" in r.text)


def selectCourse(courses, sess):    #select a list of courses
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
    if warn_diff_campus:
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


def isSelectTime(sess): #judge whether it is selection time
    r = sess.get(_baseurl + _fastinput)
    if "非本校区提示" in r.text:
        return True
    else:
        return False


def selectTerm(term, sess): #select the term
    global sterm
    sterm=term
    r = sess.post(_baseurl + _termselect, {"termId": term})
    if "姓名" in r.text:
        print("-------------------------")
    else:
        raise RuntimeError(2, f"Login Failed")
    writeterm()
    print("Term info has been saved, to change it or select again, please delete the value in config file",end="\n\n")
    return sess


def login(username, encryptpwd):
    print("Logging in...")
    session = requests.Session()
    r = session.get(_baseurl)

    if not r.url.startswith(
            ("https://oauth.shu.edu.cn/", "https://newsso.shu.edu.cn/")):
        raise RuntimeError(1, f"Unexpected Result")
    request_data = {"username": username, "password": encryptpwd}
    r = session.post(r.url, request_data)
    if not r.url.endswith(_termindex):
        if "too many requests" in r.text:
            raise RuntimeError(2,f"Too many Requests, try again later")
        raise RuntimeError(2, f"Login Failed")
    else:
        print("Login Successful:" + username)
        global encryptedpassword
        if encryptedpassword=="":
            tmp=input("Do you want to save encrypted credentials in config?[Y/N]:")
            while True:
                if tmp=="Y" or tmp=="y":
                    encryptedpassword=encryptPass(password)
                    writeepwd()
                    break
                else:
                    if tmp=="N" or tmp=="n":
                        break
                    else:
                        tmp=input("Please enter ""Y"" or ""N"" :")
        print("-------------------------")
        Termlist = getTerms(r.text)
        if len(Termlist) > 1:  # User Selection if exists multiple terms
            print("Available Terms:")
            i = 1
            for tmp in Termlist:
                print(str(i) + ': ' + tmp.name)
                if tmp.termid==sterm:
                    print("Selected Term: " + tmp.name)
                    return selectTerm(sterm, session)
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
print()

readconfig()
print()
if username=="":
    username = input("User:")
else:
    print("User:%s"%username)
if password=="" and encryptedpassword=="":
    password = getpass.getpass("Password:")

if encryptedpassword!="":
    s = login(username, encryptedpassword)
else:
    s = login(username, encryptPass(password))




if not isSelectTime(s):
    i = 0
    print("Not Selection Time...Wait %.2f sec..." % chk_select_time_delay)
    while True:
        print("Retry Times: " + str(i), end='\r')
        time.sleep(chk_select_time_delay)
        i += 1
        if isSelectTime(s):
            break

print("Selection Time OK",end="\n\n")
if len(inputlist)==0:
    #inputlist = eval(input("Enter the course list:"))
    i=1
    print("Please enter the info of courses, enter nothing to finish")
    while i<10:
        a=input("Enter the course  id of course %d :"%i)
        
        if (a==""):
            if i>1:
                break
            else:
                print("You must enter at least 1 course")
                continue
        if(len(a)!=8):
            print("Invalid input, please enter again")
            continue
        b=input("Enter the teacher id of course %d :"%i)

        if (b==""):
            if i>1:
                break
            else:
                print("incomplete information, please enter again")
                continue
        if(len(b)!=4):
            print("Invalid input, please enter again")
            continue
        inputlist.append(Courseitem(a,b))
        i+=1
    
print("Checking %d Courses"%len(inputlist), end="\n\n")
print("-------------------------")
for pair in inputlist:
    if len(Courselist) == 9:
        print("Max 9 items supported, items exceeding limits will be ignored")
        break
    course = getCourseInfo(pair.courseid, pair.teacherid, s)
    Courselist.append(course)
    print("%s(%s) by %s(%s) : %d/%d %s" %
          (course.coursename, course.courseid, course.teachername,
           course.teacherid, course.number, course.capacity, course.restriction))
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
            print("%s(%s) by %s(%s) : %d/%d %s" %
                  (course.coursename, course.courseid, course.teachername,
                   course.teacherid, course.number, course.capacity, course.restriction))
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
                deletecoursefromlist(selection.courseid,selection.teacherid)
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
            print("%d course(s) remaining...Wait %.2f sec..." %
                  (len(Courselist), query_delay))
    else:
        print("No course can be selected...")
        print("%d course(s) remaining...Wait %.2f sec..." %
              (len(Courselist), query_delay))
    i += 1
    time.sleep(query_delay)
