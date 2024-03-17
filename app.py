from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
from keras.models import load_model
import cv2
from keras.utils import img_to_array
import tensorflow as tf
res_model = load_model("resmodel.h5")
mob_model = load_model("mobile_model.h5")
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
def preprocc(img):
    image = cv2.imread(img,cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image,(256,256))
    eq = cv2.equalizeHist(image)
    img_rgb = cv2.cvtColor(eq, cv2.COLOR_GRAY2RGB)

    img_array = img_to_array(img_rgb)
# img_array = preprocess_input(img_array)
    img_array = tf.expand_dims(img_array, 0)
    return img_array
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
 
@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(file)
        img = preprocc(r"static/uploads/"+filename)
        y = res_model.predict(img)
        y2 = mob_model.predict(img)

        # # #print('upload_image filename: ' + filename)
        print(y)
        print(y2)
        s1 = ""
        s2 = ""
        resv = y[0][0]
        mobv = y2[0][0]
        resv1 = y[0][1]
        mobv1 = y2[0][1]
        if y[0][0]>y[0][1]:
            s1 = "Defective"
        else:
            s1 = "Good"
        if y2[0][0]>y2[0][1]:
            s2 = "Defective"
        else:
            s2 = "Good"          
        # print(url_for('display_image', filename=filename))

        flash('Image successfully uploaded and displayed below')
        return render_template('index.html', filename=filename,res = s1,mob = s2,res_v = resv,mob_v = mobv,mob_v1 = mobv1,res_v1 = resv1 )
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
 
if __name__ == "__main__":
    app.run()