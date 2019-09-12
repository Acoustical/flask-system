from flask import Flask, redirect, url_for, request, session, abort, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_mysqldb import MySQL
from functools import wraps
from os import urandom
import call_console

app = Flask(__name__)

# flask-mysqldb 数据库连接设置
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'flask'
app.config['MYSQL_PASSWORD'] = '9GuuZAJDGuNxmxO0'
app.config['MYSQL_DB'] = 'flask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = urandom(24)

mysql = MySQL(app)

# flask-login 用户登录包
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Access denied.'

login_manager.init_app(app)


# 继承 UserMixind 的 User 类，使用 User(id, name, type) 初始化 User 对象
class User(UserMixin):

    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.type)
        
        
# 课程表生成
def class_form(course_list):
    clform = [
        [[], [], [], [], [], []],
        [[], [], [], [], [], []],
        [[], [], [], [], [], []],
        [[], [], [], [], [], []],
        [[], [], [], [], [], []]
    ]
    print(course_list)
    for cl in course_list:
        i = int(cl['course_time'])
        j = int(cl['course_weekday'])
        clform[i][j].append(cl)
    return clform


# 自定义登录装饰器 使用 @login_type(type) 对视图函数进行登录限制装饰
# type 0 管理员 1 教师 2 学生
def login_type(type):
    def _login_type(func):
        @wraps(func)
        def __login_type(*args, **kargs):
            if current_user.type != type:
                abort(404)
            return func(*args, **kargs)

        return __login_type

    return _login_type


# 主页
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('layout.html')


# 登录页面
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        id = request.form['user_id']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM user_list WHERE user_id=%s ''', (id,))
        user_seen = cur.fetchall()
        if not user_seen:
            return "用户ID输入错误"
        if password != user_seen[0]["password"]:
            return "密码输入错误"
        name = user_seen[0]["user_name"]
        type = user_seen[0]["user_type"]
        session['name'] = name
        session['type'] = type
        user = User(id, name, type)
        login_user(user, remember='remember_me' in request.form)

        #### 定义 jinja2 全局变量 ####
        # 交易变量
        trans = [
            {
                'token_change': +3.00,
                'time': '2019年8月1日 19:32:11',
                'own': '某个用户',
                'info': '我帮他带饭了，他给我转了3积分'
            },
            {
                'token_change': -2.00,
                'time': '2019年8月1日 19:32:11',
                'own': '某个用户',
                'info': '我把他捶了一顿，赔偿他2积分'
            },
            {
                'token_change': +1.50,
                'time': '2019年8月1日 19:32:11',
                'own': '某个用户',
                'info': '卖屁股，赚了1.5积分'
            },
            {
                'token_change': -4.50,
                'time': '2019年8月1日 19:32:11',
                'own': '某个用户',
                'info': '练习时长两年半'
            }
        ]
        if len(trans) <= 4:
            app.config['TRANS'] = trans
        else:
            app.config['TRANS'] = trans[0:4]
        app.config['TOKEN'] = call_console.query_integral(int(current_user.id))[0]
        #### 停止定义 ####

        return redirect(url_for("index"))
    else:
        return render_template('login.html')


# 课程详情页及课程评价
@app.route('/course_info/<int:cid>', methods=["GET", "POST"])
@login_required
def course_info(cid):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course WHERE course_id = %s ''',(cid,))
    c = cur.fetchall()
    if not c:
        abort(404)
        return '404'
    course_1 = c[0]
    cur.execute('''SELECT * FROM course_student WHERE course_id = %s ''',(cid,))
    c = cur.fetchall()
    if not c:
        abort(404)
        return '404'
    course_2 = c[0]
    course = {**course_1, **course_2}
    course['student_num'] = len(course['student_ids'].split('#'))-2
    if course['student_num'] < 0:
        course['student_num'] = 0
    c_liked = course['course_liked'].split('#')
    if str(current_user.id) in c_liked:
        course['not_liked'] = 0
    else:
        course['not_liked'] = 1
    cur.execute('''SELECT user_name FROM user_list WHERE user_id = %s ''', (course['course_teacher'],))
    tc = cur.fetchall()
    course['course_teacher_name'] = tc[0]['user_name']

    # 从底层获取
    temp = call_console.query_assessment_by_course(int(course['course_teacher']),int(cid))
    course['likes'] = temp[1]
    course['unlikes'] = temp[2]

    cur.execute('''SELECT * FROM course_comments WHERE course_id = %s ''',(cid,))
    cs = cur.fetchall()
    for c in cs:
        cur.execute('''SELECT user_name FROM user_list WHERE user_id = %s ''',(c['user_id'],))
        un = cur.fetchall()
        c['username'] = un[0]['user_name']
    return render_template('course_info.html', course=course, comments=cs)




