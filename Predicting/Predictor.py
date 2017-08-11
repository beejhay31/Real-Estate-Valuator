import sys
import os
sys.path.insert(0, os.path.abspath('../..'))

from RealEstateValuationSystem.DatasetAnalysis.ApartmentForSaleCollection import DatasetConfig
from RealEstateValuationSystem.DatasetTransformation.DatasetTransformer import DatasetTransformer
from RealEstateValuationSystem.DatasetSource import DatasetLoader
from RealEstateValuationSystem.DatasetTransformation import TransformationScripts

from sklearn.linear_model import LinearRegression, ElasticNet, ElasticNetCV
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import SelectKBest, f_regression, RFECV
from sklearn.ensemble import GradientBoostingRegressor
import numpy
import pandas


def PredictIntervalValue(customerApartment):
	#print customerApartment
	#print dataset.tail()
	
	#insert faux data to prevent it from being dropped or being incomplete
	customerApartment['priceInEuros'] = [100000]
	customerApartment['sellerLink'] = [u'/korisnik/']
	cutomerApartmentPandas = pandas.DataFrame(customerApartment)
	
	dataset = DatasetLoader.LoadFromMongoDB(DatasetConfig.conn)
	dataset = pandas.concat([dataset, cutomerApartmentPandas], ignore_index=True)
	#print dataset.tail()
	
	transformer = DatasetTransformer(dataset)
	transformer.DropColumns(DatasetConfig.dropColumns)
	
	TransformationScripts.MakeTransformationsForApartmentForSaleCollection(transformer)
	
	countPlace = int(transformer.dataset['place'][transformer.dataset.place == customerApartment['place'][0]].count())
	print "place count:",
	print countPlace
	if countPlace > 200:
		transformer.KeepRows('place == ' + "'" + customerApartment['place'][0] + "'")
	else:
		countTown = int(transformer.dataset['town'][transformer.dataset.place == customerApartment['town'][0]].count())
		print "town count:",
		print countTown
		if countTown > 200:
			transformer.KeepRows('town == ' + "'" + customerApartment['town'][0] + "'")
		else:
			raise Exception("Not enough data!")
			
			
	
	
	Y = transformer.dataset['priceInEuros']
	transformer.DropColumns(['priceInEuros', 'place', 'town'])
	X = transformer.dataset
	#pd.get_dummies(XMod)
	
	customerApartment = X[-1:]
	X = X[:-1]
	Y = Y[:-1]
	
	print "Customer data:"
	print customerApartment
	print "X:"
	print X.tail()
	print "Y:"
	print Y.tail()
	
	model = GridSearchCV(GradientBoostingRegressor(), scoring='neg_mean_squared_error',
	                     param_grid={'loss' :('ls', 'huber'), 'learning_rate' : numpy.arange(0.05, 0.21, 0.05),
						 'n_estimators' : range(70, 111, 10), 'max_depth' : range(2, 4, 1)})
	#print dataset.head()
	#print dataset.tail()
	
	model.fit(X, Y)
	print "Predicted interval value:"
	print model.predict(customerApartment)
	print "!!!-.-.-!!!"
	#print model.cv_results_ #too long to print
	print model.best_estimator_
	print model.best_score_
	print model.best_params_
	#print model.best_index_ #not important
	print model.scorer_
	print model.n_splits_
	
	return model.predict(customerApartment)
	
#PredictIntervalValue({'town': [u'Brezovica'], 'numberOfParkingSpaces': [0], 'floor': [1], 'state': [u'Grad Zagreb'], 'place': [u'Brezovica'], 'size': [80]})
#PredictIntervalValue({'town': [u'Donji Grad'], 'numberOfParkingSpaces': [1], 'floor': [7], 'state': [u'Grad Zagreb'], 'place': [u'Donji grad'], 'size': [30]})