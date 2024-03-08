import numpy as np
import cv2 as cv
from datetime import datetime


class VideoRecorder:
	def __init__(self):
		# Properties
		self.window_title = "Hide in Darkness"

		# Reading Relateds
		self.video_reader = None
		self.video_index = 0
		self.fps = -1
		self.wait_msec = -1

		# Recording Relateds
		self.video_writer = None
		self.recording = False

		# Filter Relateds
		self.filter_rect = None
		self.filter_contrast = 1.6
		self.filter_brightness = -40

		# Mouse Input Relateds
		self.mouse_button_pressed = False
		self.mouse_position = (-1, -1)

	def display_on_screen(self, image):
		if self.recording:
			h, w, *_ = image.shape
			center = (int(w / 2), h - 50)
			radius = 20
			cv.circle(image, center, radius + 5, color=(255, 255, 255), thickness=-1)
			cv.circle(image, center, radius, color=(0, 0, 255), thickness=-1)

		cv.imshow(self.window_title, image)

	def write_video_frame(self, imgframe, video_file, codec, fps):
		if not self.video_writer.isOpened():
			h, w, *_ = imgframe.shape
			frame_size = (w, h)

			# Open the video file
			opened = self.video_writer.open(video_file, codec, fps, frame_size)
			if not opened:
				print("Write error: Failed to open a video!")
				return

		self.video_writer.write(imgframe)

	def filter_image(self, image):
		img_copy = image.copy()
		if self.filter_rect is not None:
			x_begin, y_begin = self.filter_rect[0]
			x_end, y_end = self.filter_rect[1]
			if x_begin > x_end:
				x_begin, x_end = x_end, x_begin
			if y_begin > y_end:
				y_begin, y_end = y_end, y_begin

			img_grayscale = self.filter_contrast * cv.cvtColor(image, cv.COLOR_BGR2GRAY) + self.filter_brightness
			img_grayscale[img_grayscale < 0] = 0
			img_grayscale[img_grayscale > 255] = 255
			img_copy[y_begin:y_end, x_begin:x_end, 0] = img_grayscale[y_begin:y_end, x_begin:x_end]
			img_copy[y_begin:y_end, x_begin:x_end, 1] = img_grayscale[y_begin:y_end, x_begin:x_end]
			img_copy[y_begin:y_end, x_begin:x_end, 2] = img_grayscale[y_begin:y_end, x_begin:x_end]

		return img_copy

	def run(self):
		video = cv.VideoCapture(self.video_index)
		if not video.isOpened():
			print("Read error: Failed to take a camera!")
			return

		# Reader setup
		self.video_reader = video
		self.fps = video.get(cv.CAP_PROP_FPS)
		self.wait_msec = int(1 / self.fps * 1000)

		# Writer setup
		self.video_writer = cv.VideoWriter()
		current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
		video_file = f"{current_time}.mp4"
		codec = cv.VideoWriter_fourcc(*"mp4v")

		# Open window
		cv.namedWindow(self.window_title)
		cv.setMouseCallback(self.window_title, VideoRecorder._on_mouse_event, self)

		while True: # Play the video
			valid, img = self.video_reader.read()
			if not valid:
				break

			# Process frame
			img_filtered = self.filter_image(img)
			if self.recording:
				self.write_video_frame(img_filtered, video_file, codec, self.fps)
			self.display_on_screen(img_filtered)

			# Read keyboard inputs
			key = cv.waitKey(self.wait_msec)
			if key == 27: # ESC
				self.video_writer.release()
				break
			elif key == ord(' '):
				self.recording = not self.recording

	def _on_mouse_event(event, x, y, flags, self):
		self.mouse_position = (x, y)

		if event == cv.EVENT_LBUTTONDOWN:
			self.mouse_button_pressed = True
			self._on_left_mouse_button_down()
		elif event == cv.EVENT_LBUTTONUP:
			self.mouse_button_pressed = False
			self._on_left_mouse_button_up()
		elif event == cv.EVENT_MOUSEMOVE and self.mouse_button_pressed:
			if self.filter_rect is not None:
				self.filter_rect[-1] = self.mouse_position

	def _on_left_mouse_button_down(self):
		self.filter_rect = [self.mouse_position, self.mouse_position]

	def _on_left_mouse_button_up(self):
		self.filter_rect = None


if __name__ == "__main__":
	video_recorder = VideoRecorder()
	video_recorder.run()