# 个人账户信息
@app.route("/profile")
@login_required
def profile():
    #cur = mysql.connection.cursor()
    #cur.execute('''SELECT * FROM module_score WHERE user_id=%s ''', (current_user.id,))
    #rv = cur.fetchall()
    temp = call_console.query_student_scholarship(int(current_user.id),1)
    #print(temp[2])
    #print(temp[3])
    
    
    rv = [{'user_id':current_user.id,'term_no':1,'module_one':temp[1],'module_two':temp[2],'module_three':temp[3],'module_four':temp[4],'module_five':temp[5]}]
    return render_template('profile.html', module_list=rv)
    
    
    
    
# 输入查询用户id
@app.route("/user_query", methods=["GET", "POST"])
@login_required
def user_query():
    if request.method == 'POST':
        return redirect(url_for('user_info', uid=request.form['id']))

    return render_template('user_query.html')





# 查询用户信息
@app.route("/user_info/<int:uid>", methods=["GET", "POST"])
@login_required
def user_info(uid):
    if uid == 0:
        abort(404)
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM user_list WHERE user_id=%s ''', (uid,))
    ur = cur.fetchone()
    #temp = call_console.query_integral(uid)
    user = User(ur['user_id'], ur['user_name'], ur['user_type'])
    temp = call_console.query_student_scholarship(int(ur['user_id']),1)
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course WHERE course_teacher=%s ''', (uid,))
    rv = cur.fetchall()
    return render_template('user_info.html', user=user, course_list=rv,temp = temp)


# 修改密码
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute('''SELECT password FROM user_list WHERE user_id=%s ''', (current_user.id,))
        pwd = cur.fetchall()
        if request.form['old-pwd'] != pwd[0]['password']:
            return render_template('change_password.html', e=1)
        if request.form['new-pwd'] != request.form['new2-pwd']:
            return render_template('change_password.html', e=2)
        cur.execute('''UPDATE user_list SET password=%s WHERE user_id=%s ''',
                    (request.form['new-pwd'], current_user.id))
        mysql.connection.commit()
        return render_template('change_password.html', e=0)
    return render_template('change_password.html', e=-1)


# 登出
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# 积分详细信息
@app.route("/transition")
@login_required
def transition():
    # current_user
    ##### 此处待调用区块链底层接口 #####
    trans = [
        {
            'token_change': +3.00,
            'time': '2019年8月1日 19:32:11',
            'own': '某个用户',
            'info': '我帮他带饭了，他给我转了3积分'
        },
        {
            'token_change': -2.00,
            'time': '2019年8月1日 19:32:11',
            'own': '某个用户',
            'info': '我把他捶了一顿，赔偿他2积分'
        },
        {
            'token_change': +1.50,
            'time': '2019年8月1日 19:32:11',
            'own': '某个用户',
            'info': '卖屁股，赚了1.5积分'
        },
        {
            'token_change': -4.50,
            'time': '2019年8月1日 19:32:11',
            'own': '某个用户',
            'info': '练习时长两年半'
        }
    ]
    return render_template('transition.html', trans=trans)


# 404错误页面
@app.errorhandler(404)
def page_404(e):
    return render_template('404.html')


# user_login 回调函数
@login_manager.user_loader
def load_user(id):
    return User(id, session['name'], session['type'])


