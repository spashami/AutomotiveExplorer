import numpy as np
import scipy

class SignalFeatures(object):
	def __init__(self):
		pass
		
	''' Extract some simple features from a timeseries '''
	@staticmethod
	def extract(sig_values):
		mean = np.mean(sig_values)
		median = np.median(sig_values)
		std = np.std(sig_values)
		maximum = max(sig_values)
		minimum = min(sig_values)
		skewness = scipy.stats.skew(sig_values)
		kurtosis = scipy.stats.kurtosis(sig_values)
		
		sig_values_deriv = np.gradient(sig_values)
		
		mean_deriv = np.mean(sig_values_deriv)
		median_deriv = np.median(sig_values_deriv)
		std_deriv = np.std(sig_values_deriv)
		maximum_deriv = max(sig_values_deriv)
		minimum_deriv = min(sig_values_deriv)
		skewness_deriv = scipy.stats.skew(sig_values_deriv)
		kurtosis_deriv = scipy.stats.kurtosis(sig_values_deriv)
		
		decrease_ratio = len([v for v in sig_values_deriv if v < 0]) * 1. / len(sig_values_deriv)
		increase_ratio = len([v for v in sig_values_deriv if v > 0]) * 1. / len(sig_values_deriv)
		
		# ----------------------
		features = [mean, median, std, maximum, minimum, skewness, kurtosis]
		features_deriv = [mean_deriv, median_deriv, std_deriv, maximum_deriv, minimum_deriv, skewness_deriv, kurtosis_deriv]
		
		ratios = [decrease_ratio, increase_ratio]
		
		histo, _ = np.histogram( sig_values, bins=3 ); histo = histo.tolist()
		histo_deriv, _ = np.histogram( sig_values_deriv, bins=3 ); histo_deriv = histo_deriv.tolist()
		
		return features + features_deriv + ratios + histo + histo_deriv
	
	''' Extract some simple features from many timeseries '''
	@staticmethod
	def extractMany(L_sig_values):
		F = [ SignalFeatures.extract(sig_values) for sig_values in L_sig_values ]
		x = [ v for vv in F for v in vv ] # Flat list of all features for all signals
		return x