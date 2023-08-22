import base64

from flask import Flask, render_template, request
import numpy as np
import cv2
import io
from gauge_reader import gauge_reader_mod
from digit_reader import digit_reader_mod

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/gauge_index")
def gauge_index():
    return render_template('gauge_index.html')

@app.route("/digit_index")
def digit_index():
    return render_template('digit_index.html')


@app.route("/gauge_reader", methods=['POST'])
def gauge_reader():
    if 'image' not in request.files:
        return "No file part"
    else:
        image = request.files['image']
        if image.filename == '':
            return "No selected file"

        min_angle = float(request.form.get('min_angle'))
        max_angle = float(request.form.get('max_angle'))
        min_value = float(request.form.get('min_value'))
        max_value = float(request.form.get('max_value'))
        
        image_byte = image.read()
        image_arr = cv2.imdecode(np.frombuffer(image_byte, np.uint8), -1)
        print(image_arr.shape)
        x, y, r, cal_image_bytes = gauge_reader_mod.calibrate_gauge(image_arr)
        print(cal_image_bytes)
        val = gauge_reader_mod.get_current_value(image_arr, min_angle, max_angle, min_value, max_value, x, y, r)
        return render_template('gauge_index.html', reader_text='The Current Value is {}'.format(val))

@app.route("/digit_reader", methods = ['POST'])
def digit_reader():
    if 'image' not in request.files:
        return "No file part"
    else:
        image = request.files['image']
        if image.filename == '':
            return "No selected file"

        decimal = float(request.form.get('decimal'))
        
        image_byte = image.read()
        image_arr = cv2.imdecode(np.frombuffer(image_byte, np.uint8), -1)
        val = digit_reader_mod.reader(image_arr, decimal)
        return render_template('digit_index.html', reader_text='The Current Value is {}'.format(val))

# @app.route("/gauge_reader_api", methods=['POST'])
# def reader_api():
#     # print post data
#     res = request.json['image']
#     min_angle = float(request.json['min_angle'])
#     max_angle = float(request.json['max_angle'])
#     min_value = float(request.json['min_value'])
#     max_value = float(request.json['max_value'])

#     binary_image_data = base64.b64decode(res)

#     # Convert binary data to NumPy array
#     numpy_array = np.frombuffer(binary_image_data, np.uint8)

#     # print(numpy_array.shape)
#     opencv_image = cv2.imdecode(numpy_array, -1)
#     print(opencv_image.shape)
#     cv2.imwrite('test.jpg', opencv_image)

#     print(gauge_reader.calibrate_gauge(opencv_image))
#     x, y, r, cal_img_bytes = gauge_reader.calibrate_gauge(opencv_image)
#     print(cal_img_bytes)
#     val = gauge_reader.get_current_value(opencv_image, min_angle, max_angle, min_value, max_value, x, y, r)
#     print(val)

#     return {
#         "value": val,
#         # "image":  cal_img_bytes,
#     }

# @app.route("/digit_reader_api", methods = ['POST'])
# def reader_api():
#     res = request.json['image']
#     decimal = float(request.json['decimal'])

#     binary_image_data = base64.b64decode(res)

#     # Convert binary data to NumPy array
#     numpy_array = np.frombuffer(binary_image_data, np.uint8)
#     opencv_image = cv2.imdecode(numpy_array, -1)
#     val = digit_reader.reader(opencv_image, decimal)

#     return {
#         "value": val,
#     }

if __name__ == '__main__':
    app.run(
        #debug=True, host='0.0.0.0', port=50162
    )
   
    