################################# 学生模块 #################################
# 学生选课
@app.route("/student_course", methods=["GET", "POST"])
@login_required
@login_type(2)
def student_course():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course''')
    course_list = cur.fetchall()
    for r in course_list:
        cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s ''', (r['course_teacher'],))
        rvv = cur.fetchall()
        if rvv:
            r['course_teacher_name'] = rvv[0]['user_name']
        else:
            r['course_teacher_name'] = 'Null'
    if request.method == 'POST':
        course_form = request.form.to_dict()
        course_ids = course_form.keys()
        for cid in course_ids:
            rmix = []
            for r in course_list:
                rmix.append(r['course_id'])
            if int(cid) not in rmix:
                # return '错误页，找不到课程'
                return render_template('404.html')
            cur.execute('''SELECT student_ids FROM course_student WHERE course_id=%s ''', (cid,))
            course = cur.fetchone()

            sts = course['student_ids'].split('#')
            if str(current_user.id) in sts:
                # return redirect(url_for('student_result',e=1))
                return render_template('student_course.html', course_list=course_list, e=1)  # 重复选课

            course_st = course['student_ids']
            course_st += current_user.id + '#'
            cur.execute('''UPDATE course_student SET student_ids=%s WHERE course_id=%s ''', (course_st, cid,))
            mysql.connection.commit()
        return render_template('student_course.html', course_list=course_list, e=0)  # 选课成功
    return render_template('student_course.html', course_list=course_list, e=-1)  # 正常选课界面


# 选课结果
@app.route("/student_result")
@login_required
@login_type(2)
def student_result():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course_student''')
    rv = cur.fetchall()
    clist = []
    for cs in rv:
        css = cs['student_ids'].split('#')
        if str(current_user.id) in css:
            cur.execute('''SELECT * FROM course WHERE course_id = %s ''', (cs['course_id'],))
            cl = cur.fetchone()
            cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s ''', (cl['course_teacher'],))
            rvv = cur.fetchall()
            if rvv:
                cl['course_teacher_name'] = rvv[0]['user_name']
            else:
                cl['course_teacher_name'] = 'Null'
            clist.append(cl)
    return render_template('student_result.html', course_list=clist)


# 删除选课
@app.route("/course_delete", methods=["GET", "POST"])
@login_required
@login_type(2)
def course_delete():
    cid = request.args.get('course_id')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course WHERE course_id=%s''', (cid,))
    rv = cur.fetchall()
    if rv:
        cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s ''', (rv[0]['course_teacher'],))
        rvv = cur.fetchall()
        if rvv:
            rv[0]['course_teacher_name'] = rvv[0]['user_name']
        else:
            rv[0]['course_teacher_name'] = 'Null'

        return render_template('course_delete.html', course=rv[0])
    else:
        return redirect(url_for('index'))


# 删除选课
@app.route("/course_cut", methods=["GET", "POST"])
@login_required
@login_type(2)
def course_cut():
    cid = request.args.get('course_id')
    if (not cid) or cid == '':
        return redirect(url_for('student_result'))
    cur = mysql.connection.cursor()
    cur.execute('''SELECT student_ids FROM course_student WHERE course_id=%s ''', (cid,))
    course = cur.fetchone()

    course_st = course['student_ids']
    # repl=current_user.id +'#'
    # course_st = course_st.replace(repl, '')
    sts = course_st.split('#')
    sts.remove(current_user.id)
    course_st = "#".join(i for i in sts)
    cur.execute('''UPDATE course_student SET student_ids=%s WHERE course_id=%s ''', (course_st, cid,))
    mysql.connection.commit()
    return redirect(url_for('student_result'))



# 课程表
@app.route("/student_result_form")
@login_required
@login_type(2)
def student_result_form():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course_student''')
    rv = cur.fetchall()
    clist = []
    for cs in rv:
        css = cs['student_ids'].split('#')
        if str(current_user.id) in css:
            cur.execute('''SELECT * FROM course WHERE course_id = %s ''', (cs['course_id'],))
            cl = cur.fetchone()
            cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s ''', (cl['course_teacher'],))
            rvv = cur.fetchall()
            if rvv:
                cl['course_teacher_name'] = rvv[0]['user_name']
            else:
                cl['course_teacher_name'] = 'Null'
            clist.append(cl)
    cf = class_form(clist)
    return render_template('student_form.html', course_form=cf)



# 问题悬赏列表
@app.route("/question_list", methods=["GET", "POST"])
@login_required
def question_list():
    app.config['TOKEN'] = call_console.query_integral(int(current_user.id))[0]
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM question''')
    rv = cur.fetchall()
    for r in rv:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s''', (r['student_id'],))
        rvv = cur.fetchall()
        if rvv:
            r['student_name'] = rvv[0]['user_name']
        else:
            r['student_name'] = 'NULL'

    return render_template('question_list.html', question_list=rv)


