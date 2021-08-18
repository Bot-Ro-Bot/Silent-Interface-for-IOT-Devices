from flask import Flask, render_template, request, jsonify
import logging

import requests

# import tensorflow as tf
# from tensorflow import keras
import numpy as np

from emg_lib import *

SENTENCES =["अबको समय सुनाउ","एउटा सङ्गित बजाउ","आजको मौसम बताउ","बत्तिको अवस्था बदल","पङ्खाको स्तिथी बदल"]

from sklearn.preprocessing import LabelEncoder
labelencoder_y = LabelEncoder()
Y_encode = labelencoder_y.fit_transform(SENTENCES)

app = Flask(__name__)
app.debug = True
# app.run(host="0.0.0.0")

stringPrediction = "Xaina"
makePrediction = False
lightState = False

predictionCount = 0

emgDataToKaggle = None

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/prediction')
def prediction():
	global predictionCount
	# TODO:replace putsomeWords with predicted words from the model 
	return jsonify(result= str(predictionCount) + stringPrediction)

@app.route('/getEmg', methods=['POST', 'GET'])
def getEmg():	#gets emg data from the local host
	global stringPrediction
	global emgDataToKaggle
	global makePrediction
	if request.method == 'POST':
		prediction = request.json
		if 'sentence' in prediction:
			stringPrediction = prediction['sentence']


	elif request.method == 'GET':
		if makePrediction:
			return jsonify(result = "test")#emgDataToKaggle.tolist())
		else:
			return jsonify(result = "None")
	return "msgFromget"

@app.route('/takeEmg', methods=['POST'])
def takeEmg():	# takes emg and predict words
	global predictionCount
	global emgDataToKaggle
	global makePrediction
	emgData = request.json
	if 'resetCount' in  emgData :
		predictionCount = 0

	implementModel = False
	if 'emg' in emgData:
		predictionCount += 1
		print(type(emgData))
		print(type(emgData['emg']))
		print(len(emgData['emg']))
		
		channel_data = np.array(emgData['emg'])	#send channel data 
		rawdata = []
		rawdata.append(channel_data)
		filteredData = signal_pipeline(rawdata)
		emgDataToKaggle = filteredData.copy()

		# dataFeature = feature_pipeline(filteredData)
		# dataFeature = reshapeChannelIndexToLast(dataFeature)
		makePrediction = True

		print(filteredData.shape)
		print("EXTRACTING Success")

		# if implementModel:
		# 	# TODO : need to test with a trained model and real data ... 
		# 	# pass to a trained model
		# 	model = tf.keras.models.load_model("<modelname>.h5")
		# 	# model.summary()
		# 	prediction = model.predict_classes(dataFeature)
		# 	print(prediction)
		# 	stringPrediction = list(labelencoder_y.inverse_transform(list(prediction)))
		# 	makePrediction = True
		    # return the predicted result to the web interface. 
	return "Success"

# SENTENCES =["अबको समय सुनाउ","एउटा सङ्गित बजाउ","आजको मौसम बताउ","बत्तिको अवस्था बदल","पङ्खाको स्तिथी बदल"]
sendBeaconCount = 5
# route for ESP to fetch data from
@app.route('/esp')
def esp():
	# Todo : need make implementation as per predicted word
	global makePrediction
	global sendBeaconCount
	global lightState

	if makePrediction and sendBeaconCount :
		sendBeaconCount -= 1
		if sendBeaconCount == 1 :
			makePrediction = False
		if(lightState):
			prediction = "0"
		else :
			prediction = "1"
		return "P" + prediction 		#send only number to the arduino relating...
		# ruff plan : send command String as "P<predNumber>"
		# where P - prediction
		#		<predNumber> - sentence index : 0, 1, 2, 3, 4
		# TODO figure out indicies of sentences and update in arduino...
	else :
		if not makePrediction :
			sendBeaconCount = 5
		return "NA"

'''
source :
https://pythonprogramming.net/jquery-flask-tutorial/
https://youtu.be/j5wysXqaIV8
'''
