import sys
import os
sys.path.insert(0, os.path.abspath('../..'))

from Database.DatabaseController import DatabaseController
from RealEstateValuationSystem.InputControl.InputController import InputController

import pandas

def Load(datasetName, condition):
	if InputController.IsDict(datasetName):
		return _LoadFromMongoDB(datasetName, condition)
	#if InputController.IsString(datasetName):
		#LoadFromJSON(datasetName)
	return pandas.DataFrame()

def _LoadFromMongoDB(conn, condition):
	"""Load a dataset from MongoDB. Returns the dataset in a pandas DataFrame."""
	if not InputController.IsDict(conn):
		raise Exception("conn isn't a dictionary")
	if not InputController.IsDict(condition):
		raise Exception("condition isn't a dictionary")
		
	db = DatabaseController()
	db.RunMongod()
	db.Open(conn)
	
	dataset = []
	iter = db.Find(condition)
	for doc in iter:
		doc = _ExtractValueFromListInDict(doc)
		dataset.append(doc)
	db.CloseAndStop()
	
	dataset = pandas.DataFrame(dataset)
	return dataset
	
def _ExtractValueFromListInDict(dict):
	"""Replace the pattern {'key1' : [value1], ...} with {'key1' : value1, ...}. All other values
	are left as it is. Returns the extracted dictionary."""
	if not InputController.IsDict(dict):
		raise Exception("Cannot extract values because the parameter isn't a dictionary")
	
	for key in dict.keys():
		if InputController.IsList(dict[key]):
			if dict[key] != []:
				dict[key] = dict[key][0]
	return dict
	
#def LoadFromCSV(filePath):

#def LoadFromJSON(filePath):