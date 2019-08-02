from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_mysqldb import MySQL
from functools import wraps
from os import urandom\

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
        cur.execute('''SELECT * FROM user_list WHERE user_id=%s ''' ,(id,))
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
        login_user(user, remember = 'remember_me' in request.form)
        return redirect(url_for("index"))
    else:
        return render_template('login.html')


# 个人账户信息
@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html')


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
        cur.execute('''UPDATE user_list SET password=%s WHERE user_id=%s ''', (request.form['new-pwd'], current_user.id))
        mysql.connection.commit()
        return render_template('change_password.html', e=0)
    return render_template('change_password.html', e=-1)


# 登出
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# 404错误页面
@app.errorhandler(404)
def page_404(e):
    return render_template('404.html')


# user_login 回调函数
@login_manager.user_loader
def load_user(id):
    return User(id, session['name'], session['type'])

################################# 学生模块 #################################
@app.route("/student_course", methods=["GET", "POST"])
@login_required
@login_type(2)
def student_course():
    cur=mysql.connection.cursor()
    cur.execute('''SELECT * FROM course''')
    rv=cur.fetchall()
    return render_template('student_course.html',course_list=rv)

################################# 管理员模块 #################################
# 添加用户
@app.route("/user_add", methods=["GET", "POST"])
@login_required
@login_type(0)
def user_add():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute('''SELECT user_id FROM user_list WHERE user_id=%s ''',(request.form['id'],))
        rv = cur.fetchall()
        if rv:
            return render_template('user_add.html', e=1)
        else:
            cur.execute('''INSERT INTO user_list (user_id, user_name, user_type, password) VALUES (%s, %s, %s, %s) ''',(request.form['id'], request.form['username'], request.form['type'], request.form['pwd']))
            mysql.connection.commit()
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
        cur.execute('''SELECT user_id FROM user_list WHERE user_id=%s ''',(request.form['id'],))
        rv = cur.fetchall()
        if rv and rv[0]['user_id'] != uid:
            return redirect(url_for('user_edit' ,eq=1, uid=uid))
            #return render_template('user_edit.html', e=1, user=user)
        else:
            cur.execute('''UPDATE user_list SET user_id=%s, user_name=%s, user_type=%s WHERE user_id=%s  ''',(request.form['id'], request.form['username'], request.form['type'], uid,))
            mysql.connection.commit()
            cur.execute('''SELECT * FROM user_list WHERE user_id=%s ''', (request.form['id'],))
            ur = cur.fetchone()
            user = User(ur['user_id'], ur['user_name'], ur['user_type'])
            return redirect(url_for('user_edit', eq=0, uid=ur['user_id']))
    print(request.args.get('eq'))
    return render_template('user_edit.html', e=request.args.get('eq'), user=user)


# 删除用户
@app.route("/user_delete", methods=["GET", "POST"])
@login_required
@login_type(0)
def user_delete():
    uid=request.args.get('user_id')
    cur=mysql.connection.cursor()
    cur.execute('''SELECT * FROM user_list WHERE user_id=%s''',(uid,))
    rv=cur.fetchall()
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
    print(uid)
    if (not uid) or uid == '0' or uid == '':
        return redirect(url_for('user_list'))
    cur = mysql.connection.cursor()
    cur.execute('''DELETE FROM user_list WHERE user_id=%s ''', (uid,))
    mysql.connection.commit()
    return redirect(url_for('user_list'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
