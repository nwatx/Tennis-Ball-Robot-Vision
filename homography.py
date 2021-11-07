from numpy import arcsin, arctan, cos
from numpy.lib.function_base import average
import math

def get_dist(h1, h2):

	# get our first two angles
	c = 280
	height = 0.25
	scaling_factor = 1/1000

	d = 234

	# calibration for d
	# for d in range(2, 320):
	# print("d:", d)
	theta_1, theta_2 = arctan((c - h1)/d), arctan((c - h2)/d)
	a = math.sqrt(c**2 /
	(2 * (1 - cos(average([theta_1, theta_2]))))) * scaling_factor
	x = a * cos(average([theta_1, theta_2])/2)
	dist = a * cos(arcsin(height/x))
	return dist