# 问题悬赏详情
@app.route("/question_info", methods=["GET", "POST"])
@login_required
def question_info():
    app.config['TOKEN'] = call_console.query_integral(int(current_user.id))[0] 
    e = int(request.args.get('e'))
    qid = request.args.get('id')
    f = request.args.get('f')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM question WHERE question_id=%s ''', (qid,))
    rv = cur.fetchall()
    if rv:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s''', (rv[0]['student_id'],))
        rvv = cur.fetchall()
        if rvv:
            rv[0]['student_name'] = rvv[0]['user_name']
        else:
            rv[0]['student_name'] = 'NULL'
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM answer_list WHERE question_id=%s''', (qid,))
    mv = cur.fetchall()
    if mv:
        for m in mv:
            cur = mysql.connection.cursor()
            cur.execute('''SELECT user_name,user_type FROM user_list WHERE user_id=%s''', (m['answer_id'],))
            mvv = cur.fetchall()
            if rvv:
                m['answer_type'] = mvv[0]['user_type']
                m['answer_name'] = mvv[0]['user_name']
            else:
                m['answer_type'] = 'NULL'
                m['answer_name'] = 'NULL'
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO answer_list (question_id, answer_id, answer_info) VALUES (%s, %s, %s) ''',
                    (qid, current_user.id, request.form['answer_info']))
        mysql.connection.commit()
        return redirect(url_for('question_info', id=qid, e=e, f=1))

    return render_template('question_info.html', question=rv[0], e=e, mv=mv, f=f)


# 我的问题悬赏
@app.route("/question_my", methods=["GET", "POST"])
@login_required
@login_type(2)
def question_my():
    app.config['TOKEN'] = call_console.query_integral(int(current_user.id))[0]
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM question WHERE student_id=%s''', (current_user.id,))
    rv = cur.fetchall()
    if rv:
        for r in rv:
            cur = mysql.connection.cursor()
            cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s''', (r['student_id'],))
            rvv = cur.fetchall()
            if rvv:
                r['student_name'] = rvv[0]['user_name']
            else:
                r['student_name'] = 'NULL'
        return render_template('question_my.html', e=0, question_list=rv)
    else:
        return render_template('question_my.html', e=1, question_list=rv)


# 发布新的悬赏
@app.route("/question_add", methods=["GET", "POST"])
@login_required
@login_type(2)
def question_add():
    app.config['TOKEN'] = call_console.query_integral(int(current_user.id))[0]
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM question WHERE question_id=%s ''',
                    (request.form['question_id'],))
        rv = cur.fetchall()
        if rv:
            return render_template("question_add.html", e=1)
        else:
            cur.execute(
                '''INSERT INTO question (question_id,student_id, question_intro, token, status, question_info) VALUES (%s, %s, %s, %s, %s,%s)''',
                (request.form['question_id'], current_user.id, request.form['question_intro'], request.form['token'], 0,
                 request.form['question_info']))
            mysql.connection.commit()
            call_console.release_reward(int(current_user.id),int(request.form['token']),'/question_list')
            temp = call_console.query_integral(int(current_user.id))
            print(temp)
            app.config['TOKEN'] =  temp[0]
            return render_template("question_add.html", e=0)

    return render_template("question_add.html", e=-1)


# 修改我的悬赏
@app.route("/question_my_edit", methods=["GET", "POST"])
@login_required
@login_type(2)
def question_my_edit():
    qid = request.args.get('id')
    e = request.args.get('eq')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM question WHERE question_id=%s''', (qid,))
    rv = cur.fetchall()
    if rv:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s''', (rv[0]['student_id'],))
        rvv = cur.fetchall()
        if rvv:
            rv[0]['student_name'] = rvv[0]['user_name']
        else:
            rv[0]['student_name'] = 'NULL'
    if request.method == 'POST':
        cur.execute(
            '''UPDATE question SET  status=%s, question_info=%s WHERE question_id=%s ''',
            (request.form['status'], request.form['question_info'], qid,))
        mysql.connection.commit()
        return redirect(url_for('question_my_edit', id=qid, eq=0))
    return render_template('question_my_edit.html', question=rv[0], e=e)


# 完成悬赏
@app.route("/question_commit", methods=["GET", "POST"])
@login_required
def question_commit():
    faid = int(request.args.get('faid'))
    shouid = request.args.get('shouid')
    token = request.args.get('token')
    print(faid)
    print(shouid)
    print(token)
    call_console.answer_reward(int(faid),int(shouid),int(token),'/question_list')
    return redirect(url_for('question_list', ))

@app.route('/likes/<int:cid>')
@login_required
@login_type(2)
def likes(cid):
 tid = request.args.get('tid')
 sid = request.args.get('sid')
 print(sid,cid,tid)
 call_console.like_course(int(sid),int(cid),int(tid))
 
 # 给cid课程号点赞
 app.config['TOKEN'] = call_console.query_integral(int(current_user.id))[0]
 return(redirect(url_for('course_info', cid=cid)))
 
 
@app.route('/unlikes/<int:cid>')
@login_required
@login_type(2)
def unlikes(cid):
 tid = request.args.get('tid')
 sid = request.args.get('sid')
 # 给cid课程号点踩
 call_console.hate_course(int(sid),int(cid),int(tid))
 return(redirect(url_for('course_info', cid=cid)))




################################# 教师模块 #################################
# 上传课题
@app.route('/teacher_course_update', methods=["GET", "POST"])
@login_required
@login_type(1)
def teacher_course_update():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute(
            '''INSERT INTO course (course_id, course_name, course_teacher, course_weekday, course_time, course_total, course_credit, course_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (
                request.form['course_id'],
                request.form['course_name'],
                current_user.id,
                request.form['course_weekday'],
                request.form['course_time'],
                request.form['course_total'],
                request.form['course_credit'],
                request.form['course_info'],
            )
        )
        mysql.connection.commit()
        cur.execute(
            '''INSERT INTO course_student (course_id, student_ids,course_status,course_liked) VALUES (%s, %s,%s,%s)''',
            (
                request.form['course_id'],
                '#',
                0, '#'
            )
        )
        mysql.connection.commit()
    return render_template("teacher_course_update.html")


