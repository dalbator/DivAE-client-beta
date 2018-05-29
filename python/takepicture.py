import os
#from pathlib import Path
#import path
import picamera
from time import sleep
from threading import Thread

def takePictureGlobal(picturetaken_callback, peripheral_id):
    camera = picamera.PiCamera()
    try:
      camera.sharpness = 0
      camera.contrast = 0
      camera.brightness = 50
      camera.saturation = 0
      camera.ISO = 0
      camera.video_stabilization = False
      camera.exposure_compensation = 0
      camera.exposure_mode = 'off'
      camera.meter_mode = 'average'
      camera.awb_mode = 'auto'
      camera.image_effect = 'none'
      camera.color_effects = None
      camera.rotation = 270
      camera.hflip = False
      camera.vflip = False
      camera.crop = (0.0, 0.0, 1.0, 1.0)
      camera.resolution = "HD"

      PICTURE_PATH = os.path.expanduser("../../akpics")

      if not os.path.exists(PICTURE_PATH):
        os.makedirs(PICTURE_PATH)

      if os.path.exists(PICTURE_PATH):
        print('capturing image')
        picturefile = PICTURE_PATH+ '/img' + '.jpg';
        camera.capture(picturefile)
        sleep(3);
        if not (picturetaken_callback is None):
          picturetaken_callback(picturefile, peripheral_id);	 
      else:
        print("picture path does  not exist");
    finally:
      camera.close();

class AKCamera:
  def takeOnePicture(self, picturetaken_callback, peripheral_id):
    thread = Thread(target = takePictureGlobal, args = (picturetaken_callback, peripheral_id, ))
    thread.start()
    #thread.join()
    #print "thread finished...exiting"



#tp = AKCamera();
#tp.takeOnePicture(None, None)
#tp = None;
