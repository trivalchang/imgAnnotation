# imgAnnotation
This is a simple utility to crop image from video or image. imgAnnotation uses **OpenCV** to read video or directory of pictures, crop the object and save the in pascal VOC format.

imgAnnotation uses hotkey to select and save the annotation instead of GUI.

Thanks to [pyimagesearch](https://www.pyimagesearch.com/) and [lableImg](https://github.com/tzutalin/labelImg) . The most of the techniques are from these 2 places.

## Usage
python imgAnnotation.py -d PATH_TO_PICTURS -c OBJECT_CLASS_STORE

**for ex:
  
  python imgAnnotation.py -a -d ../pikachu -c classes.txt**
  
  imgAnnotation will display the pictures under ../pikchu. Users use the mouse to select the region containting the object.
  
  Hotkey
    'n' : next picture
    '0' ~ '9': select nth class in classes.txt
    's' : save piscal voc file in IMG_FILE_NAME.xml

The snapshot of this utility is [here](https://goo.gl/gvv8rX)

## Note
This tool is only tested on MAC OSX equipped with python 2.7 and OpenCV 3.3