# 课程结果
@app.route('/teacher_course_list')
@login_required
@login_type(1)
def teacher_course_list():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course WHERE course_teacher=%s ''', (current_user.id,))
    rv = cur.fetchall()
    return render_template('teacher_course_list.html', course_list=rv)


# 编辑课程信息
@app.route("/teacher_course_edit/<int:cid>", methods=["GET", "POST"])
@login_required
@login_type(1)
def teacher_course_edit(cid):
    # uid = request.args.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course WHERE course_id=%s ''', (cid,))
    cr = cur.fetchone()
    if request.method == 'POST':
        cur.execute('''SELECT course_id FROM course WHERE course_id=%s ''', (request.form['course_id'],))
        rv = cur.fetchall()
        if rv and rv[0]['course_id'] != cid:
            return redirect(url_for('teacher_course_edit', eq=1, cid=cid))
            # return render_template('user_edit.html', e=1, user=user)
        else:
            cur.execute(
                '''UPDATE course SET course_id=%s, course_name=%s, course_weekday=%s, course_time=%s, course_total=%s, course_credit=%s, course_info=%s WHERE course_id=%s  ''',
                (request.form['course_id'], request.form['course_name'], request.form['course_weekday'],
                 request.form['course_time'], request.form['course_total'], request.form['course_credit'],
                 request.form['course_info'], cid,))
            mysql.connection.commit()
            cur.execute('''SELECT * FROM course WHERE course_id=%s ''', (request.form['course_id'],))
            cr = cur.fetchone()
            return redirect(url_for('teacher_course_edit', eq=0, cid=cr['course_id']))
    return render_template('teacher_course_edit.html', e=request.args.get('eq'), course=cr)


# 删除已发起课程
@app.route("/teacher_course_delete", methods=["GET", "POST"])
@login_required
@login_type(1)
def teacher_course_delete():
    cid = request.args.get('course_id')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course WHERE course_id=%s''', (cid,))
    rv = cur.fetchall()
    if rv:
        return render_template('teacher_course_delete.html', course=rv[0])
    else:
        return redirect(url_for('index'))


# 执行删除操作
@app.route("/teacher_course_cut", methods=["GET", "POST"])
@login_required
@login_type(1)
def teacher_course_cut():
    cid = request.args.get('course_id')
    if (not cid) or cid == '':
        return redirect(url_for('teacher_course_list'))
    cur = mysql.connection.cursor()
    cur.execute('''DELETE FROM course WHERE course_id=%s ''', (cid,))
    mysql.connection.commit()
    return redirect(url_for('teacher_course_list'))

# 课程表
@app.route('/teacher_course_form')
@login_required
@login_type(1)
def teacher_course_form():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course WHERE course_teacher=%s ''', (current_user.id,))
    rv = cur.fetchall()
    cf = class_form(rv)
    return render_template('student_form.html', course_form=cf)



