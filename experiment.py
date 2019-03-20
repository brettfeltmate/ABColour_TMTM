# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

# Import required KLibs libraries
import klibs
from klibs import P
from klibs.KLConstants import STROKE_INNER, TK_S, NA, RC_COLORSELECT, RC_KEYPRESS
from klibs.KLUtilities import *
from klibs.KLKeyMap import KeyMap
from klibs.KLUserInterface import any_key, ui_request
from klibs.KLGraphics import fill, blit, flip, clear
from klibs.KLGraphics.KLDraw import *
from klibs.KLGraphics.colorspaces import const_lum as colors
from klibs.KLResponseCollectors import ResponseCollector
from klibs.KLEventInterface import TrialEventTicket as ET
from klibs.KLExceptions import TrialException
from klibs.KLCommunication import message
from klibs.KLTime import CountDown
# Import required external libraries
import sdl2
import time
import random
import math
import aggdraw # For drawing mask cells in a single texture
import numpy as np
from PIL import Image

# Define some useful constants
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
GRAY = (127,127,127,255)

IDENTITY = "identity"
COLOUR = "colour"


numbers = ['1', '2', '3', '4', '5',
                '6', '7', '8', '9']

class ABColour_TMTM(klibs.Experiment):

	def setup(self):
		# Stimulus sizes
		fix_thickness = deg_to_px(0.1)
		fix_size = deg_to_px(0.6)
		wheel_size = int(P.screen_y * 0.75)
		cursor_size = deg_to_px(1)
		cursor_thickness = deg_to_px(0.3)
		target_size = deg_to_px(1)


		# Initilize drawbjects
		self.fixation = FixationCross(size=fix_size, thickness=fix_thickness, fill=WHITE)
		self.t1_wheel = ColorWheel(diameter=wheel_size)
		self.t2_wheel = ColorWheel(diameter=wheel_size)
		self.cursor = Annulus(diameter=cursor_size, thickness=cursor_thickness, fill=BLACK)

		# Create text styles to store target colouring
		self.txtm.add_style(label="T1", font_size=target_size)
		self.txtm.add_style(label="T2", font_size=target_size)

		# Stimulus presentation durations (intervals of 16.7ms refresh rate)
		self.id_target_duration = P.refresh_time * 5 # 83.3ms
		self.id_mask_duration = P.refresh_time
		self.col_target_duration = P.refresh_time * 10 # 167ms
		self.col_mask_duration = P.refresh_time
		self.isi = P.refresh_time # ISI = inter-stimulus interval (target offset -> mask onset)

		# Colour ResponseCollector needs to be passed an object whose fill (colour)
		# is that of the target colour. W/n trial_prep(), these dummies will be filled
		# w/ the target colour and then passed to their ResponseCollectors, respectively.
		self.t1_dummy = Ellipse(width=1)
		self.t2_dummy = Ellipse(width=1)
		
		# Experiment messages
		self.anykey_txt = "{0}\nPress any key to continue."
		self.t1_id_request = "What was the first number?"
		self.t2_id_request = "What was the second number?"
		self.t1_col_request = "What was the first colour?"
		self.t2_col_request = "What was the second colour?"
		self.prac_identity_instruct = "\nIn this block, you will be asked to report what number was presented.\nIf you're unsure, make your best guess."
		self.prac_colour_instruct = "\nIn this block, you will be asked to report what colour was presented.\nIf you're unsure, make your best guess."
		self.test_identity_instruct = "\nIn this block, you will be asked to report which two numbers were presented.\nIf you're unsure, make your best guess."
		self.test_colour_instruct = "\nIn this block, you will be asked to report which two colours were presented.\nIf you're unsure, make your best guess."

		# Initialize ResponseCollectors
		self.t1_identity_rc = ResponseCollector(uses=RC_KEYPRESS)
		self.t2_identity_rc = ResponseCollector(uses=RC_KEYPRESS)

		self.t1_colouring_rc = ResponseCollector(uses=RC_COLORSELECT)
		self.t2_colouring_rc = ResponseCollector(uses=RC_COLORSELECT)

		# Initialize ResponseCollector Keymaps
		self.keymap = KeyMap(
			'identity_response',
			['1','2','3','4','5','6','7','8','9'],
			['1','2','3','4','5','6','7','8','9'],
			[sdl2.SDLK_1,sdl2.SDLK_2,sdl2.SDLK_3,
			sdl2.SDLK_4,sdl2.SDLK_5,sdl2.SDLK_6,
			sdl2.SDLK_7,sdl2.SDLK_8,sdl2.SDLK_9]
		)

		# Inserting practice blocks requires a pre-defined trial count; but in our case they are of an undefined length,
		# lasting for as long as it takes participants to reach a performance threshold. So, initially they are of length 1
		# but trials are inserted later on depending on participant performance.
		if P.run_practice_blocks:
			self.insert_practice_block([1,3], trial_counts=1)

		# Randomly select starting condition
		self.block_type = random.choice([COLOUR,IDENTITY])

	def block(self):
		if not P.practicing:
			if P.trial_number % 60 == 0:
				rest_txt = "Whew, go ahead a take a break!\nPress any key when you're ready to continue."
				rest_msg = message(rest_txt,align='center',blit_txt=False)
				fill()
				blit(rest_msg,5,P.screen_c)
				flip()
				any_key()
		
		
		
		self.t1_performance = 0


		# Present block progress
		block_txt = "Block {0} of {1}".format(P.block_number, P.blocks_per_experiment)
		progress_txt = self.anykey_txt.format(block_txt)

		if P.practicing: 
			progress_txt += "\n(This is a practice block)"

		progress_msg = message(progress_txt, align='center', blit_txt=False)

		fill()
		blit(progress_msg,5,P.screen_c)
		flip()
		any_key()

		# Inform as to block type
		if self.block_type == COLOUR:
			if P.practicing:
				block_type_txt = self.anykey_txt.format(self.prac_colour_instruct)
			else:
				block_type_txt = self.anykey_txt.format(self.test_colour_instruct)
		else:
			if P.practicing:
				block_type_txt = self.anykey_txt.format(self.prac_identity_instruct)
			else:
				block_type_txt = self.anykey_txt.format(self.test_identity_instruct)

		block_type_msg = message(block_type_txt, align='center', blit_txt=False)

		fill()
		blit(block_type_msg,5,P.screen_c)
		flip()
		any_key()

		# Pre-run: First 10 practice trials, no performance adjustments
		self.pre_run_complete = False
		# Practice: Subsequent practice trials wherein performance is adjusted
		self.practice_complete = False
		self.practice_trial_num = 1
		# Reset T1 performance each practice block
		self.t1_performance = 0
		
		# The following block manually inserts trials one at a time
		# during which performance is checked and adjusted for.
		if P.practicing:
			while P.practicing:
				self.itoa = random.choice([100,200,300])
				self.ttoa = random.choice([120,240,360,480,600])

				self.setup_response_collector()
				self.trial_prep()
				self.evm.start_clock()
				
				try:
					self.trial()
				except TrialException:
					pass
				
				self.evm.stop_clock()
				self.trial_clean_up()
				# Once practice is complete, the loop is exited
				if self.practice_complete:
					P.practicing = False



	def setup_response_collector(self):
		# Configure identity collector
		self.t1_identity_rc.terminate_after = [10, TK_S] # Waits 10s for response
		self.t1_identity_rc.display_callback = self.identity_callback # Continuously draw images to screen	
		self.t1_identity_rc.display_kwargs = {'target':"T1"} # Passed as arg when identity_callback() is called
		self.t1_identity_rc.keypress_listener.key_map = self.keymap # Assign key mappings
		self.t1_identity_rc.keypress_listener.interrupts = True # Terminates listener after valid response

		self.t2_identity_rc.terminate_after = [10, TK_S] 
		self.t2_identity_rc.display_callback = self.identity_callback
		self.t2_identity_rc.display_kwargs = {'target':"T2"}
		self.t2_identity_rc.keypress_listener.key_map = self.keymap 
		self.t2_identity_rc.keypress_listener.interrupts = True 

		# Configure colour collector
		# Because colours are randomly selected on a trial by trial basis
		# most properties of colouring_rc need to be assigned within trial_prep()
		self.t1_colouring_rc.terminate_after = [10, TK_S]
		self.t2_colouring_rc.terminate_after = [10, TK_S]

	def trial_prep(self):
		# Prepare colour wheels
		self.t1_wheel.rotation = random.randrange(0,360) # Randomly rotate wheel to prevent location biases
		self.t2_wheel.rotation = random.randrange(0,360) 
		
		while self.t1_wheel.rotation == self.t2_wheel.rotation: # Ensure unique rotation values
			self.t2_wheel.rotation = random.randrange(0,360)
		
		self.t1_wheel.render()
		self.t2_wheel.render()

		# Select target identities
		self.t1_identity = random.sample(numbers,1)[0] # Select & assign identity
		self.t2_identity = random.sample(numbers,1)[0]
		
		while self.t1_identity == self.t2_identity: # Ensure that T1 & T2 identities are unique
			self.t2_identity = random.sample(numbers,1)[0]

		# Select target angles (for selecting colour from wheel)
		self.t1_angle = random.randrange(0,360)
		self.t2_angle = random.randrange(0,360)

		while self.t1_angle == self.t2_angle:
			self.t2_angle = random.randrange(0,360)
		
		self.t1_colour = self.t1_wheel.color_from_angle(self.t1_angle) # Assign colouring
		self.t2_colour = self.t2_wheel.color_from_angle(self.t2_angle)

		# Dummy objects to serve as reference point when calculating response error
		self.t1_dummy.fill = self.t1_colour
		self.t2_dummy.fill = self.t2_colour

		self.t1_colouring_rc.display_callback = self.wheel_callback
		self.t1_colouring_rc.display_kwargs = {'wheel': self.t1_wheel}

		self.t1_colouring_rc.color_listener.set_wheel(self.t1_wheel) # Set generated wheel as wheel to use
		self.t1_colouring_rc.color_listener.set_target(self.t1_dummy) # Set dummy as target reference point

		self.t2_colouring_rc.display_callback = self.wheel_callback
		self.t2_colouring_rc.display_kwargs = {'wheel': self.t2_wheel} # Passed as arg w/ calling wheel_callback()

		self.t2_colouring_rc.color_listener.set_wheel(self.t2_wheel)
		self.t2_colouring_rc.color_listener.set_target(self.t2_dummy)
		
		if self.block_type == IDENTITY:
			self.target_duration = self.id_target_duration
			self.mask_duration = self.id_mask_duration
		else:
			self.target_duration = self.col_target_duration
			self.mask_duration = self.col_mask_duration

		# Initialize EventManager
		if P.practicing: # T2 not present during practice blocks
			events = [[self.itoa, "T1_on"]]
			events.append([events[-1][0] + self.target_duration, 'T1_off'])
			events.append([events[-1][0] + self.isi, 'T1_mask_on'])
			events.append([events[-1][0] + self.mask_duration, 'T1_mask_off'])
			events.append([events[-1][0] + 300, 'response_foreperiod'])
		else:
			events = [[self.itoa, 'T1_on']]
			events.append([events[-1][0] + self.target_duration, 'T1_off'])
			events.append([events[-1][0] + self.isi, 'T1_mask_on'])
			events.append([events[-1][0] + self.mask_duration, 'T1_mask_off'])
			events.append([events[-4][0] + self.ttoa, 'T2_on']) # SOA = Time between onset of T1 & T2
			events.append([events[-1][0] + self.target_duration, 'T2_off'])
			events.append([events[-1][0] + self.isi, 'T2_mask_on'])
			events.append([events[-1][0] + self.mask_duration, 'T2_mask_off'])
			events.append([events[-1][0] + 300, 'response_foreperiod'])

		# Stream begins 1000ms after fixation
		for e in events:
			self.evm.register_ticket(ET(e[1],e[0]))

		# Prepare stream
		self.tmtm_stream = self.prep_stream()

		# Present fixation & wait for initiation
		self.present_fixation()

	def trial(self):
		# Hide cursor during trial
		hide_mouse_cursor()

		# Wait some foreperiod before presenting T1
		while self.evm.before('T1_on', True): ui_request()

		# Present T1
		fill()
		blit(self.tmtm_stream['t1_target'], registration=5, location=P.screen_c)
		flip()		

		# Don't do anything during T1 presentation
		while self.evm.before('T1_off', True): ui_request()
		
		# Remove T1
		fill()
		flip()

		# After one refresh rate (how long it takes to remove T1) present mask
		fill()
		blit(self.tmtm_stream['t1_mask'], registration=5, location=P.screen_c)
		flip()

		# Don't do anything during presentation
		while self.evm.before('T1_mask_off', True): ui_request()
		
		# Remove mask
		fill()
		flip()

		# If not practicing, present T2
		if not P.practicing:
			
			# After TTOA is up, present T2
			while self.evm.before('T2_on', True): ui_request()
			
			fill()
			blit(self.tmtm_stream['t2_target'], registration=5, location=P.screen_c)
			flip()

			# Don't do anything during presentation
			while self.evm.before('T2_off', True): ui_request()

			# Remove T2
			fill()
			flip()

			# After one refresh rate, present mask
			fill()
			blit(self.tmtm_stream['t2_mask'], registration=5, location=P.screen_c)
			flip()

			# Don't do anything during presentation
			while self.evm.before('T2_mask_off', True): ui_request()

			# Remove mask
			fill()
			flip()

		# Wait 1/3 second before asking for responses
		while self.evm.before('response_foreperiod', True): ui_request()

		# Request & record responses
		if self.block_type == IDENTITY:
			# Not relevant to identity trials
			t1_response_err, t1_response_err_rt, t2_response_err, t2_response_err_rt = ['NA','NA','NA','NA']

			# Collect identity responses
			self.t1_identity_rc.collect()
			
			if not P.practicing:
				self.t2_identity_rc.collect()

			# Assign to variables returned
			t1_id_response, t1_id_rt = self.t1_identity_rc.keypress_listener.response()
			
			# No T2 present during practice
			if not P.practicing:
					t2_id_response, t2_id_rt = self.t2_identity_rc.keypress_listener.response()
			else:
				t2_id_response, t2_id_rt = ['NA','NA']
			
			# During practice, keep a tally of T1 performance
			if P.practicing:
				if t1_id_response == self.t1_identity:
					self.t1_performance += 1
		
		else: # Colour block
			# Not relevant to colour trials
			t1_id_response, t1_id_rt, t2_id_response, t2_id_rt = ['NA','NA','NA','NA']
			
			# Collect colour responses 
			self.t1_colouring_rc.collect()
			
			if not P.practicing:
				self.t2_colouring_rc.collect()

			# Assign to variables returned
			t1_response_err, t1_response_err_rt = self.t1_colouring_rc.color_listener.response()

			# T2 only presented during test blocks
			if not P.practicing:
				t2_response_err, t2_response_err_rt = self.t2_colouring_rc.color_listener.response()
			else:
				t2_response_err, t2_response_err_rt = ['NA', 'NA']

			if P.practicing:
				# As numeric identities have 9 possible values, similarly the colour wheel can 
				# be thought of as having 9 'bins' (each 40º wide). Colour responses are labelled
				# as 'correct' if their angular error does not exceed 20º in either direction.
				if (abs(t1_response_err) <= 20):
					self.t1_performance += 1

		clear()

		return {
			"practicing": str(P.practicing),
			"block_num": P.block_number,
			"trial_num": P.trial_number,
			"itoa": self.itoa,
			"ttoa": self.ttoa,
			"target_duration": self.target_duration,
			"mask_duration": self.mask_duration,
			"t1_identity": self.t1_identity,
			"t2_identity": self.t2_identity if not P.practicing else 'NA',
			"t1_identity_response": t1_id_response,
			"t1_identity_rt": t1_id_rt,
			"t2_identity_response": t2_id_response ,
			"t2_identity_rt": t2_id_rt,
			"t1_colour": self.t1_colour,
			"t1_angle": self.t1_angle,
			"t1_wheel_rotation": self.t1_wheel.rotation,
			"t2_colour": self.t2_colour if not P.practicing else 'NA',
			"t2_angle": self.t2_angle if not P.practicing else 'NA',
			"t2_wheel_rotation": self.t2_wheel.rotation if not P.practicing else 'NA',
			"t1_ang_err": t1_response_err,
			"t1_colour_rt": t1_response_err_rt,
			"t2_ang_err": t2_response_err,
			"t2_colour_rt": t2_response_err_rt,
			"t1_performance_practice": self.t1_performance if P.practicing else 'NA'
		}

	def trial_clean_up(self):
		# Reset response listeners
		self.t1_identity_rc.keypress_listener.reset()
		self.t2_identity_rc.keypress_listener.reset()

		self.t1_colouring_rc.color_listener.reset()
		self.t2_colouring_rc.color_listener.reset()
		
		# Performance checks during practice
		if not self.practice_complete:
			# First 10 trials considered an 'introductory' run, where no performance check is performed
			if not self.pre_run_complete:
				if self.practice_trial_num == 10:
					
					self.t1_performance = 0
					self.pre_run_complete = True
			else:
				# Every 10 trials, check performance & adjust difficulty as necessary
				if self.practice_trial_num % 10 == 0:
					# If subj accuracy below 80%, 
					if self.t1_performance > 8:
						# Make task harder by adjusting target & mask durations
						if self.block_type == IDENTITY:
							if self.id_target_duration > P.refresh_time:
								self.id_target_duration -= P.refresh_time
								self.id_mask_duration += P.refresh_time
							self.t1_performance = 0
						else:
							if self.col_target_duration > P.refresh_time:
								self.col_target_duration -= P.refresh_time
								self.col_mask_duration += P.refresh_time
							self.t1_performance = 0
					# Otherwise, terminate practice
					else:
						
						self.practice_complete = True
			self.practice_trial_num += 1

	def clean_up(self):
		pass
	
	# --------------------------------- #
	# Project specific helper functions
	# --------------------------------- #

	def present_fixation(self):
		fill()
		blit(self.fixation, location=P.screen_c, registration=5)
		flip()

		any_key()

	def prep_stream(self):
		# Dynamically assign target colouring
		self.txtm.styles['T1'].color = self.t1_colour
		self.txtm.styles['T2'].color = self.t2_colour

		# Generate unique masks for each target
		self.t1_mask = self.generate_mask()
		self.t2_mask = self.generate_mask()

		stream_items = {
			't1_target': message(self.t1_identity, align='center', style='T1', blit_txt=False),
			't1_mask': self.t1_mask,
			't2_target': message(self.t2_identity, align='center', style='T2', blit_txt=False),
			't2_mask': self.t2_mask
		}

		return stream_items



	def wheel_callback(self, wheel):
		# Hide cursor during selection phase
		hide_mouse_cursor()
		
		# Response request msg
		colour_request_msg = self.t1_col_request if wheel == self.t1_wheel else self.t2_col_request
		message_offset = deg_to_px(1.5)
		message_loc = (P.screen_c[0], (P.screen_c[1]-message_offset))

		fill()
		
		# Present appropriate wheel
		if wheel == self.t1_wheel:
			blit(self.t1_wheel, registration=5, location=P.screen_c)
		else:
			blit(self.t2_wheel, registration=5, location=P.screen_c)
		# Present response request
		message(colour_request_msg, location=message_loc, registration=5, blit_txt=True)
		# Present annulus drawbject as cursor
		blit(self.cursor,registration=5,location=mouse_pos())
		
		flip()

	def identity_callback(self, target):
		# Request appropriate identity
		identity_request_msg = self.t1_id_request if target == "T1" else self.t2_id_request
		
		fill()
		message(identity_request_msg, location=P.screen_c, registration=5, blit_txt=True)
		flip()


	def generate_mask(self):
		# Set mask size
		canvas_size = deg_to_px(1.5)
		# Set cell size
		cell_size = canvas_size / 4 # Mask comprised of 16 smaller cells arranged 4x4
		# Each cell has a black outline
		cell_outline_width = deg_to_px(.05)

		# Initialize canvas to be painted w/ mask cells
		canvas = Image.new('RGBA', [canvas_size, canvas_size], (0,0,0,0))

		surface = aggdraw.Draw(canvas)

		# Initialize pen to draw cell outlines
		transparent_pen = aggdraw.Pen((0,0,0),cell_outline_width)

		# Generate cells, arranged in 4x4 array
		for row in [0,1,2,3]:
			for col in [0,1,2,3]:
				# Randomly select colour for each cell
				cell_colour = const_lum[random.randrange(0,360)]
				# Brush to apply colour
				colour_brush = aggdraw.Brush(tuple(cell_colour[:3]))
				# Determine cell boundary coords
				top_left = (row * cell_size, col * cell_size)
				bottom_right = ((row+1) * cell_size, (col+1) * cell_size)
				# Create cell
				surface.rectangle(
					(top_left[0], top_left[1], bottom_right[0], bottom_right[1]),
					transparent_pen,
					colour_brush)
		# Apply cells to mask
		surface.flush()

		return np.asarray(canvas)


