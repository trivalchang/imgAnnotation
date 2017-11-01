from __future__ import print_function

import numpy as np
import argparse
import ConfigParser
from configobj import ConfigObj
import glob
import cv2
import os 
import sys

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs

from color_kmeans import findDominantColor
from click_and_crop import *

DOMINATE_CLUSTER_NO	= 2
font = cv2.FONT_HERSHEY_SIMPLEX
class_color = [
	(255, 0, 0),
	(0, 255, 0),
	(0, 0, 255),
	(255, 255, 0),
	(255, 0, 255),
	(0, 255, 255),
	(128, 255, 0)
	]

class VideoReader():
	imageList = []
	bVideo = False
	index = 0
	cap = None
	def __init__(self, images, is_video):
		self.imageList = []
		self.bVideo = is_video
		self.index = 0
		if (is_video == False):
			for f in os.listdir(images):
				#if f.endswith(".png") or f.endswith(".jpg"):
				if f.endswith(".jpg"):
					self.imageList.append(images+'/'+f)

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

class pacasl_voc_writer:

	def __init__(self, fName, folder, imgSize, path=None):
		self.fName = fName
		self.imgSize = imgSize
		self.folder = folder
		self.path = path
		self.objList = []

	def new_box(self, objName, box):
		self.objList.append((objName, box))

	def prettify(self, elem):
		rough_string = ElementTree.tostring(elem, 'utf8')
		root = etree.fromstring(rough_string)
		return etree.tostring(root, pretty_print=True)

	def save(self):
		vocFile = codecs.open(self.fName+'.xml', 'w')
		annotation = Element('annotation')
		annotation.set('verified', 'yes')
		folder = SubElement(annotation, 'folder')
		folder.text = self.folder
		filename = SubElement(annotation, 'filename')
		filename.text = self.fName
		if (self.path != None):
			path = SubElement(annotation, 'path')
			path.text = self.path

		source = SubElement(annotation, 'source')
		database = SubElement(source, 'database')
		database.text = 'Unkown'

		size = SubElement(annotation, 'size')
		width = SubElement(size, 'width')
		width.text = str(self.imgSize[0])
		height = SubElement(size, 'height')
		height.text = str(self.imgSize[1])
		depth = SubElement(size, 'depth')
		depth.text = str(self.imgSize[2])

		for (objName, objBox) in self.objList:
			print(objName, objBox)
			obj = SubElement(annotation, 'object')
			name = SubElement(obj, 'name')
			name.text = objName
			pose = SubElement(obj, 'pose')
			pose.text = 'Unspecified'
			truncated = SubElement(obj, 'truncated')
			truncated.text = '0'
			difficult = SubElement(obj, 'difficult')
			difficult.text = '0'
			bndbox = SubElement(obj, 'bndbox')
			xmin = SubElement(bndbox, 'xmin')
			xmin.text = str(objBox[0])
			ymin = SubElement(bndbox, 'ymin')
			ymin.text = str(objBox[1])
			xmax = SubElement(bndbox, 'xmax')
			xmax.text = str(objBox[2])
			ymax = SubElement(bndbox, 'ymax')
			ymax.text = str(objBox[3])

		prettifyResult = self.prettify(annotation)
		vocFile.write(prettifyResult.decode('utf8'))
		vocFile.close()

