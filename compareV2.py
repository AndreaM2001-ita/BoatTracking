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

if not os.path.exists(os.path.join(results_dir, 'matches')):
        os.makedirs(os.path.join(results_dir, 'matches'))

if not os.path.exists(os.path.join(results_dir, 'duplicates')):
        os.makedirs(os.path.join(results_dir, 'duplicates'))

match_dir = os.path.join(results_dir, 'matches')
dupe_dir = os.path.join(results_dir, 'duplicates')

comp_dict = {}
comp_results = {}

#if os.path.isfile('results.txt'):
#  with open("results.txt", "r") as infile:
#    first_char = infile.read(1)
#    if first_char:
#      prev_results = infile.read()
#      split_results = (prev_results.rstrip()).split('\n')
#      for i in range(0, len(split_results)):
#        split_split = split_results[i].split(',')
#        comp_dict[i+1] = int(split_split[0]), int(split_split[1]), int(split_split[2]), 'O', int(split_split[4])

res_num = len(fnmatch.filter(os.listdir(results_dir), '*.jpg'))

for i in range(0, res_num, 5):
  image = fnmatch.filter(os.listdir(results_dir), '*.jpg')[i]
  imageID = image.split("_")[0]
  batch = fnmatch.filter(os.listdir(results_dir), f'{imageID}_*')
  comp_dict[len(comp_dict)+1] = imageID, (batch[4].split("_"))[1], 0, 'O', 0

boatIDs = []
for i in range(1, len(comp_dict)+1):
  boatIDs.append(comp_dict.get(i)[0])

print(len(boatIDs))

for i in range(0, len(boatIDs)):

  if i+1 < len(boatIDs):
    print(i, len(boatIDs))
    compare1 = fnmatch.filter(os.listdir(results_dir), f'{boatIDs[i]}_*')
    l_index = int(((compare1[4].split("_"))[1]))
    #print(compare1[4].split("_"))
    l_timestmp = datetime.datetime.fromtimestamp(l_index)
    l_date = str(l_timestmp).split(' ')[0]
    l_time = str(l_timestmp).split(' ')[1]
    j = i+1

    while j < len(boatIDs):
      #print(j)
      compare2 = fnmatch.filter(os.listdir(results_dir), f'{boatIDs[j]}_*')
      r_index = int(((compare2[0].split("_"))[1]))
      r_timestmp = datetime.datetime.fromtimestamp(r_index)
      r_time = str(r_timestmp).split(' ')[1] 

      orb_similarity = 0
      ssim = 0

      for img1 in compare1:

        for img2 in compare2:
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

      print(f'The average Orb and Structural Similarity scores between boat ID {boatIDs[i]} and {boatIDs[j]} are:')
      print(f' Orb: {orb}')
      print(f' Ssim: {struc_sim}\n')

      if (orb > 30) & (struc_sim > 10):
        #grab compare1[4] and take the index from it and convert it from epoch time back to a time stamp

        if (r_index - l_index) > 1800:
          waterminutes = int(((r_index - l_index) / 60) )
          comp_results[i+1] = boatIDs[i], l_index, r_index, 'M', boatIDs[j], waterminutes
          with open("results.txt", "a") as file:
            file.write(f'Boat ID {boatIDs[i]} launched on {l_date} at {l_time} and matched with Boat ID {boatIDs[j]}, with a  retreival time of {r_time}. Minutes on water: {waterminutes}\n')

        else:
          comp_results[i+1] = boatIDs[i], l_index, r_index, 'D', boatIDs[j]
          
      else:
        comp_results[i+1] = boatIDs[i], l_index, 0, 'O', 0
        
      j+=1

  else:
    foundIDs = []
    for k in range(0, len(comp_results)):
      foundIDs.append(int(comp_results.get(k+1)[0]))
      foundIDs.append(int(comp_results.get(k+1)[4]))
    if int(boatIDs[i]) not in foundIDs:
      comp_results[k+2] = boatIDs[i], l_index, 0, 'O', 0

for r in range(1, len(comp_results)+1):
  if comp_results.get(r)[3] == 'M':
    moveID1 = comp_results.get(r)[0]
    moveID2 = comp_results.get(r)[4]
    for img1 in fnmatch.filter(os.listdir(results_dir), f'{moveID1}_*'):
      os.replace(os.path.join(results_dir, img1), os.path.join(match_dir, img1))
    for img2 in fnmatch.filter(os.listdir(results_dir), f'{moveID2}_*'):
      os.replace(os.path.join(results_dir, img2), os.path.join(match_dir, img2))
    
  elif comp_results.get(r)[3] == 'D':
    dupeID1 = comp_results.get(r)[0]
    dupeID2 = comp_results.get(r)[4]
    for img1 in fnmatch.filter(os.listdir(results_dir), f'{dupeID1}_*'):
      os.replace(os.path.join(results_dir, img1), os.path.join(dupe_dir, img1))
    with open("results.txt", "a") as file:
      file.write(f'Boat ID {dupeID1} is a duplicate of {dupeID2}\n')
  elif comp_results.get(r)[3] == 'O':
    orphanID = comp_results.get(r)[0]
    with open("results.txt", "a") as file:
      file.write(f'Boat ID {orphanID} is an orphan\n')