################################# 管理员模块 #################################
# 添加用户
@app.route("/user_add", methods=["GET", "POST"])
@login_required
@login_type(0)
def user_add():
    app.config['TOKEN'] = 0
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute('''SELECT user_id FROM user_list WHERE user_id=%s ''', (request.form['id'],))
        rv = cur.fetchall()
        if rv:
            return render_template('user_add.html', e=1)
        else:
            cur.execute('''INSERT INTO user_list (user_id, user_name, user_type, password) VALUES (%s, %s, %s, %s) ''',
                        (request.form['id'], request.form['username'], request.form['type'], request.form['pwd']))
            mysql.connection.commit()
            if request.form['type'] == 2:
                
                call_console.create_student(int(request.form['id']), request.form['username'], '网络空间安全')
            else:
                call_console.create_teacher(int(request.form['id']), request.form['username'])
            return render_template('user_add.html', e=0)
    return render_template('user_add.html', e=-1)


# 用户列表
@app.route("/user_list")
@login_required
@login_type(0)
def user_list():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM user_list ''')
    rv = cur.fetchall()
    return render_template('user_list.html', user_list=rv)


# 编辑用户
@app.route("/user_edit/<int:uid>", methods=["GET", "POST"])
@login_required
@login_type(0)
def user_edit(uid):
    # uid = request.args.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM user_list WHERE user_id=%s ''', (uid,))
    ur = cur.fetchone()
    user = User(ur['user_id'], ur['user_name'], ur['user_type'])
    if request.method == 'POST':
        cur.execute('''SELECT user_id FROM user_list WHERE user_id=%s ''', (request.form['id'],))
        rv = cur.fetchall()
        if rv and rv[0]['user_id'] != uid:
            return redirect(url_for('user_edit', eq=1, uid=uid))
            # return render_template('user_edit.html', e=1, user=user)
        else:
            cur.execute('''UPDATE user_list SET user_id=%s, user_name=%s, user_type=%s WHERE user_id=%s  ''',
                        (request.form['id'], request.form['username'], request.form['type'], uid,))
            mysql.connection.commit()
            cur.execute('''SELECT * FROM user_list WHERE user_id=%s ''', (request.form['id'],))
            ur = cur.fetchone()
            user = User(ur['user_id'], ur['user_name'], ur['user_type'])
            return redirect(url_for('user_edit', eq=0, uid=ur['user_id']))
    return render_template('user_edit.html', e=request.args.get('eq'), user=user)