def main():

	global DOMINATE_CLUSTER_NO

	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video", required=False, help="Path to video file, 'webcam' for live video from your computer camera")
	ap.add_argument("-d", "--directory", required=False, help="Path to the picture photo")
	ap.add_argument("-f", "--filename", required = False, default='hikeen.ini', help="file name for config output")
	ap.add_argument("-a", "--annotation", action='store_true', help="create Annotations are saved as XML files in PASCAL VOC format")
	ap.add_argument("-c", "--classes", required=False,  help="text file contains classes")
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



	classes = []
	if (args['classes'] != None):
		classes = open(args['classes']).read().split("\n")

	bAnnotation = args["annotation"]
	if (bAnnotation):
		if (classes == []):
			ap.print_help()
			sys.exit()

	bVideo = False
	if (args["video"] != None):
		bVideo = True
		vr = VideoReader([args["video"]], True)
	else:
		vr = VideoReader(args["directory"], False)

	#voc_writer = pacasl_voc_writer('pikachu0', 'pikachu', [100, 80, 3])
	#voc_writer.new_box('pikachu', [100, 101, 102, 103])
	#voc_writer.save()

	vr.open()

	cv2.namedWindow("image")
	

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

			(tH, tW, channels) = frame.shape[:3]

			voc_writer = pacasl_voc_writer(imageName.replace('.jpeg', '').replace('.jpg', ''), 'pikachu', [tW, tH, channels])

			title = imageName

			newH = height
			newW = width
			if (tH > height):
				scale = float(height)/float(tH)
				newH = height;
				newW = int(scale * width)
			if (tW > width):
				scale = float(width)/float(tW)
				newW = width;
				newH= int(scale * height)
			scaleH = float(newH)/float(tH)
			scaleW = float(newW)/float(tW)
			frame = cv2.resize(frame, (newW, newH))
			(tH, tW) = frame.shape[:2]
			cv2.imshow(title, frame)
			cv2.moveWindow(title, 0, 0)
			cv2.waitKey(1)
			cv2.setMouseCallback(title, click_and_crop)
			clone = frame.copy()
			framecnt = framecnt + 1
			if (bVideo == False):
				bPause = True

		key = cv2.waitKey(1) & 0xFF

		if key == ord('d') and bRoiGot == True:
			bRoiGot = False
			cv2.destroyWindow('template'+str(captureCnt))
			lastPoints = []
			frame = clone.copy()
			cv2.imshow(title, frame)
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
		if key == ord('n'):
			bPause = True if (bPause == False) else False
			cv2.destroyWindow(title)
		if key == ord('q'):
			break

		if (key>=ord('0') and key<=ord('9')) and bAnnotation == True and bRoiGot == True:
			print(classes[key-ord('0')])
			classIdx = key-ord('0')
			textX = min(points[0][0], points[1][0]) + 5
			textY = min(points[0][1], points[1][1]) + 30
			frame = clone.copy()
			cv2.putText(frame, classes[classIdx], (textX,textY), font, 0.8, class_color[classIdx], 2, cv2.LINE_AA)
			cv2.rectangle(frame, lastPoints[0], lastPoints[1], class_color[classIdx], 2)
			x = [lastPoints[0][0], lastPoints[1][0]]
			x[:] = [int(float(p)/scaleW) for p in x]
			y = [lastPoints[0][1], lastPoints[1][1]]
			y[:] = [int(float(p)/scaleH) for p in y]
			voc_writer.new_box(classes[classIdx], [x[0], y[0], x[1], y[1]])
			cv2.imshow(title, frame)
			cv2.waitKey(1)
			clone = frame
			bRoiGot = False

		if key == ord('s') and bAnnotation == True:
			voc_writer.save()

		#if bAnnotation == True and (int(:


		if is_cropping() == True:
			bPause = True
			bRoiGot, points = is_cropDone()
			if (bRoiGot == False):
				if (lastPoints != points):
					frame = clone.copy()
					#cv2.rectangle(frame, points[0], points[1], (0, 255, 0), 2)
					print('draw Rect')
					cv2.rectangle(frame, 
								(min(points[0][0], points[1][0]), min(points[0][1], points[1][1])), 
								(max(points[0][0], points[1][0]), max(points[0][1], points[1][1])), 
								(0, 255, 0), 2)
					cv2.imshow(title, frame)
					cv2.waitKey(1)
					lastPoints = []
					lastPoints.append(points[0])
					lastPoints.append(points[1])
					continue
			else:
				lastPoints = []
				lastPoints.append((min(points[0][0], points[1][0]), min(points[0][1], points[1][1])))
				lastPoints.append((max(points[0][0], points[1][0]), max(points[0][1], points[1][1])))
				roi = clone[points[0][1]:points[1][1], points[0][0]:points[1][0]]	
				#cv2.imshow('template'+str(captureCnt), roi)	
				frame = clone.copy()
				cv2.rectangle(frame, lastPoints[0], lastPoints[1], (0, 255, 0), 2)
				cv2.imshow(title, frame)
				cv2.waitKey(1)


	if bAnnotation == False:
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
	else:
		print('annotation is true')


	print('program finished')

main()
