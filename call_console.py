import os
import re

###一些固定常量
contractName = "SmartClassroom" #合约名称
address = "0x243e97e3c2920e0b43fa4a6a6e4b998042ab567d"  #合约位于链上的地址
method_modify = "sendtx" #	修改类方法
method_not_modify = "call" #非修改类方法	
console_address = "D:/git/python-sdk/console.py"   #控制台文件所在位置



def create_student(uid,uname,specialty): 
    return_code =  (os.popen("%s %s %s %s %s %d %s %s" %(console_address,method_modify,contractName,address,"CreateStudent",uid,uname,specialty))).read()
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return return_code
  
def create_teacher(tid,tname):
    return_code = (os.popen("%s %s %s %s %s %d %s" %(console_address,method_modify,contractName,address,"CreateTeacher",tid,tname))).read()
    #result = re.search(r'\((.*),\)',return_code)
    #flag = int(result[1])
    return return_code
  
def query_integral(id):
    return_code = (os.popen("%s %s %s %s %s %d" %(console_address,method_not_modify,contractName,address,"QueryIntegral",id)).read())
    result = re.search(r'\((.*),(.*),(.*),(.*)\)',return_code)
    flag = int(result[1])
    id_ret = int(result[2]) 
    name = result[3]
    specialty = result[4]
    return (flag,id_ret,name,specialty)
    