# 删除用户
@app.route("/user_delete", methods=["GET", "POST"])
@login_required
@login_type(0)
def user_delete():
    uid = request.args.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM user_list WHERE user_id=%s''', (uid,))
    rv = cur.fetchall()
    if rv:
        return render_template('user_delete.html', user=rv[0])
    else:
        return redirect(url_for('index'))



# 删除用户
@app.route("/user_cut", methods=["GET", "POST"])
@login_required
@login_type(0)
def user_cut():
    uid = request.args.get('user_id')
    if (not uid) or uid == '0' or uid == '':
        return redirect(url_for('user_list'))
    cur = mysql.connection.cursor()
    cur.execute('''DELETE FROM user_list WHERE user_id=%s ''', (uid,))
    mysql.connection.commit()
    return redirect(url_for('user_list'))


# 课程列表
@app.route("/manager_course_list")
@login_required
@login_type(0)
def manager_course_list():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course''')
    course_list = cur.fetchall()
    for r in course_list:
        cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s ''', (r['course_teacher'],))
        rvv = cur.fetchall()
        if rvv:
            r['course_teacher_name'] = rvv[0]['user_name']
        else:
            r['course_teacher_name'] = 'Null'
    for r in course_list:
        cur.execute('''SELECT course_status FROM course_student WHERE course_id=%s''', (r['course_id'],))
        rvv = cur.fetchall()
        if rvv:
            r['course_status'] = rvv[0]['course_status']
        else:
            r['course_status'] = 'NULL'
    return render_template('manager_course_list.html', course_list=course_list)


# 编辑课程状态
@app.route("/manager_course_edit/<int:cid>", methods=["GET", "POST"])
@login_required
@login_type(0)
def manager_course_edit(cid):
    # cid = request.args.get('cid')
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM course WHERE course_id=%s''', (cid,))
    rv = cur.fetchall()

    if rv:
        cur.execute('''SELECT user_name FROM user_list WHERE user_id=%s ''', (rv[0]['course_teacher'],))
        rvv = cur.fetchall()
        if rvv:
            rv[0]['course_teacher_name'] = rvv[0]['user_name']
        else:
            rv[0]['course_teacher_name'] = 'Null'
        cur.execute('''SELECT course_status FROM course_student WHERE course_id=%s''', (rv[0]['course_id'],))
        rvv = cur.fetchall()
        if rvv:
            rv[0]['course_status'] = rvv[0]['course_status']
        else:
            rv[0]['course_status'] = 'NULL'

        if request.method == 'POST':
            if request.form['course_status'] == '-1' or request.form['course_status'] == '0' or request.form[
                'course_status'] == '-2':
                cur.execute('''UPDATE course_student SET course_status=%s WHERE course_id=%s  ''',
                            (request.form['course_status'], cid))
                mysql.connection.commit()
            if request.form['course_status'] == '1':
                cur.execute('''UPDATE course_student SET course_status=%s WHERE course_id=%s  ''',
                            (request.form['course_counter'], cid,))
                mysql.connection.commit()
            return redirect(url_for('manager_course_list'))

        return render_template('manager_course_edit.html', course=rv[0])
    else:
        return redirect(url_for('index'))


# 给学生增加模块分
@app.route("/module_score_add", methods=["GET", "POST"])
@login_required
@login_type(0)
def module_score_add():
    app.config['TOKEN'] = 0
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM module_score WHERE user_id=%s AND term_no=%s ''',
                    (request.form['student_id'], request.form['term_no']))
        rv = cur.fetchall()
        if rv:
            if request.form['module_no'] == '1':
                score = int(rv[0]['module_one']) + int(request.form['score_add'])
                cur = mysql.connection.cursor()
                cur.execute('''UPDATE module_score SET module_one=%s WHERE user_id=%s AND term_no=%s   ''',
                            (score, request.form['student_id'], request.form['term_no']))
                mysql.connection.commit()
            if request.form['module_no'] == '2':
                score = int(rv[0]['module_two']) + int(request.form['score_add'])
                cur = mysql.connection.cursor()
                cur.execute('''UPDATE module_score SET module_two=%s WHERE user_id=%s AND term_no=%s   ''',
                            (score, request.form['student_id'], request.form['term_no']))
                mysql.connection.commit()
            if request.form['module_no'] == '3':
                score = int(rv[0]['module_three']) + int(request.form['score_add'])
                cur = mysql.connection.cursor()
                cur.execute('''UPDATE module_score SET module_three=%s WHERE user_id=%s AND term_no=%s   ''',
                            (score, request.form['student_id'], request.form['term_no']))
                mysql.connection.commit()
            if request.form['module_no'] == '4':
                score = int(rv[0]['module_four']) + int(request.form['score_add'])
                cur = mysql.connection.cursor()
                cur.execute('''UPDATE module_score SET module_four=%s WHERE user_id=%s AND term_no=%s   ''',
                            (score, request.form['student_id'], request.form['term_no']))
                mysql.connection.commit()
            if request.form['module_no'] == '5':
                score = int(rv[0]['module_five']) + int(request.form['score_add'])
                cur = mysql.connection.cursor()
                cur.execute('''UPDATE module_score SET module_five=%s WHERE user_id=%s AND term_no=%s   ''',
                            (score, request.form['student_id'], request.form['term_no']))
                mysql.connection.commit()
        call_console.scholarship_increasement(int(request.form['student_id']),1,1,int(request.form['score_add']),"test1")
        return redirect(url_for('module_score_add', eq=0))
    return render_template('module_score_add.html', e=request.args.get('eq'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
