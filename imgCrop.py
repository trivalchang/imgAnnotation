from __future__ import print_function

import numpy as np
import argparse
import ConfigParser
from configobj import ConfigObj
import glob
import cv2
import os 
import sys

from color_kmeans import findDominantColor
from click_and_crop import *

DOMINATE_CLUSTER_NO	= 2

class VideoReader():
	imageList = []
	bVideo = False
	index = 0
	cap = None
	def __init__(self, images, is_video):
		self.imageList = images
		self.bVideo = is_video
		self.index = 0

	def open(self):
		if (self.bVideo == True): 
			if self.imageList[0] == 'webcam':
				self.cap = cv2.VideoCapture(0)
			else:
				self.cap = cv2.VideoCapture(self.imageList[0])

	def read(self):
		if (self.bVideo == True): 
			if (self.cap.isOpened() == False):
				return (False, None, None)
			ret, frame = self.cap.read()
			return (ret, frame, None)
		else:
			if (self.index >= len(self.imageList)):
				return (False, None, None)
			img = cv2.imread(self.imageList[self.index])
			imageName = self.imageList[self.index]
			self.index = self.index + 1
			return (True, img, imageName)

	def close(self):
		self.cap.release()

def main():

	global DOMINATE_CLUSTER_NO

	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video", required=False, help="Path to video file, 'webcam' for live video from your computer camera")
	ap.add_argument("-d", "--directory", required=False, help="Path to the picture photo")
	ap.add_argument("-f", "--filename", required = False, default='hikeen.ini', help="file name for config output")
	args = vars(ap.parse_args())

	if (len(args) == 2):
		ap.print_help()
		sys.exit()

	if (args["video"] == None) and (args["directory"] == None):
		ap.print_help()
		sys.exit()

	if (args["video"] != None) and (args["directory"] != None):
		ap.print_help()
		sys.exit()	

	bVideo = False
	if (args["video"] != None):
		bVideo = True
		vr = VideoReader([args["video"]], True)
	else:
		vr = VideoReader(args["directory"], False)

	vr.open()

	cv2.namedWindow("image")
	cv2.setMouseCallback("image", click_and_crop)

	width = 1280
	height = 720

	framecnt = 0
	bPause = False
	captureCnt = 0
	bRoiGot = False
	points = []
	lastPoints = []
	itemList = []
	while (True):

		if (bPause != True):
			ret, frame, imageName = vr.read()
			if (ret == False):
				break

			frame = cv2.resize(frame, (width, height))
			cv2.imshow('image', frame)
			clone = frame.copy()
			framecnt = framecnt + 1

		if (bVideo == True):
			key = cv2.waitKey(1) & 0xFF
		else:
			key = ord('c')
			bRoiGot = True
			roi = frame

		if key == ord('d') and bRoiGot == True:
			bRoiGot = False
			cv2.destroyWindow('template'+str(captureCnt))
			lastPoints = []
			frame = clone.copy()
			cv2.imshow("image", frame)
			#cv2.setMouseCallback("image", click_and_crop)
			cv2.waitKey(1)
	
		if key == ord('c') and bRoiGot == True:
			#os.system('tput bel')
			cv2.imwrite('template'+str(captureCnt)+'.png', roi)
			grayRoi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
			colorList = findDominantColor(roi, DOMINATE_CLUSTER_NO)
			if (imageName != None):
				itemList.append((imageName, colorList, points))
			else:
				itemList.append(('template'+str(captureCnt)+'.png', colorList, list(points)))
			captureCnt = captureCnt + 1
		if key == ord('p'):
			bPause = True if (bPause == False) else False
		if key == ord('q'):
			break

		if is_cropping() == True:
			bPause = True
			bRoiGot, points = is_cropDone()
			if (bRoiGot == False):
				if (lastPoints != points):
					frame = clone.copy()
					cv2.rectangle(frame, points[0], points[1], (0, 255, 0), 2)
					cv2.imshow("image", frame)
					cv2.waitKey(1)
					lastPoints = []
					lastPoints.append(points[0])
					lastPoints.append(points[1])
				continue
			else:
				roi = clone[points[0][1]:points[1][1], points[0][0]:points[1][0]]	
				cv2.imshow('template'+str(captureCnt), roi)		
				cv2.rectangle(frame, points[0], points[1], (0, 255, 0), 2)
				cv2.imshow("image", frame)
				cv2.waitKey(1)


	if itemList != []:
		config = ConfigObj(args["filename"])
		config['item number'] = len(itemList)
		config['dominant cluster'] = DOMINATE_CLUSTER_NO
		itemIndex = 0
		for (itemPicName, dominant, loc) in itemList:
			itemName = 'ITEM'+str(itemIndex)
			config[itemName] = {}
			config[itemName]['File name'] = itemPicName
			config[itemName]['dominant'] = dominant
			if (loc==[]):
				config[itemName]['location'] = []
			else:
				config[itemName]['location'] = [loc[0][0], loc[0][1], loc[1][0], loc[1][1]]
			itemIndex = itemIndex + 1
		with open(args["filename"], 'w') as configfile:
			config.write()


	print('program finished')

main()
