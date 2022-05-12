from flask import Flask, render_template, request, Response,redirect,session,flash
from werkzeug.utils import secure_filename
import os
from db import MyUpload, db_init, db

import base64

app = Flask(__name__)
app.secret_key='newproject'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/paint')
def paint():
    image=MyUpload.query.filter_by(id=1).first()
    return render_template('index2.html',data=image)

@app.route('/remove')
def remove():
    return render_template('tab3.html')

def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg','png'}


@app.route('/upload', methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        print(request.files)
        file= request.files['file']
        if not file:
            return 'No pic uploaded!', 400

        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        if not filename or not mimetype:
            return 'Bad upload!', 400
        if file and allowed_files(file.filename):
                print(file.filename)
                filename = secure_filename(file.filename)
                file.save(os.path.join(os.getcwd(),"static/uploads",filename))
                
                upload = MyUpload(img =f"/static/uploads/{filename}", imgtype = os.path.splitext(file.filename)[1])
                db.session.add(upload)
                db.session.commit()

                flash('file uploaded and saved','success')
                session['uploaded_file'] = f"/static/uploads/{filename}"
                return redirect(request.url)
        else:
            flash('wrong file selected, only PNG and JPG images allowed','danger')
            return redirect(request.url)

  
    return 'Img Uploaded!', 200    
    
        
@app.route('/<int:id>')
def get_img(id):
    img = MyUpload.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)

if __name__ == '__main__':
  app.run(debug=True)    