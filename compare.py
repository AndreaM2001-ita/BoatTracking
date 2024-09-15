import os
import fnmatch
from skimage.metrics import structural_similarity
import cv2
import datetime
import calendar

def orb_sim(img1, img2):
  # SIFT is no longer available in cv2 so using ORB
  orb = cv2.ORB_create()

  # detect keypoints and descriptors
  kp_a, desc_a = orb.detectAndCompute(img1, None)
  kp_b, desc_b = orb.detectAndCompute(img2, None)

  # define the bruteforce matcher object
  bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
  #perform matches. 
  matches = bf.match(desc_a, desc_b)
  #Look for similar regions with distance < 50. Goes from 0 to 100 so pick a number between.
  similar_regions = [i for i in matches if i.distance < 50]  
  if len(matches) == 0:
    return 0
  return len(similar_regions) / len(matches)


#Needs images to be same dimensions
def structural_sim(img1, img2):

  sim, diff = structural_similarity(img1, img2, data_range=1, full=True)
  return sim

script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(script_dir, 'result_tracks')

batches = int(len(os.listdir(results_dir)) / 5)

if not os.path.exists('matches'):
        os.makedirs('matches')

i = 1
d = 1

comp_results = {}

while i+1 <= batches:
		
	if fnmatch.filter(os.listdir(results_dir), f'{d}_*'):
		compare1 = fnmatch.filter(os.listdir(results_dir), f'{d}_*')
		j=i+1
		e = d+1
		print(f'dict index {i}, Boat ID {d}')
		# ID, first second, last second, status, matchID
		l_index = int(((compare1[4].split("_"))[1])[:-4])
		comp_results[i] = d, l_index, 0, 'O', 0

		while j <= batches:
			if fnmatch.filter(os.listdir(results_dir), f'{e}_*'):
				compare2 = fnmatch.filter(os.listdir(results_dir), f'{e}_*')
				print(f'\n##### Comparing {d} images against {e} images #####')
				orb_similarity = 0
				ssim = 0

				for img1 in compare1:
					
					for img2 in compare2:
						#print(img1, img2)
						com1 = cv2.imread(os.path.join(results_dir, img1), 0)
						com2 = cv2.imread(os.path.join(results_dir, img2), 0)
						#print(f"Similarity between {img1} and {img2}")
						orb_similarity = orb_similarity + orb_sim(com1, com2)  #1.0 means identical. Lower = not similar
						#print("ORB is: ", round((orb_similarity*100), 2))
						#Resize for SSIM
						from skimage.transform import resize
						com2r = resize(com2, (com1.shape[0], com1.shape[1]), anti_aliasing=True, preserve_range=True)
						ssim = ssim + structural_sim(com1, com2r) #1.0 means identical. Lower = not similar
						#print("SSIM is: ", round((ssim*100),2))

				orb = round((orb_similarity * 20 ), 2)
				struc_sim = round((ssim * 20), 2)
				print(f'The average Orb and Structural Similarity scores between boat ID {d} and {e} are:')
				print(f' Orb: {orb}')
				print(f' Ssim: {struc_sim}\n')
				if (orb > 30) & (struc_sim > 10):
					#grab compare1[4] and take the index from it and convert it from epoch time back to a time stamp
					l_index = int(((compare1[4].split("_"))[1])[:-4])
					l_timestmp = datetime.datetime.fromtimestamp(l_index)
					l_date = str(l_timestmp).split(' ')[0]
					l_time = str(l_timestmp).split(' ')[1]

					r_index = int(((compare2[0].split("_"))[1])[:-4])
					r_timestmp = datetime.datetime.fromtimestamp(r_index)
					r_time = str(r_timestmp).split(' ')[1] 

					if (r_index - l_index) > 1800:
						waterminutes = int(((r_index - l_index) / 60) )
						comp_results[i] = d, l_index, r_index, 'M', e, waterminutes
						print(f'Boat ID {d} launched on {l_date} at {l_time} and matched with Boat ID {e}, with a  retreival time of {r_time}. Minutes on water: {waterminutes}')

					else:
						print(f'boat ID {d} is a duplicate')	
						comp_results[i] = d, l_index, r_index, 'D', 0
				
				e+=1
				j+=1
			else:
				e+=1
		d+=1
		i+=1
	else:
		d+=1

for k in range(1, (len(comp_results)+1)):
	if comp_results.get(k)[3] == 'M':
		print(f'\nBoat {comp_results.get(k)[0]} is Matched with Boat {comp_results.get(k)[4]}.\nTotal time on water: {comp_results.get(k)[5]} minutes')
	elif comp_results.get(k)[3] == 'O':
		print(f'\nBoat {comp_results.get(k)[0]} is an Orphan')
	elif comp_results.get(k)[3] == 'D':
		print(f'\nBoat {comp_results.get(k)[0]} is a Duplicate')

