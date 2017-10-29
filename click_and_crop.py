# import the necessary packages
import cv2

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = [(0, 0), (0, 0)]
cropping = False
cropDOne = False

def is_cropping():
	global refPt, cropping, cropDOne
	return cropping

def is_cropDone():
	global refPt, cropping, cropDOne
	if (cropDOne == True):
		cropping = False
	return (cropDOne, refPt)

def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, cropping, cropDOne

	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		if (cropping == False):
			refPt[0] = (x, y)
			refPt[1] = (x, y)
			cropping = True
			cropDOne = False
		else:
			cropDOne = True
		print('left button pressed')
	elif event == cv2.EVENT_MOUSEMOVE:
		refPt[1] = (x, y)
