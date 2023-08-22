from flask import Flask, render_template, request
import numpy as np
import cv2
import digit_reader

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/reader", methods = ['POST'])
def reader():
    if 'image' not in request.files:
        return "No file part"
    else:
        image = request.files['image']
        if image.filename == '':
            return "No selected file"

        decimal = float(request.form.get('decimal'))
        
        image_byte = image.read()
        image_arr = cv2.imdecode(np.frombuffer(image_byte, np.uint8), -1)
        val = digit_reader.reader(image_arr, decimal)
        return render_template('index.html', reader_text='The Current Value is {}'.format(val))

if __name__ == '__main__':
    app.run()
   
    