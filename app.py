from flask import Flask, render_template, request, redirect, url_for, session
from logging import FileHandler
import sqlite3
import secrets
import logging

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

db_file = 'mydb.db'


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'idno' not in session:
        return redirect(url_for('login'))

    conn = create_connection(db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM member WHERE idno = ?", (session['idno'],))
    user = c.fetchone()
    conn.close()

    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('idno', None)
    if request.method == 'POST':
        idno = request.form['idno']
        pwd = request.form['pwd']

        conn = create_connection(db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM member WHERE idno = ? AND pwd = ?", (idno, pwd))
        user = c.fetchone()
        conn.close()

        if user:
            session['idno'] = idno
            return redirect(url_for('index'))
        else:
            error_message = '請輸入正確的帳號密碼'
            return render_template('login.html',error=error_message)

    return render_template('login.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'idno' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nm = request.form['nm']
        birth = request.form['birth']
        blood = request.form['blood']
        phone = request.form['phone']
        email = request.form['email']
        idno = request.form['idno']
        pwd = request.form['pwd']

        try:
            conn = create_connection(db_file)
            c = conn.cursor()
            c.execute("UPDATE member SET nm=?, birth=?, blood=?, phone=?, email=?, idno=?, pwd=? WHERE idno=?", (nm, birth, blood, phone, email, idno, pwd, session['idno']))
            conn.commit()
            conn.close()
        except Exception as e:
            app.logger.errer('更新資料時發生錯誤',e)
            return redirect(url_for('error'))

        return redirect(url_for('index'))

    conn = create_connection(db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM member WHERE idno = ?", (session['idno'],))
    user = c.fetchone()
    conn.close()

    if user:
        return render_template('edit.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('idno', None)
    return redirect(url_for('login'))

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    handler = FileHandler('error.log')
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)
    app.run(debug=True)
