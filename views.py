import sys
import glob
import errno
import json
from pprint import pprint
import re
import csv
import itertools
from itertools import chain
from collections import defaultdict
import operator
from operator import itemgetter
#reload(sys)
#sys.setdefaultencoding('utf8')

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from Fara.models import Document
from Fara.forms import DocumentForm, NonElecForm

#For cropping the pdf file
import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader

#Registering
from Fara.forms import UserForm

#login
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

import subprocess

# Levenshtein distance
from pyxdameraulevenshtein import damerau_levenshtein_distance, normalized_damerau_levenshtein_distance, damerau_levenshtein_distance_ndarray, normalized_damerau_levenshtein_distance_ndarray
import random
import string
import timeit
import numpy as np
import time


# import tasasAPI



#Registration view
def register(request):
	context = RequestContext(request)
	registered = False 

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)

		if user_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()

			registered = True

		else:
			print (user_form.errors)
	else:
		user_form = UserForm()

	return render_to_response(
		'Fara/register.html',
		{'user_form': user_form, 'registered': registered},
		context)

#Login view
def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return render(request, 'Fara/chooseapplication.html', {})
				# return HttpResponseRedirect('/Fara/')
			else:
				return HttpResponse("Your account is disabled")
		else:
			return HttpResponse("Invalid login details supplied")
	else:
		return render(request, 'Fara/login.html', {})

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/Fara/')

def list(request):
	# Handle file upload
	Document.objects.all().delete()
	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)

		if form.is_valid():
			newdoc = Document(docfile = request.FILES['docfile'])
			newdoc.save()
			if 'docfile1' in request.FILES:
				newdoc = Document(docfile = request.FILES['docfile1'])
				newdoc.save()

			# Redirect to the document list after POST
			return HttpResponseRedirect(reverse('Fara.views.show'))
	else:
		form = DocumentForm() # A empty, unbound form

	# Load documents for the list page
	documents = Document.objects.all()
	# Render list page with the documents and the form
	return render_to_response(
		'Fara/list.html',
		{'documents': documents, 'form': form},
		context_instance=RequestContext(request)
	)

def index(request):
	return render_to_response('Fara/index.html')

