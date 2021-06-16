################################################################################################
#       Author   : Abhishek Hazra
#       verion   : 0.0.1
#       build    : application/Demo
#       desc     : Demo app to explain basic fundamental concepts of routing and web application
#       email    : dmabhishekhazra@gmail.com
#       github   : https://github.com/hazra1991
#################################################################################################

from flask import Flask,render_template,request,session,flash,url_for,redirect ,send_file
import sqlite3
from passlib.hash import pbkdf2_sha256 as passhash
import os


#####################
## app settings  ###
####################
app = Flask(__name__)
app.secret_key = "password"
app.config["UPLOAD_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)),'uploads')
print(os.getenv('UPLOAD_PATH'))


#################
### DB Models ###
#################
def createDb():
    # global cur
    db = sqlite3.connect('user_db.db')
    cur = db.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS userinfo (username PRIMARY KEY,password)')
    cur.execute('CREATE TABLE IF NOT EXISTS userrecords (username PRIMARY KEY,storage_path)')

    if not os.path.exists(app.config["UPLOAD_PATH"]):
        os.makedirs(app.config["UPLOAD_PATH"])


##############################
### View functions /routes ###
##############################

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/login',methods=['GET','POST'])
def login():
    print(session)
    if not session:
        if request.method == 'GET':
            return render_template('login.html')
        username = request.form['email']
        password = request.form['password']  
        message = None      
        with sqlite3.connect('user_db.db') as db:
            cur =db.cursor()
            cur.execute('SELECT password FROM userinfo WHERE username=(?)',(username,))
            db.commit()
            pw = cur.fetchone()
            if pw and passhash.verify(password,pw[0]):
                session['username'] = username
            else:
                if pw is None:
                    message = "USER NOT PRESENT .PLEASE REGISTER"
                else:
                    message =  'INVALLID PASSWORD'
                return render_template('login.html',message = message)  
    return redirect(url_for('filestore'))
    
    
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    message =None
    if request.form['password'] == request.form['confirmpass']:
        password = passhash.hash(request.form['password'])
        username =  request.form['email']
        try:
            with sqlite3.connect('user_db.db') as db:
                cur = db.cursor()
                cur.execute('INSERT INTO userinfo values(?,?)',(username,password))
                db.commit()
                message = 'User Created please login'
        except sqlite3.IntegrityError:
            message = 'User already present please login'
    else:
        message = 'Password and confirm password didnot match'
    return render_template('register.html',message=message)
    
    
@app.route('/filestore',methods = ['GET','POST'])
def filestore():
    if 'username' in session:
        if request.method == 'GET':
            return render_template('filestore.html',username=session['username'],fileset=os.listdir(app.config['UPLOAD_PATH']))
        if request.args['value'] == 'upload':
            file_to_upload =  request.files['File']
            name = file_to_upload.filename
            if name:
                if os.path.exists(app.config["UPLOAD_PATH"]):
                    file_to_upload.save(os.path.join(app.config["UPLOAD_PATH"],name))
                message = "File uploaded successfull"

            else:
                message = 'No file spesified to upload'
        
        elif request.args['value'] == 'download':
            print(request.form)
            try:
                return send_file(os.path.join(app.config['UPLOAD_PATH'],request.form['downloadFile']),as_attachment = True)
            except FileNotFoundError:
                message = "File not found'"
        return render_template('filestore.html',message=message,fileset=os.listdir(app.config['UPLOAD_PATH']))

    else:
        return redirect('login')


@app.route('/logout',methods = ['GET'])
def logout():
    session.pop('username')
    return redirect('login')

####################
# ERROR HANDELLERS #
####################

@app.errorhandler(404)
def notFound(er):
    return render_template('notfound.html')


if __name__ == '__main__':
    createDb()
    app.run(debug =True)

