from flask import Flask, jsonify, render_template, request, Response,redirect,session,flash
from werkzeug.utils import secure_filename
from db import MyUpload, db_init, db
from io import BytesIO
from PIL import Image
import base64
import re
import os
import numpy as np
import matplotlib as plt


app = Flask(__name__)
app.secret_key='newproject'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)


@app.route('/upload_file')
def upload_file():
    return render_template('upload_file.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/feature')
def feature():
    return render_template('feature.html')    
    

@app.route('/gallery')
def gallery():
    images=MyUpload.query.all()
    return render_template('gallery.html',images=images)

@app.route('/canvas')
def canvas():
    id = request.args.get('i')
    image = MyUpload.query.filter_by(id=id).first()
    image_path = image.img
    return render_template('canvas.html',image=image,image_path=image_path)

@app.route('/contact')
def contact():
    return render_template('contact.html')    


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
                filepath=os.path.join(os.getcwd(),"static/uploads",filename)
                print(filepath)
                file.save(os.path.join(filepath))
                
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

@app.route('/delete/<int:id>')
def delete(id):
    img = MyUpload.query.filter_by(id=id).first()

    try:
        db.session.delete(img)
        db.session.commit()
        flash("image deleted successfully!!")
        images=MyUpload.query.all()
        return render_template('gallery.html',images=images)


    except:
        flash("whoops! there was a problem ")    
        images=MyUpload.query.all()
        return render_template('gallery.html',images=images)

@app.route('/saveimg',methods=['POST'])
def saveimg():
    if request.method=='POST':
        data=request.form.get('data')
        file=request.form.get('file')
        filename=os.path.basename(file)
        savepath=os.path.join('static','mask',filename)
        content = data.split(';')[1]
        image_encoded = content.split(',')[1]
        if not image_encoded.endswith('=='):
            image_encoded += '=='
        body = base64.decodebytes(image_encoded.encode('utf-8'))
        with open(savepath, 'wb') as f:
            f.write(body)
        image64 = base64.b64encode(open(file, 'rb').read())
        image64 = image64.decode('utf-8')
        print(f'Will use {file} for inpainting')
        img = np.array(plt.imread(f'{file}')[:,:,:3])
        with_mask = np.array(plt.imread(savepath)[:,:,:3])
        mask = (with_mask[:,:,0]==1)*(with_mask[:,:,1]==0)*(with_mask[:,:,2]==0)
        img = np.array((1-mask.reshape(mask.shape[0], mask.shape[1], -1))*plt.imread(file)[:,:,:3])
        if '.jpeg' in file:
            '''PYTHONPATH=. TORCH_HOME=$(pwd) python3 bin/predict.py model.path=$(pwd)/big-lama indir=$(pwd)/data_for_prediction outdir=/content/output dataset.img_suffix=.jpeg > /dev/null'''
        elif '.jpg' in file:
            '''PYTHONPATH=. TORCH_HOME=$(pwd) python3 bin/predict.py model.path=$(pwd)/big-lama indir=$(pwd)/data_for_prediction outdir=/content/output  dataset.img_suffix=.jpg > /dev/null'''
        elif '.png' in file:
            '''PYTHONPATH=. TORCH_HOME=$(pwd) python3 bin/predict.py model.path=$(pwd)/big-lama indir=$(pwd)/data_for_prediction outdir=/content/output  dataset.img_suffix=.png > /dev/null'''
        else:
            print(f'Error: unknown suffix .{file.split(".")[-1]} use [.png, .jpeg, .jpg]')
    return jsonify({'status':'success','message':'image saved successfully','path':savepath})
    
        
    
if __name__ == '__main__':
  app.run(debug=True)    