#!/usr/bin/env python3
import sys
import cv2
import requests
import operator
import xml.etree.ElementTree as ET
import os
import random
import shutil

class Slide:
	def __init__(self, time_sec, slide_name):
		self.time_sec = time_sec
		self.slide_name = slide_name
		
	def __str__(self):
		return f"orderId: {self.order_id} timeSec: {self.time_sec} time: {self.time} slideName: {self.slide_name}"
		
	def __repr__(self):
		return self.__str__()

if __name__ == "__main__":
	# Download the xml from first argument
	assert len(sys.argv) == 3, "Please provide the xml file id as first argument and output name as second argument."
	xml_id = sys.argv[1]
	url = f"https://slides.slideslive.com/{xml_id}/{xml_id}.xml"
	print("Downloading xml file...")
	response = requests.get(url)
	xml_doc = response.content

	# Parse the xml
	print("Parsing xml file...")
	slides = []
	for slide in ET.ElementTree(ET.fromstring(xml_doc)).getroot():
		time_sec = int(slide.find('timeSec').text)
		slide_name = slide.find('slideName').text
		slide = Slide(time_sec, slide_name)
		slides.append(slide)
	slides = sorted(slides, key=operator.attrgetter('time_sec'))

	# Download the slides mentioned in the xml
	print("Creating temporary directory...")
	base_url = f"https://slides.slideslive.com/{xml_id}/slides/big"
	exists = True
	while exists:
		rand_id = random.randint(0, 100000)
		tmp_folder_name = f"slides-{rand_id}"
		if not os.path.exists(tmp_folder_name):
			exists = False
			os.makedirs(tmp_folder_name)

	print("Downloading slides...")
	for idx, slide in enumerate(slides):
		if idx % 5 == 0:
			print(f"\tDownloading slide {idx}/{len(slides)}...")
		slide_url = f"{base_url}/{slide.slide_name}.jpg"
		response = requests.get(slide_url)
		with open(f"{tmp_folder_name}/{slide.slide_name}.jpg", 'wb') as f:
			f.write(response.content)

	# Create the video
	print("Creating video...")
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out_name = sys.argv[2]
	out = cv2.VideoWriter(f"{out_name}-slides.mp4", fourcc, 1.0, (1024, 576))

	first_frame = cv2.imread(f"{tmp_folder_name}/{slides[0].slide_name}.jpg")
	for _ in range(4):		# First frame lasts ~ 4 seconds more than stated
		out.write(first_frame)
	for i in range(0, len(slides)-1):
		frame_count = slides[i + 1].time_sec - slides[i].time_sec
		frame = cv2.imread(f"{tmp_folder_name}/{slides[i].slide_name}.jpg")
		for _ in range(frame_count):
			out.write(frame)
	last_frame = cv2.imread(f"{tmp_folder_name}/{slides[-1].slide_name}.jpg")
	for _ in range(10):		# Last frame for 10 seconds
			out.write(last_frame)
	out.release()
	
	# Delete the temporary folder with slides
	print("Deleting temporary folder...")
	shutil.rmtree(tmp_folder_name)

	print("Done!")