def show(request):
	documents = Document.objects.all()
	form = DocumentForm()

	#Finding the address of the file on the computer
	address_pdf = "arash"
	address_xml = "arash"
	file_pdf = False
	file_xml = False
	for document in documents:
		if "pdf" in document.docfile.url:
			address_pdf = document.docfile.url
			adder = document.docfile.url
			file_pdf = True
		if "xml" in document.docfile.url:
			address_xml = document.docfile.url
			adder_xml = document.docfile.url
			file_xml = True

	#Finding the absolute path of the file
	if address_pdf != "arash":
		address_pdf = '/home/agobal/Desktop/TASAS/web/Diako' + adder
		address_pdf2 = '/home/agobal/Desktop/TASAS/web/Diako/media/documents/test/1.pdf'

	if address_xml != "arash":
		address_xml = '/home/agobal/Desktop/TASAS/web/Diako' + adder_xml
		address_xml2 = '/home/agobal/Desktop/TASAS/web/Diako/media/documents/test/1.xml'

	#Opening and cropping the pdf file (if we have the pdf file)
	if file_pdf == True:
		input1 = PdfFileReader(open(address_pdf, "rb"))
		output = PdfFileWriter()

		page = input1.getPage(0)
		page.cropBox.lowerLeft = (0, 630)
		page.cropBox.upperRight = (700, 950)
		output.addPage(page)

		outputStream = open(address_pdf2, "wb")
		output.write(outputStream)
		outputStream.close()

		address_pdf2 = '/media/documents/test/1.pdf' 

		if file_xml == True:
			address_pdf2 = '/media/documents/test/1.pdf' 
			subprocess.call(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/hiu6/src/main.py", "-p", address_pdf, "-x", address_xml])
			foldernamepdf = "arash"
			for c in reversed(address_pdf):
				if c == "/":
					break
				else:
					foldernamepdf = c + foldernamepdf
			foldernamepdf = re.sub(".pdfarash", "", foldernamepdf)

			foldernamexml = "arash"
			for c in reversed(address_xml):
				if c == "/":
					break
				else:
					foldernamexml = c + foldernamexml
			foldernamexml = re.sub(".xmlarash", "", foldernamexml)

			diagram_file_address = address_pdf.replace(".pdf", "")
			diagram_file_address = diagram_file_address.replace(foldernamepdf, "")
			address_xml = address_xml.replace(".xml", "") + "/" + foldernamexml + ".json"
			address_pdf = address_pdf.replace(".pdf", "") + "/" + foldernamepdf + ".json"

		if file_xml == False:
			funcinp = [address_pdf, address_xml]
			subprocess.call(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/hiu6/src/main.py", "-p", address_pdf])
			foldername = "arash"
			for c in reversed(address_pdf):
				if c == "/":
					break
				else:
					foldername = c + foldername
			foldername = re.sub(".pdfarash", "", foldername)
			diagram_file_address = address_pdf.replace(".pdf", "")
			diagram_file_address = diagram_file_address.replace(foldername, "")
			address_pdf = address_pdf.replace(".pdf", "") + "/" + foldername + ".json"

	else:
		address_pdf = document.docfile.url
		address_pdf = "/home/agobal/Desktop/TASAS/web/Diako" + address_pdf
		address_pdf2 = '/home/agobal/Desktop/TASAS/web/Diako/media/documents/test/1.pdf'
		if ".json" in address_pdf:
			file_pdf = True



	###################################################################################################
	######################## Extra information ########################################################
	#Reading the full and abbreviated county names from json file     								  #
	with open('/home/agobal/Desktop/TASAS/SList/counties.json') as county_file:                        #
		counties_data = json.load(county_file)                        								  #
	#Reading district number from json file                           								  #
	with open('/home/agobal/Desktop/TASAS/SList/districts.json') as district_file:                     #
		districts_data = json.load(district_file)                     								  #
	#Reading the routes in each district from json file               								  #
	with open('/home/agobal/Desktop/TASAS/SList/routes.json') as routes_file:                          #
		route_data = json.load(routes_file)                           								  #
	with open('/home/agobal/Desktop/TASAS/SList/route_3digit.json') as routes_3digit:                  #
		route_file = json.load(routes_3digit)                         								  #
	#Read the short corrector json file                               								  #
	with open('/home/agobal/Desktop/TASAS/SList/shorts.json') as abbs:                                 #
		shortnames = json.load(abbs)      							  								  #
	#Read the names and abbreviations of cities 					  						      	  #
	with open('/home/agobal/Desktop/TASAS/SList/cities.json') as cityabbs:                             #
		citynames = json.load(cityabbs)			                  								      #
	###################################################################################################

	#Define all the city name abbreviations
	city_name_abbs = []
	for key in citynames:
		for keys in citynames[key]:
			for items in citynames[key][keys]:
				city_name_abbs.append(items)

	#Initializing the road initiators
	road_prefix = ["SR", "STATE ROUTE", "I", "INTERSTATE", "US", "JCT", "RTE"]

	#Match the collision location with sequence list
	if file_pdf == True:
		used_address = address_pdf
	if file_xml == True:
		used_address = address_xml

	with open(used_address) as File:
		report_data = json.load(File)
		#Take out the narrative (if there)
		party_info = report_data["PARTIES"]
		narrative = report_data["NARRATIVE"]
		area_of_impact = []

		if len(narrative) > 1:
			#Find the AREA OF IMPACT lines:
			for i, item in enumerate(narrative):
				item = item.lower()
				if " of impact" in item[0:20]:
					index_aoi = i
					break
				if i == (len(narrative) - 2):
					index_aoi = i
					break

			for i, item in enumerate(narrative):
				item = item.lower()
				if ("cause" in item[0:10]) or ("intoxication narrative" in item):
					index_next = i
					break
				if i == (len(narrative) - 1):
					index_next = i
					break

			for i in range(index_aoi, index_next, 1):
				area_of_impact.append(narrative[i])
			
			# area_of_impact[0] = re.sub(r'.*IMPACT', '', area_of_impact[0])
		else:
			narrative = ["No record of narrative was available in the report", ""]

		#Diagram file address
		diagram_address = []
		if (report_data["DIAGRAM_FILE"] == []):
			diagram_address = ["A"]
		try:
			for item in report_data["DIAGRAM_FILE"]:
				diagram_file_address = re.sub("/home/agobal/Desktop/TASAS/web/Diako", "", diagram_file_address)
				diagram_address.append(diagram_file_address + item)
		except KeyError:
			diagram_address = ["A"]

		#Load the information of first page boxes
		fp_boxes = report_data["LOCATION"]

		#Getting the collision route from first page boxes
		collision_route = str(fp_boxes["ROUTE"])
		collision_route = re.sub(r'([^\s\w]|_)+', ' ', collision_route)

		#Cutting extra information from the box to get the route name
		collision_route1 = 0
		if any(route in collision_route for route in route_file):
			for item in road_prefix:
				if item in collision_route:
					collision_route = collision_route.strip(item)
			collision_route = collision_route.split()[0]
			collision_route1 = collision_route
			if collision_route in route_file:
				collision_route = route_file[collision_route]

		#Reading the gps data
		#First checking if can be converted to float
		gps_invalid = False
		if isinstance(fp_boxes["LATITUDE"],dict) or (fp_boxes["LATITUDE"] == None):
			gps_invalid = True

		if gps_invalid == False:	
			try:
				float(fp_boxes["LATITUDE"])
			except ValueError:
				gps_invalid= True

		gps_text = "a"
		if (gps_invalid == False) and (collision_route.isdigit() == True):
			if fp_boxes["LATITUDE"] != None:
				gpslat = str(fp_boxes["LATITUDE"]).strip()
				gpslong = str(fp_boxes["LONGITUDE"]).strip()
				gpslat = str(gpslat)
				gpslong = str(gpslong)
				gpslat = gpslat.replace(" ", "")
				gpslong = gpslong.replace(" ", "")
				gps_text = subprocess.check_output(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/travis/geo2pm.py", "--lat", gpslat, "--lon", gpslong, "--rng", "10560", "--rt", collision_route])
			if fp_boxes["LATITUDE"] == None:
				gpslat = 0
				gpslong = 0

		if gps_invalid == True:
			gpslat = 0
			gpslong = 0

		gps_text = (str(gps_text))

		if (gps_invalid == True) or ("None" in gps_text) or (collision_route.isdigit() == False):
			gps_postmile = "Could not calculate postmile from GPS"
			gps_route = "0"
		else:
			gps_text = str(gps_text)
			gps_text = gps_text.split("-")
			gps_route = gps_text[1]
			gps_postmile = gps_text[2]
			gps_postmile = gps_postmile[:-3]
		
		#Load the district and county and city information from the boxes
		city_name_full = fp_boxes["CITY"]
		county_name = fp_boxes["COUNTY"]
		county_name = re.sub('[^0-9a-zA-Z]+', ' ', county_name)
		#print (fp_boxes)
		county_abbreviation = counties_data[county_name]
		district = districts_data[county_name]
		#Read the json sequence lists
		seq_list_file = "/home/agobal/Desktop/TASAS/SList/" + "D" + district + ".json"
		autocomplete_file = "./autocomplete/d" + district + "js.json"
		with open(seq_list_file) as sequence_list:
			seq_lst = json.load(sequence_list)

		#Getting the postmile information from the milepost box
		milepost_text = fp_boxes["MILEPOST INFO TEXT"]
		if (milepost_text != None): 
			milepost_text = milepost_text.split()
			if len(milepost_text) > 1:
				distance_to_milepost_marker = 0
				if len(milepost_text) > 1:
					distance_to_milepost_marker = 0
					# if fp_boxes["MILEPOST INFORMATION"] != "x":
					distance_to_milepost_marker = float(milepost_text[0])
					milepost_text.remove(milepost_text[0])
					if milepost_text[0] in ["FEET", "FET", "FT"]:
						distance_to_milepost_marker = distance_to_milepost_marker/5280
					milepost_text.remove(milepost_text[0])
					dot_direction = milepost_text[0]
					if milepost_text[0] in ["SOUTH", "WEST", "S", "W"]:
						distance_to_milepost_marker = -distance_to_milepost_marker
					postmile_marker = milepost_text[-1]

				try:
					float(postmile_marker)
				except ValueError:
					for i in postmile_marker:
						try:
							float(i)
						except ValueError:
							postmile_marker = postmile_marker.strip(i)
				try:
					postmile_marker = float(postmile_marker)
				except ValueError:
					collision_route = str(collision_route)
					county_abbreviation = str(county_abbreviation)
					postmile_marker = str(postmile_marker)
					if str(int(collision_route)) in postmile_marker[0:3]:
						postmile_marker = postmile_marker.replace(str(int(collision_route)), '')
					if county_abbreviation in postmile_marker:
						postmile_marker = postmile_marker.replace(county_abbreviation, '')
					if "MPM" in postmile_marker:
						postmile_marker = postmile_marker.replace("MPM", '')
					postmile_marker = re.sub("-", "", postmile_marker)
					postmile_marker = re.sub("/", "", postmile_marker)
					postmile_marker = float(postmile_marker)
				
				distance_to_milepost_marker = float(distance_to_milepost_marker)
				postmile_marker_loc = postmile_marker + distance_to_milepost_marker
			else:
				postmile_marker_loc = None
		else:
			postmile_marker_loc = None

		#Getting the postmile information from the boxes
		Intersections = fp_boxes["SECONDARY INFORMATION"]
		direction_of_travel = Intersections["DIRECTION"]
		intersection_text = fp_boxes["SECONDARY INFORMATION TEXT"]
		start_end = False
		# if file_pdf == True:
		intersection_text = intersection_text.split()
		# Appending LT and RT to intersection text
		print (direction_of_travel)
		if direction_of_travel in ["NB", "N/B", "EB", "E/B"]:
			intersection_text.append("RT")
		else:
			intersection_text.append("LT")
		print (intersection_text)
		distance_to_intersection = 0
		if len(intersection_text) > 1:
			if intersection_text[1] in ["FEET", "FET", "FT", "MILE(S)", "MILE", "MILES"]:
				dtt = intersection_text[0]
				if dtt[0] == ".":
					dtt = "0" + dtt
				distance_to_intersection = float(dtt)
				intersection_text.remove(intersection_text[0])
				if intersection_text[0] in ["FEET", "FET", "FT"]:
					distance_to_intersection = distance_to_intersection/5280
				intersection_text.remove(intersection_text[0])
				dotdirection = intersection_text[0]
				if intersection_text[0] in ["SOUTH", "WEST", "S", "W"]:
					distance_to_intersection = -distance_to_intersection
				elif intersection_text[0] in ["EAST", "NORTH", "E", "N"]:
					start_end = True
				intersection_text.pop(0)
				intersection_text.pop(0)
		else:
			distance_to_intersection = 0
			dotdirection = "NORTH"
		# print (distance_to_intersection)
		#Remove all non alphanumeric characters from the query and split it
		for i in range(len(intersection_text)):
			if "-" in intersection_text[i]:
				intersection_text.append(re.sub("-", "", intersection_text[i]))
			intersection_text[i] = re.sub(r'\W+', ' ', intersection_text[i])
			item = intersection_text[i].split()
			intersection_text.extend(item)
		#Append the extra words for common stuff
		loop_length = len(intersection_text)
		for i in range(loop_length):
			if intersection_text[i] in shortnames:
				intersection_text.extend(shortnames[intersection_text[i]])
		
		#Append OC and UC to the list
		bool_indicator = 0
		for item in intersection_text:
			if item in ["OC", "UC", "OVERCROSSING", "UNDERCROSSING"]:
				bool_indicator = 1
		if bool_indicator == 0:
			intersection_text.extend(["OC", "UC", "OVERCROSSING", "UNDERCROSSING"])

		starting = 0
		if (("COUNTY" in intersection_text) and ("LINE" in intersection_text)) or (("CO" in intersection_text) and ("LN" in intersection_text)):
			if start_end == True:
				starting = 1
			else:
				starting = 2
		# print ("Query:")
		# print (intersection_text)
		# Search for the query through the sequence list
		district_roads = []
		for item in route_data[district]:
			district_roads.append(str(int(item)))

		if (collision_route1 in route_file) and (collision_route1 in district_roads):
			result = seq_lst[collision_route][county_abbreviation]
		else:
			return render_to_response('Fara/nohighway.html')

		# Finding the lines from sequence listing around the gps postmile and mpm postmile
		pm_seqlst = []
		for i in range(len(result)):
			line = result[i]
			pm_width = 0.0
			for j in range(len(line)):
				word = line[j]
				####################################3333
				if start_end == True:
					if (("OC" in line) or ("UC" in line)) and ("END" in line) and ("BR" in line):
						if (len(word) == 6) and (word[2] == "."):
							pm_width = float(word)
				########################################
				if (len(word) == 7) and (word[3] == "."):
					try:
						word2 = float(word)
						# pm_seqlst.append(word2)
					except ValueError:
						continue
			print (word2 + pm_width)
			word2 = word2 + pm_width
			pm_seqlst.append(word2)

		gps_seq_list = []
		if "Could" in gps_postmile:
			print (" ")
		else:
			if gps_postmile[0].isalpha():
				gps_postmile = gps_postmile[1:]
			if gps_postmile[-1].isalpha():
				gps_postmile = gps_postmile[:-1]
			for i in range(len(pm_seqlst)):
				if (i != 0) and (i != (len(pm_seqlst) - 1)):
					if (float(gps_postmile) >= float(pm_seqlst[i])) and (float(gps_postmile) < float(pm_seqlst[i + 1])):
						goal_num = i
						gpsseq1 = county_abbreviation + " " + collision_route + " " + " ".join(result[goal_num])
						gpsseq2 = county_abbreviation + " " + collision_route + " " + " ".join(result[goal_num + 1])
						gps_seq_list = [gpsseq1, gpsseq2]

		mpm_seq_list = []
		if postmile_marker_loc != None:
			for i in range(len(pm_seqlst)):
				if (i != 0) and (i != (len(pm_seqlst) - 1)):
					if (float(postmile_marker_loc) >= float(pm_seqlst[i])) and (float(postmile_marker_loc) < float(pm_seqlst[i + 1])):
						goal_num = i
						mpmseq1 = county_abbreviation + " " + collision_route + " " + " ".join(result[goal_num])
						mpmseq2 = county_abbreviation + " " + collision_route + " " + " ".join(result[goal_num + 1])
						mpm_seq_list = [mpmseq1, mpmseq2]

		##################################################################
		result_length = len(result)
		# print(result)
		# print (intersection_text)
		for i, item in enumerate(intersection_text):
			intersection_text[i] = item.lower()
		intersection_text2 = np.array(intersection_text)

		score = [1 for x in range(result_length)]
		if starting == 1:
			score[0] = score[0] + 3
		elif starting == 2:
			score[-1] = score[-1] + 3

		for i in range(result_length):
			line = result[i]
			try:
				next_line = result[i + 1]
				next_line2 = result[i + 2]
			except IndexError:
				next_line = line
			if ("END" in next_line) and ("BR" in next_line):
				result[i] = line + next_line
			if ("END" in next_line2) and ("BR" in next_line2):
				result[i] = line + next_line2
			#if the city is right
			if line == []:
				line.append("1")
			# if line[0] in city_name_abbs:
			# 	city_name = citynames[district][county_abbreviation][line[0]]
				# if city_name == city_name_full:
				# 	score[i] = score[i] + 0.5
			#if other keywords are right
			for item in line:
				# if item in intersection_text:
				if min(normalized_damerau_levenshtein_distance_ndarray(item.lower(), intersection_text2)) < 0.25:
					if item in shortnames:
						score[i] = score[i] + 0.05
					else:
						score[i] = score[i] + 1
					for t in line:
						if t in ["OFF", "ON", "NB", "SB", "EB", "WB", "NBOFFTO", "SBOFFTO", "SBON", "NBON", "NBOFF", "SBOFF"]:
							score[i] = score[i] - 0.1
				else:
					if (len(item) > 2.0):
						score[i] = score[i] - 0.01 

		#print ("Result:")
		max_score = max(score)
		result_list = []
		score_list = []
		for i in range(result_length):
			if (abs(score[i] - max_score) < 1.0 and score[i] > 1.0):
				#print (result[i])
				result_list.append(result[i])
				score_list.append(score[i])

		collision_route = int(collision_route)

		pm_w2 = [0]*len(result_list) ########################################
		prefixx = [0]*len(result_list)
		postmiles = [0]*len(result_list)
		for j in range(len(result_list)):
			finalresult = result_list[j]
			mpm_marker = False;################################
			width_marker = False;###############################
			for i in range(len(finalresult)):
				num = finalresult[i]
				###############################################3
				if (start_end == True) and (width_marker == False): #########################
					if (("OC" in finalresult) or ("UC" in finalresult)) and ("END" in finalresult) and ("BR" in finalresult):##########################
						if (len(num) == 6) and (num[2] == "."):####################
							pm_w2[j] = float(num)#################################
							width_marker = True
				###############################################3
				if mpm_marker == False:####################################
					if (len(num) == 7 and num[3] == "." and i != 0):
						if len(finalresult[i - 1]) == 1:
							prefixx[j] = finalresult[i - 1]
						else:
							prefixx[j] = ""
						postmiles[j] = finalresult[i]
						mpm_marker = True
					if (len(num) == 7 and num[3] == "." and i == 0):
						prefixx[j] = ""
						postmiles[j] = finalresult[i]
						mpm_marker = True

			valid_postmiles = True
			try:
				float(postmiles[j])
			except ValueError:
				valid_postmiles= False

			if valid_postmiles == False:
				postmiles[j] = postmiles[j - 1]
			else:
				postmiles[j] = float(postmiles[j])
			postmiles[j] = postmiles[j] + pm_w2[j] + distance_to_intersection#######################################3

	#Using travis's app
	lat = []
	longi = []
	for pm in postmiles:
		if pm >= 0:
			loc3_query = county_abbreviation + "-" + str(collision_route) + "-" + str(pm)
			gps_loc3 = subprocess.check_output(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/travis/pm2geo.py", "--crp", loc3_query])
			gps_loc3 = str(gps_loc3)
			if "None" in gps_loc3:
				loc3_query = county_abbreviation + "-" + str(collision_route) + "-" + "R" + str(pm)
				gps_loc3 = subprocess.check_output(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/travis/pm2geo.py", "--crp", loc3_query])
				gps_loc3 = str(gps_loc3)
			if "None" in gps_loc3:
				loc3_query = county_abbreviation + "-" + str(collision_route) + "-" + "L" + str(pm)
				gps_loc3 = subprocess.check_output(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/travis/pm2geo.py", "--crp", loc3_query])
				gps_loc3 = str(gps_loc3)
			if "None" in gps_loc3:
				lat.append("0")
				longi.append("0")
			else:
				gps_loc3 = gps_loc3.split(",")
				latit = gps_loc3[0]
				latit = latit[2:]
				logit = gps_loc3[1]
				logit = logit[:-3]
				lat.append(latit)
				longi.append(logit)
		else:
			lat.append("0")
			longi.append("0")
		
	# Doing the AOI part:
	# area_of_impact_str = " ".join(area_of_impact)
	# area_of_impact_str = area_of_impact_str.replace('\n',' ')
	# area_of_impact_str = area_of_impact_str.replace("'",' feet')
	# area_of_impact_str = area_of_impact_str.replace('"',' inches')
	# area_of_impact_str = area_of_impact_str.split(" ")
	# area_of_impact_str = [i for i in area_of_impact_str if i != '']
	# AOI_list = []
	# area_of_impact_list = []

	# for item in area_of_impact_str:
	# 	if ("AOI" in item) or ("A.O.I" in item):
	# 		area_of_impact_list.append(AOI_list)
	# 		AOI_list = []
	# 		AOI_list.append(item)
	# 	else:
	# 		AOI_list.append(item)
	# area_of_impact_list.append(AOI_list)
	# print (area_of_impact_list)
	# area_of_impact_list = [i for i in area_of_impact_list if i != []]
	
	# #Process the aoi data
	# aoi_list = []
	# for item in area_of_impact_list:
	# 	print(item)
	# 	for index, things in item:
	# 		if index != 0:
	# 			if (things in ["feet", "miles", "mile"]) and (item[index - 1].isfloat() == True):
	# 				aoi_list.append(item[(index-1):])
	# 				break
	# print (aoi_list)

	#Using travis's app
	if (postmile_marker_loc) and (postmile_marker_loc >= 0):
		loc2_query = county_abbreviation + "-" + str(collision_route) + "-" + str(postmile_marker_loc)
		gps_loc2 = subprocess.check_output(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/travis/pm2geo.py", "--crp", loc2_query])
		gps_loc2 = str(gps_loc2)

		if "None" in gps_loc2:
			loc2_query = county_abbreviation + "-" + str(collision_route) + "-" + "R" + str(postmile_marker_loc)
			gps_loc2 = subprocess.check_output(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/travis/pm2geo.py", "--crp", loc2_query])
			gps_loc2 = str(gps_loc2)

		if "None" in gps_loc2:
			loc2_query = county_abbreviation + "-" + str(collision_route) + "-" + "L" + str(postmile_marker_loc)
			gps_loc2 = subprocess.check_output(["python", "/home/agobal/Desktop/TASAS/web/Diako/Fara/travis/pm2geo.py", "--crp", loc2_query])
			gps_loc2 = str(gps_loc2)


		gps_loc2 = gps_loc2.split(",")
		latit = gps_loc2[0]
		latit = latit[2:]
		logit = gps_loc2[1]
		logit = logit[:-3]
		pm_lat = latit
		pm_long = logit
	else:
		pm_lat = None
		pm_long = None

	#Clean up the score list
	for i in range(len(score_list)):
		score_list[i] = float(score_list[i])*100
		score_list[i] = int(score_list[i])
		score_list[i] = float(score_list[i])/100

	#limit the accuracy of postmile infor
	for i in range(len(postmiles)):
		postmiles[i] = float(int(1000*postmiles[i]))/1000
	#Clean up the result list:
	result_list2 = []
	for item in result_list:
		result_list2.append(' '.join(item))
	loop_length_html = len(postmiles)
	#Mark each match with a letter from A to Z
	letter_strings = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	for i in range(0, 10):
		letter_strings = letter_strings + letter_strings

	#Make a dict to contain all the info for the results
	letter_strings2 = [0]*len(postmiles)
	final_result_dict = {}
	for i in range(len(postmiles)):
		item = {"highway": collision_route, "score": score_list[i], "verbage": result_list2[i], "postmile": postmiles[i], "postmile_lat": lat[i], "postmile_long": longi[i]}
		final_result_dict[i] = item
		letter_strings2[i] = letter_strings[i]

	final_result_dict = sorted(final_result_dict.items(),key=lambda x: x[1]['score'],reverse=True)
	final_result_dict2 = {}
	for i in range(len(postmiles)):
		final_result_dict2[i] = [letter_strings2[i], final_result_dict[i][1]]

	##########################################################################################################################################################################33
	################## Intersection/ramp #############################################################################################################################33
	##########################################################################################################################################################################33
	# Intersections = fp_boxes["SECONDARY INFORMATION"]

	intersection = Intersections["INTERSECTION"]

	if intersection == "x":
		intersection_num = 1

	##########################################################################################################################################################################33
	################## OTHER TASAS DATA ANALYSIS #############################################################################################################################33
	##########################################################################################################################################################################33
	with open(used_address) as File:
		report_data = json.load(File)
		temp_address = used_address.split("/")
		csv_filename = temp_address[-2]
		temp_address = temp_address[-1]
		# csv_address = used_address.strip(temp_address) + csv_filename + ".csv"
		csv_address = "/home/agobal/Desktop/TASAS/web/Diako/media/documents/tasas.csv"

		csv_other = report_data["OTHER"]
		csv_hour_of_day = csv_other["TIME"]
		csv_coding = report_data["CODING"]

		pcf = csv_coding["PRIMARY COLLISION FACTOR"]
		pcff = []
		for keys in pcf:
			pcff.append(keys)
		# print(pcff)

		tasas = {'ID':csv_filename}
		tasas['TIME'] = csv_hour_of_day[0:2] + ':' + csv_hour_of_day[2:4]
		tasas['DI'] = district
		tasas['RO'] = collision_route
		tasas['CO'] = county_abbreviation
		tasas['DTE'] = csv_other["DATE"]
		try:
			tasas['PM'] = postmiles[0]
		except IndexError:
			tasas['PM'] = "None"
		if csv_coding["TYPE OF COLLISION"] is not None:
			tasas['TOC'] = csv_coding["TYPE OF COLLISION"][0]
		tasas['PCF'] = pcff[-1][0]
		if csv_coding["ROADWAY CONDITION(S)"][0] is not None:
			tasas['RC'] = csv_coding["ROADWAY CONDITION(S)"][0][0]
		if csv_coding["ROADWAY CONDITION(S)"][0] is not None:
			tasas['RS'] = csv_coding["ROADWAY SURFACE"][0]
		if csv_coding["WEATHER"][0] is not None:
			tasas['WEA'] = csv_coding["WEATHER"][0][0]
		if csv_coding["LIGHTING"] is not None:
			tasas['LIGHT'] = csv_coding["LIGHTING"][0]

		# print (tasas)
		csv_columns = ['ID', 'PDF NAME', 'RO', 'CO', 'PM', 'DTE', 'TIME', 'HG', 'AC', 'MT', 'BT', 'NOLL', 'NOLR', 'PC', 'FT', 'IRAL', 'SOH', 'DOW', 'YR', 'DI', 'AN', 'PCF', 'WEA', 'LIGHT', 'RS', 'RC', 'ROWC', 'TOC', 'NOMVI']

		dict_data = [
			tasas
			]
		WriteDictToCSV(csv_address,csv_columns,dict_data)

	# print (diagram_address)

	return render_to_response(
        'Fara/show3.html',
        {'pdflocation': address_pdf2, 'documents': documents, 'form': form, 'result': final_result_dict2, 'gpslat': gpslat, 'gpslong': gpslong, 'gpsroute': gps_route, 'gpspostmile': gps_postmile, 'loop_length':loop_length_html, 'text': collision_route, 'mpm': postmile_marker_loc, 'pm_lat':pm_lat, 'pm_long':pm_long, 'narrative':narrative, 'area_of_impact':area_of_impact, 'json_file': autocomplete_file, 'gps_close': gps_seq_list, 'mpm_close': mpm_seq_list, 'diag_address': diagram_address[0], 'milepost_info_text': fp_boxes["MILEPOST INFO TEXT"], 'secondary_info_text': fp_boxes["SECONDARY INFORMATION TEXT"], 'csv_file_address':csv_address, 'party_info': party_info, 'countyname': county_name},
        # {'documents': documents, 'form': form, 'highway': collision_route, 'result': result_list2, 'score': score_list, 'postmile': postmiles, 'latitude': lat, 'longitude': longi, 'gpslat': gpslat, 'gpslong': gpslong, 'dot': dotdirection, 'loop_length':loop_length_html},
        context_instance=RequestContext(request)
    )	

def send_file(request):
	import os, tempfile, zipfile
	from django.core.servers.basehttp import FileWrapper
	from django.conf import settings
	import mimetypes
	filename     = "/home/agobal/Desktop/TASAS/web/Diako/media/documents/tasas.csv" # Select your file here.
	download_name ="tasas.csv"
	wrapper      = FileWrapper(open(filename))
	content_type = mimetypes.guess_type(filename)[0]
	response     = HttpResponse(wrapper,content_type=content_type)
	response['Content-Length']      = os.path.getsize(filename)    
	response['Content-Disposition'] = "attachment; filename=%s"%download_name
	return response

def WriteDictToCSV(csv_file,csv_columns,dict_data):
	with open(csv_file, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
		writer.writeheader()
		for data in dict_data:
			writer.writerow(data)
	return     

def NonElecShow(request):
	#Copying the written stuff into the memory
	if request.method == 'POST':
		form = NonElecForm(request.POST)
		if form.is_valid():
			COUNTY = form.cleaned_data.get('COUNTY')
			CITY = form.cleaned_data.get('CITY')
			ROUTE = form.cleaned_data.get('ROUTE')
			MILEPOST_INFORMATION = form.cleaned_data.get('MILEPOST_INFORMATION')
			SECONDARY_INFORMATION = form.cleaned_data.get('SECONDARY_INFORMATION')
			LATITUDE = form.cleaned_data.get('LATITUDE')
			LONGITUDE = form.cleaned_data.get('LONGITUDE')


		###################################################################################################
		######################## Extra information ########################################################
		#Reading the full and abbreviated county names from json file     								  #
		with open('/home/agobal/Desktop/TASAS/SList/counties.json') as county_file:                        #
			counties_data = json.load(county_file)                        								  #
		#Reading district number from json file                           								  #
		with open('/home/agobal/Desktop/TASAS/SList/districts.json') as district_file:                     #
			districts_data = json.load(district_file)                     								  #
		#Reading the routes in each district from json file               								  #
		with open('/home/agobal/Desktop/TASAS/SList/routes.json') as routes_file:                          #
			route_data = json.load(routes_file)                           								  #
		with open('/home/agobal/Desktop/TASAS/SList/route_3digit.json') as routes_3digit:                  #
			route_file = json.load(routes_3digit)                         								  #
		#Read the short corrector json file                               								  #
		with open('/home/agobal/Desktop/TASAS/SList/shorts.json') as abbs:                                 #
			shortnames = json.load(abbs)      							  								  #
		#Read the names and abbreviations of cities 					  						      	  #
		with open('/home/agobal/Desktop/TASAS/SList/cities.json') as cityabbs:                             #
			citynames = json.load(cityabbs)			                  								      #
		###################################################################################################

		#Define all the city name abbreviations
		city_name_abbs = []
		for key in citynames:
			for keys in citynames[key]:
				for items in citynames[key][keys]:
					city_name_abbs.append(items)

		#Initializing the road initiators
		road_prefix = ["SR", "STATE ROUTE", "I", "INTERSTATE", "US", "JCT", "RTE"]

		#Match the collision location with sequence list

		#Reading the gps data
		if LATITUDE != None:
			gpslat = LATITUDE.strip()
			gpslong = LONGITUDE.strip()
		if LATITUDE == None:
			gpslat = 0
			gpslong = 0

		#Load the district and county and city information from the boxes
		city_name_full = CITY
		county_name = COUNTY

		county_abbreviation = counties_data[county_name]
		district = districts_data[county_name]
		#Read the json sequence lists
		seq_list_file = "/home/agobal/Desktop/TASAS/SList/" + "D" + district + ".json"
		with open(seq_list_file) as sequence_list:
			seq_lst = json.load(sequence_list)

		#Getting the collision route from first page boxes
		collision_route = ROUTE
		collision_route = re.sub(r'([^\s\w]|_)+', ' ', collision_route)

		#Cutting extra information from the box to get the route name
		collision_route1 = 0
		if any(route in collision_route for route in route_file):
			for item in road_prefix:
				if item in collision_route:
					collision_route = collision_route.strip(item)
			collision_route = collision_route.split()[0]
			collision_route1 = collision_route
			if collision_route in route_file:
				collision_route = route_file[collision_route]

		#Getting the postmile information from the milepost box
		milepost_text = MILEPOST_INFORMATION
		if (milepost_text != None): 
			milepost_text = milepost_text.split()
			distance_to_milepost_marker = 0
			if MILEPOST_INFORMATION != "x":
				distance_to_milepost_marker = float(milepost_text[0])
				milepost_text.remove(milepost_text[0])
				if milepost_text[0] in ["FEET", "FT", "FET"]:
					distance_to_milepost_marker = distance_to_milepost_marker/5280
				milepost_text.remove(milepost_text[0])
				dot_direction = milepost_text[0]
				if milepost_text[0] in ["SOUTH", "WEST", "S", "W"]:
					distance_to_milepost_marker = -distance_to_milepost_marker
				postmile_marker = milepost_text[-1]
			postmile_marker = float(postmile_marker)
			distance_to_milepost_marker = float(distance_to_milepost_marker)
			postmile_marker_loc = postmile_marker + distance_to_milepost_marker
		else:
			postmile_marker_loc = None

		#Getting the postmile information from the boxes
		intersection_text = SECONDARY_INFORMATION
		intersection_text = intersection_text.split()
		distance_to_intersection = 0
		if intersection_text[1] in ["FEET", "MILE(S)", "MILE", "FET", "FT"]:
			distance_to_intersection = float(intersection_text[0])
			intersection_text.remove(intersection_text[0])
			if intersection_text[0] in ["FEET", "FET", "FT"]:
				distance_to_intersection = distance_to_intersection/5280
			intersection_text.remove(intersection_text[0])
			dotdirection = intersection_text[0]
			if intersection_text[0] in ["SOUTH", "WEST", "S", "W"]:
				distance_to_intersection = -distance_to_intersection
			intersection_text.remove(intersection_text[0])
			intersection_text.remove(intersection_text[0])
		else:
			distance_to_intersection = 0
			dotdirection = "NORTH"
		#Remove all non alphanumeric characters from the query and split it
		for i in range(len(intersection_text)):
			intersection_text[i] = re.sub(r'\W+', ' ', intersection_text[i])
			item = intersection_text[i].split()
			intersection_text.extend(item)
		#Append the extra words for common stuff
		loop_length = len(intersection_text)
		for i in range(loop_length):
			if intersection_text[i] in shortnames:
				intersection_text.extend(shortnames[intersection_text[i]])

		#Append OC and UC to the list
		bool_indicator = 0
		for item in intersection_text:
			if item in ["OC", "UC", "OVERCROSSING", "UNDERCROSSING"]:
				bool_indicator = 1
		if bool_indicator == 0:
			intersection_text.extend(["OC", "UC", "OVERCROSSING", "UNDERCROSSING"])
		#print ("Query:")
		#print (intersection_text)
		#Search for the query through the sequence list
		if collision_route1 in route_file:
			result = seq_lst[collision_route][county_abbreviation]
		else:
			return render_to_response('Fara/nohighway.html')

		result_length = len(result)
		score = [1 for x in range(result_length)]
		for i in range(result_length):
			line = result[i]
			#if the city is right
			if line == []:
				line.append("1")
			if line[0] in city_name_abbs:
				city_name = citynames[district][county_abbreviation][line[0]]
				if city_name == city_name_full:
					score[i] = score[i] + 0.5
			#if other keywords are right
			for item in line:
				if item in intersection_text:
					if item in shortnames:
						score[i] = score[i] + 0.1
					else:
						score[i] = score[i] + 1
					for t in line:
						if t in ["OFF", "ON", "NB", "SB", "EB", "WB", "NBOFFTO", "SBOFFTO", "SBON", "NBON"]:
							score[i] = score[i] - 0.01
				else:
					if (len(item) > 2.0):
						score[i] = score[i] - 0.01 

		#print ("Result:")
		max_score = max(score)
		result_list = []
		score_list = []
		for i in range(result_length):
			if abs(score[i] - max_score) < 1.0:
				#print (result[i])
				result_list.append(result[i])
				score_list.append(score[i])

		collision_route = int(collision_route)

		prefixx = [0]*len(result_list)
		postmiles = [0]*len(result_list)
		for j in range(len(result_list)):
			finalresult = result_list[j]
			for i in range(len(finalresult)):
				num = finalresult[i]
				if (len(num) == 7 and num[3] == "." and i != 0):
					if len(finalresult[i - 1]) == 1:
						prefixx[j] = finalresult[i - 1]
					else:
						prefixx[j] = ""
					postmiles[j] = finalresult[i]
				if (len(num) == 7 and num[3] == "." and i == 0):
					prefixx[j] = ""
					postmiles[j] = finalresult[i]
			postmiles[j] = float(postmiles[j])
			postmiles[j] = postmiles[j] + distance_to_intersection

		#Calculating GPS locations for the LOC3
		lat = []
		longi = []
		path = '/home/agobal/Desktop/TASAS/web/Diako/Fara/postmiles/' + county_abbreviation + '/' + str(collision_route) + '.json'
		with open(path) as lookuptable:
			lookup = json.load(lookuptable)

		l = len(lookup["postmile"])
		for pm in postmiles:
			sm = lookup["postmile"][0]
			mm = lookup["postmile"][l - 1]
			if pm > mm or pm < sm:
				lat.append(0)
				longi.append(0)
				continue
			for i in range(0, l-1):
				# sm = lookup["postmile"][0]
				# mm = lookup["postmile"][l - 1]
				# if pm > mm:
				# 	break
				if lookup["postmile"][i] < pm and lookup["postmile"][i] >= sm:
					sm = lookup["postmile"][i]
					ii = i
				if lookup["postmile"][i] > pm and lookup["postmile"][i] <= mm:
					mm = lookup["postmile"][i]
					iii = i
			b = (pm - sm)/(mm - sm)
			a = 1 - b
			# if pm > mm:
			# 	lat.append(0)
			# 	longi.append(0)
			# else:
			lat.append(lookup["latitude"][ii]*a + lookup["latitude"][iii]*b)
			longi.append(lookup["longitude"][ii]*a + lookup["longitude"][iii]*b)

		#Calculating GPS locations for the LOC2
		sm = lookup["postmile"][0]
		mm = lookup["postmile"][l - 1]
		if postmile_marker_loc:
			if postmile_marker_loc > mm or pm < sm:
					pm_lat = 0
					pm_long = 0
			else:
				for i in range(0, l-1):
					if lookup["postmile"][i] < postmile_marker_loc and lookup["postmile"][i] >= sm:
						sm = lookup["postmile"][i]
						ii = i
					if lookup["postmile"][i] > postmile_marker_loc and lookup["postmile"][i] <= mm:
						mm = lookup["postmile"][i]
						iii = i
				b = (postmile_marker_loc - sm)/(mm - sm)
				a = 1 - b
				pm_lat = lookup["latitude"][ii]*a + lookup["latitude"][iii]*b
				pm_long = lookup["longitude"][ii]*a + lookup["longitude"][iii]*b
		else:
			pm_lat = None
			pm_long = None

		#Clean up the score list
		for i in range(len(score_list)):
			score_list[i] = float(score_list[i])*100
			score_list[i] = int(score_list[i])
			score_list[i] = float(score_list[i])/100

		#limit the accuracy of postmile infor
		for i in range(len(postmiles)):
			postmiles[i] = float(int(1000*postmiles[i]))/1000
		#Clean up the result list:
		result_list2 = []
		for item in result_list:
			result_list2.append(' '.join(item))
		loop_length_html = len(postmiles)
		#Mark each match with a letter from A to Z
		letter_strings = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		for i in range(0, 10):
			letter_strings = letter_strings + letter_strings

		#Make a dict to contain all the info for the results
		letter_strings2 = [0]*len(postmiles)
		final_result_dict = {}
		for i in range(len(postmiles)):
			item = {"highway": collision_route, "score": score_list[i], "verbage": result_list2[i], "postmile": postmiles[i], "postmile_lat": lat[i], "postmile_long": longi[i]}
			final_result_dict[i] = item
			letter_strings2[i] = letter_strings[i]

		final_result_dict = sorted(final_result_dict.items(),key=lambda x: x[1]['score'],reverse=True)
		final_result_dict2 = {}
		for i in range(len(postmiles)):
			final_result_dict2[i] = [letter_strings2[i], final_result_dict[i][1]]

		# mpm_rounded = postmile_marker_loc*1000
		# postmile_marker_loc = int(mpm_rounded)
		# postmile_marker_loc = float(postmile_marker_loc)
		# postmile_marker_loc = postmile_marker_loc/1000

		return render_to_response(
	        'Fara/show2_nonelec.html',
	        {'form': form, 'result': final_result_dict2, 'gpslat': gpslat, 'gpslong': gpslong, 'loop_length':loop_length_html, 'text': collision_route, 'mpm': postmile_marker_loc, 'pm_lat':pm_lat, 'pm_long':pm_long},
	        RequestContext(request, {})
	    )	
	else:
		form = NonElecForm()
		return render_to_response('Fara/nonelec.html',{'form': form}, context_instance = RequestContext(request))