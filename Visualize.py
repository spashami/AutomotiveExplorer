import datetime
import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pylab as pl
import matplotlib
from matplotlib.dates import MinuteLocator, DayLocator, HourLocator, DateFormatter, drange, MonthLocator
from sklearn.decomposition import PCA
from sklearn import manifold
from sklearn.metrics import euclidean_distances

class Visualize:
	def __init__(self):
		matplotlib.rcParams['agg.path.chunksize']  = 20000
		
		self.w = 15 # width of the plots
		self.h = 10 # hight of the plots
		
		self.lw = 0
		self.s = 20
		
		self.plots = None
		# self.xyz_range = { 'x':[float("inf"), float("-inf")], 'y':[float("inf"), float("-inf")], 'z':[float("inf"), float("-inf")] }
		self.colors = ['r', 'b', 'g', 'm', 'y', 'k', 'c'] + [ (random.uniform(0.,1.), random.uniform(0.,1.), random.uniform(0.,1.)) for _ in range(10) ]
		
	#---------------------------------------
	def cl(self, id):
		if id >= len(self.colors):
			print("Warning: the color id is ", id, " >= ", len(self.colors),". Some colors may be reused for the same id.")
		return self.colors[id%len(self.colors)]
		
	#---------------------------------------
	@staticmethod
	def colors(nb):
		cmap = plt.get_cmap('gist_ncar')
		return [cmap(i) for i in np.linspace(0, 1, nb)]
		
	#---------------------------------------
	def PCA_Plot(self, axs, dim = 3, axs_labels = None, color = 'r', marker = '.', fig = None):
		X = [ list(v) for v in list(zip(*axs)) ]
		pca = PCA(n_components=dim)
		XX = pca.fit(X).transform(X)
		XX = [list(x) for x in XX]
		
		axs_r = [ list(v) for v in list(zip(*XX)) ]
		self.plot(axs_r, axs_labels, color, marker, fig)
		
	#---------------------------------------
	def PCA_Transform(self, axs, dim = 3):
		X = [ list(v) for v in list(zip(*axs)) ]
		pca = PCA(n_components=dim)
		XX = pca.fit(X).transform(X)
		return [list(x) for x in XX]
		
	#---------------------------------------
	def MDS_Plot(self, axs, dim = 3, axs_labels = None, color = 'r', marker = '.', fig = None):
		X = [ list(v) for v in list(zip(*axs)) ]
		similarities = euclidean_distances( np.array(X).astype(np.float64) )
		mds = manifold.MDS(n_components=dim, dissimilarity='precomputed')
		XX = mds.fit(similarities).embedding_
		XX = [list(x) for x in XX]
		
		axs_r = [ list(v) for v in list(zip(*XX)) ]
		self.plot(axs_r, axs_labels, color, marker, fig)
		
	#---------------------------------------
	def MDS_Transform(self, axs, dim = 3):
		X = [ list(v) for v in list(zip(*axs)) ]
		similarities = euclidean_distances( np.array(X).astype(np.float64) )
		mds = manifold.MDS(n_components=dim, dissimilarity='precomputed')
		XX = mds.fit(similarities).embedding_
		return [list(x) for x in XX]
	
	#---------------------------------------
	def start_plot( self, axs_labels ):
		if len(axs_labels) < 3:
			fig, self.plots = plt.subplots( 1, 1, sharex=False )
			fig.set_size_inches(self.w, self.h)
			
			self.plots.set_xlabel(axs_labels[0])
			self.plots.set_ylabel(axs_labels[1])
		else:
			fig = plt.figure()
			self.plots = fig.add_subplot(111, projection='3d')
			fig.set_size_inches(self.w, self.h)
			
			self.plots.set_xlabel(axs_labels[0])
			self.plots.set_ylabel(axs_labels[1])
			self.plots.set_zlabel(axs_labels[2])

			
	#---------------------------------------
	def do_plot(self, axs, axs_labels = None, color = 'r', marker = '.', lw = 1, label="Label"): # FIXME what is len(axs) is > 3 ? Use Multidim Scaling or Feature selection
		if axs_labels is None:
			axs_labels = [ "Axis "+str(i+1) for i in range( len(axs) ) ]
		
		if len(axs) == 1:
			axs = [ range( len(axs[0]) ) ] + axs
			axs_labels = [ "Samples" ] + axs_labels
		elif len(axs) > 3:
			axs = list(zip(*self.PCA_Transform(axs)))
		
		if self.plots is None:
			self.start_plot( axs_labels )
		
		if all([ isinstance(v, datetime.date) for v in axs[0] ]):
			self.plots.set_xlim([ min(axs[0]), max(axs[0]) ]) 
			plt.gcf().autofmt_xdate()
			self.plots.xaxis.set_major_locator(MinuteLocator(interval=15))
			self.plots.xaxis.set_major_formatter( DateFormatter("%Y-%m-%d %H:%M") )
			
		if marker == '-':
			self.plots.plot( *axs, c = color, lw = lw, label=label )
		else:
			self.plots.scatter( *axs, c = color, marker = marker, lw = self.lw, s = self.s, cmap = plt.copper(), label=label )
			
		self.plots.legend(loc='best', ncol=2)
		
	#---------------------------------------
	def end_plot(self, fig = None):
		if fig is None: plt.show()
		else: plt.savefig(fig)
		
		# plt.grid(True) # FIXME
		plt.close()
		
		self.plots = None
		# self.xyz_range = { 'x':[float("inf"), float("-inf")], 'y':[float("inf"), float("-inf")], 'z':[float("inf"), float("-inf")] }
		
	#---------------------------------------
	def plot(self, axs, axs_labels = None, color = 'r', marker = '.', fig = None, label="Label"):
		self.do_plot( axs, axs_labels, color, marker, label=label )
		self.end_plot( fig )
		
	#---------------------------------------
	def plot_groups(self, groups, fig = None):
		colors = self.colors
		keys = groups.keys()
		
		if len(keys) > len(colors):
			print("Warning: the number of groups to plot is ", len(keys), " > ", len(colors),". Some groups may be colored similarly.")
			
		for y in keys:
			cl = colors[y % len(colors)]
			self.do_plot( list(zip(* groups[y] )), color = cl )
		
		self.end_plot(fig)
		
	#---------------------------------------
	
	