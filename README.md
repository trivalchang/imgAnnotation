# imgCrop
This is a simple utility to crop image from video or image. imgCrop uses **OpenCV** to read video or directory of pictures. Users can use mouse to select the region of interest to save to a new image file. 

This tool was to generate some template images for computer auto test. So it also stores the location and dominant color into an INI file in the following format

```
item number = 1
dominant cluster = 2
[ITEM0]
File name = template0.png
dominant = "[16, [191, 225, 221]]", "[83, [39, 248, 61]]"
location = 212, 20, 560, 148
```

Thanks to [pyimagesearch](https://www.pyimagesearch.com/). The most of the techniques are from pyimagesearch.

## Usage
python imgCrop.py -f PATH_TO_INI -v PATH_TO_VIDEO_FILE


The snapshot of this utility is [here](https://goo.gl/NAaX8g)

## Note
This tool is only tested on MAC OSX equipped with python 2.7 and OpenCV 3.3

## The next step
After some investigation, I can't find a good way to have a high accuracy to do computer auto test. So I will try to include tensorflow. I will develop imgCrop to do annotation for tensorflow object detection.