def modify_student_info(uid,change_info,info,id):
    return_code = (os.popen("%s %s %s %s %s %d %d %s %d" %(console_address,method_modify,contractName,address,"ModifyStudentInfo",uid,change_info,info,id_new)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag
    
def modify_teacher_info(tid,change_info,info,id):
    return_code = (os.popen("%s %s %s %s %s %d %d %s %d" %(console_address,method_modify,contractName,address,"ModifyTeacherInfo",tid,change_info,info,id_new)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag
    
def change_integral_student(uid,value,change_type):
    return_code = (os.popen("%s %s %s %s %s %d %d %s" %(console_address,method_modify,contractName,address,"ChangeIntegral_Student",uid,value,change_type)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag =int(result[1])   
    return flag

def change_integral_teacher(tid,value,change_type):
    return_code = (os.popen("%s %s %s %s %s %d %d %s" %(console_address,method_modify,contractName,address,"ChangeIntegral_Teacher",tid,value,change_type)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])   
    return flag    
    
def delete_student(uid):
    return_code = (os.popen("%s %s %s %s %s %d" %(console_address,method_modify,contractName,address,"DeleteStudent",uid)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag
    
def delete_teacher(tid):
    return_code = (os.popen("%s %s %s %s %s %d" %(console_address,method_modify,contractName,address,"DeleteTeacher",tid)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag
  
def transaction_integral(fromid,toid,value,trans_type):
    return_code = (os.popen("%s %s %s %s %s %d %d %d %s" %(console_address,method_modify,contractName,address,"TransactionIntegral",fromid,toid,value,trans_type)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag
    
def elective_course(uid,courseNo,tid):
    return_code = (os.popen("%s %s %s %s %s %d %d %d" %(console_address,method_modify,contractName,address,"ElectiveCourse",uid,courseNo,tid)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag

def delete_course(uid,courseNo):
    return_code = (os.popen("%s %s %s %s %s %d %d" %(console_address,method_modify,contractName,address,"DeleteCourse",uid,courseNo)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag    

def course_score(uid,courseNo,score):
    return_code = (os.popen("%s %s %s %s %s %d %d %d" %(console_address,method_modify,contractName,address,"CourseScore",uid,courseNo,score)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1]) 
    return flag
 
def query_course(uid):
    return_code = (os.popen("python D:/git/python-sdk/console.py %s %s %s %s %d " %("sendtx","SmartClassroom","0x128e8fd5fbe98de9ede90d3f93271fa8f9688dc7","QueryCourse",uid)).read())
    result =  re.search(r'\(\((.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*)\),\)',return_code)
    flag = int(result[1]) 
    return c[20] 
    
def release_reward(uid,value,url):
    return_code = (os.popen("%s %s %s %s %s %d %d %s" %(console_address,method_modify,contractName,address,"ReleaseReward",uid,value,url)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag

def answer_reward(fromid,toid,value,url):
    return_code = (os.popen("%s %s %s %s %s %d %d %d %s" %(console_address,method_modify,contractName,address,"AnswerReward",fromid,toid,value,url)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag
    
def rate_of_attendance(uid,courseNo,atdn_type):
    return_code = (os.popen("%s %s %s %s %s %d %d %d" %(console_address,method_modify,contractName,address,"RateOfAttendance",uid,courseNo,atdn_type)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag

def scholarship_increasement(uid,inc_type,sch_type,score,cause):
    return_code = (os.popen("%s %s %s %s %s %d %d %d %d %s" %(console_address,method_modify,contractName,address,"ScholarshipIncreasement",uid,inc_type,sch_type,score,cause)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1]) 
    return flag

def query_student_scholarship(uid,sch_type):
    return_code = (os.popen("%s %s %s %s %s %d %d" %(console_address,method_not_modify,contractName,address,"QueryStudentScholarship",uid,sch_type)).read())
    result = re.search(r'\((.*),(.*),(.*),(.*),(.*),(.*)\)',return_code)
    flag = int(result[1])
    m1 = int(result[2])
    m2 = int(result[3])
    m3 = int(result[4])
    m4 = int(result[5])
    m5 = int(result[6])
    return(flag,m1,m2,m3,m4,m5)

def up_courseware(tid,courseNo,courseware_hash):
    return_code = (os.popen("%s %s %s %s %s %d %d %s" %(console_address,method_modify,contractName,address,"UpCourseware",tid,courseNo,cousrwareHash)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])	    
    return flag

def confirmation(courseware_hash):
    return_code = (os.popen("%s %s %s %s %s %s" %(console_address,method_not_modify,contractName,address,"Confirmation",cousrwareHash)).read())
    result = re.search(r'\((.*),(.*),(.*)\)',return_code)
    flag = int(result[1])
    tid = int(result[2])
    courseNo = result[3]  
    return (flag,tid,courseNo)

def modify_courseware_info(courseware_hash,mod_type,info):
    return_code = (os.popen("%s %s %s %s %s %s %d %d" %(console_address,method_modify,contractName,address,"ModifyCoursewareInfo",cousrwareHash,mod_type,info)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag
    
def delete_courseware(courseware_hash):
    return_code = (os.popen("%s %s %s %s %s %s" %(console_address,method_modify,contractName,address,"DeleteCourseware",cousrwareHash)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1]) 
    return flag
    
def like_course(uid,courseNo,tid):
    return_code = (os.popen("%s %s %s %s %s %d %d %d" %(console_address,method_modify,contractName,address,"LikeCourse",uid,courseNo,tid)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])  
    return flag
    
    
def hate_course(uid,courseNo,tid):
    return_code = (os.popen("%s %s %s %s %s %d %d %d" %(console_address,method_modify,contractName,address,"HateCourse",uid,courseNo,tid)).read())
    result = re.search(r'\((.*),\)',return_code)
    flag = int(result[1])
    return flag
    
    
def query_assessment_by_course(tid,courseNo):
    return_code = (os.popen("%s %s %s %s %s %d %d" %(console_address,method_not_modify,contractName,address,"QueryAssessmentByCourse",tid,courseNo)).read())
    result = re.search(r'\((.*),(.*)\)',return_code)
    like_count = int(result[1])
    hate_count = int(result[2])
    if(like_count == -1):
        return (-1,0,0)
    elif(like_count == -2):
        return (-2,0,0)
    else :
        return (0,like_count,hate_count)
        
        
def query_assessment(tid):
    return_code = (os.popen("%s %s %s %s %s %d %d %d" %(console_address,method_not_modify,contractName,address,"QueryAssessment",tid)).read())
    result = re.search(r'\((.*),(.*)\)',return_code)
    like_count = int(result[1])
    hate_count = int(result[2])
    if(like_count == -1):
        return (-1,0,0)
    else :
        return (0,like_count,hate_count)
	
print(query_integral(888))
