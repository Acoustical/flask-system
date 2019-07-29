from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_mysqldb import MySQL
from os import urandom

app = Flask(__name__)

# flask-mysqldb
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'flask'
app.config['MYSQL_PASSWORD'] = '9GuuZAJDGuNxmxO0'
app.config['MYSQL_DB'] = 'flask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = urandom(24)

mysql = MySQL(app)

# flask-login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Access denied.'

login_manager.init_app(app)


# silly user model
class User(UserMixin):

    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.type)


# some protected url
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('layout.html')


# login
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


@app.route("/profile")
def profile():
    return render_template('profile.html')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(id):
    return User(id, session['name'], session['type'])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
