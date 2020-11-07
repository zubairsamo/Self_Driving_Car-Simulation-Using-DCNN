from flask import Flask
from flask import render_template
import socketio
import eventlet
from io import BytesIO
from PIL import Image
import cv2
from tensorflow.keras.models import load_model
import base64
import numpy as np

app = Flask(__name__)

server = socketio.Server()

@server.on('connect')
def connect(sid,environ):
    print('Connected')
    # send_control(0,1)

def imgpreprocess(img):
    img = img[60:140,:,:]
    img = cv2.cvtColor(img,cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img,(3,3),0)
    img = cv2.resize(img,(200,66))
    img = img/255
    return img


@server.on('telemetry')
def telemetry(sid,data):
    speed_limit = 10
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = imgpreprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0 - speed/speed_limit
    send_control(steering_angle,throttle)

def send_control(steering_angle,throttle):
    server.emit('steer',data={
        'steering_angle': steering_angle.__str__(),
        'throttle':throttle.__str__()
    })

if __name__ == "__main__":
    model = load_model('DriveCar2.h5')
    app = socketio.Middleware(server,app)
    eventlet.wsgi.server(eventlet.listen(('',4567)),app)


