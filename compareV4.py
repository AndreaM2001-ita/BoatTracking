import os
import fnmatch
from skimage.metrics import structural_similarity
import cv2
import datetime
import calendar
from PIL import Image

from serverV2 import create_launch_event, update_retrieval_event, read_boats

##########
#The following comparison scripting is taken from
# https://www.youtube.com/watch?v=16s3Pi1InPU
# https://github.com/bnsreenu/python_for_microscopists/blob/master/191_measure_img_similarity.py
##########
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

def compare():
  script_dir = os.path.dirname(os.path.abspath(__file__)) # set script directory, the same as this script
  results_dir = os.path.join(script_dir, 'result_tracks') # set results directory, relative to the script directory

  if not os.path.exists(os.path.join(results_dir, 'matches')): #if the folder "matches" doesn't exist...
    os.makedirs(os.path.join(results_dir, 'matches')) #create it
  match_dir = os.path.join(results_dir, 'matches') #set match dir, relative to the results dir

  if not os.path.exists(os.path.join(results_dir, 'duplicates')): # if the duplicates directory doesn't exist...
    os.makedirs(os.path.join(results_dir, 'duplicates')) #create it
  dupe_dir = os.path.join(results_dir, 'duplicates') #set duplicate dir, relative to the results dir

  comp_dict = {} # create comparison dictionary
  comp_results = {} #create comparison results dictionary
  boatIDs = [] # create a boatID list

  res_num = len(fnmatch.filter(os.listdir(results_dir), '*.jpg')) #find the number of files in the results directory that are JPGs

  for i in range(0, res_num, 5): # iterate through all the images in the results directory in leaps of 5 (as there will be 5 images per ID at this stage)
    image = fnmatch.filter(os.listdir(results_dir), '*.jpg')[i] #take the image name
    imageID = image.split("_")[0] #split it by underscores and take the first value (the ID number)
    boatIDs.append(int(imageID)) # and append it to this list

  boatIDs.sort() # sort the list so they're sequential
  #print(boatIDs)

  r_index = 0
  l_index = 0
  #with open("results.csv", "w") as file:
  #  file.write(f"\n")

  i = 0
  while i < len(boatIDs): # while i is less than the number of boatIDs to compare

    if i+1 < len(boatIDs): # if there is atleast 2 boat IDs to compare
      #print("if i+1")
      compare1 = fnmatch.filter(os.listdir(results_dir), f'{boatIDs[i]}_*') # create a list of all the boat image names of one of the IDs
      l_index = int(((compare1[4].split("_"))[1])) #take the detection time of the last image as the 'launch' time
      classNamei = compare1[0].replace('.jpg', '').split("_")[4] #take the detections class name from its first detection
      j = i+1 #make j +1 so we're always at least comparing "the next" boat ID

      while j < len(boatIDs): #while j is less than the number boat IDs, there are more boat IDs to compare
        compare2 = fnmatch.filter(os.listdir(results_dir), f'{boatIDs[j]}_*') #create a list of boat images of the comparison ID
        r_index = int(((compare2[0].split("_"))[1])) # take the detection time of the first image as the 'possible return' time
        
        orb_similarity = 0 #set Orb and SSim to 0
        ssim = 0
        
        for img1 in compare1: #for every image in the first list

          for img2 in compare2: #compare it against all images of the second list
            com1 = cv2.imread(os.path.join(results_dir, img1), 0)
            com2 = cv2.imread(os.path.join(results_dir, img2), 0)
            orb_similarity = orb_similarity + orb_sim(com1, com2)  # the higher the results, the more alike it is

            #Resize for SSIM
            from skimage.transform import resize
            com2r = resize(com2, (com1.shape[0], com1.shape[1]), anti_aliasing=True, preserve_range=True)
            ssim = ssim + structural_sim(com1, com2r) # the higher the results, the more alike it is

                                    
        orb = round((orb_similarity * 20 ), 2) # divided by 25, then multiplied by 100 (for percentage), then multiplied by 5 to exagerate the differences between similar and dissimilar detections
        struc_sim = round((ssim * 20), 2)

        with open("results.txt", "a") as file:
          file.write(f'The average Orb and Structural Similarity scores between boat ID {boatIDs[i]} and {boatIDs[j]} are:\nOrb: {orb}\nSsim: {struc_sim}\n')

        if (orb > 50) & (struc_sim > 17): #if the two image batches are similar

          if abs((r_index - l_index)) > 1800: #and they're far enough apart to not be a duplicate
            waterminutes = int(((r_index - l_index) / 60) ) # since epoch seconds are from the same time stamp, and they're just seconds, we can divide their difference by 60 to get minutes on water
            comp_results[i+1] = boatIDs[i], l_index, r_index, 'M', boatIDs[j], waterminutes, classNamei #add this boat as a Match to the comp_results dictionary
            with open("results.txt", "a") as file:
              file.write(f"matched {boatIDs[i]} and {boatIDs[j]}\n")
            #break

          else:
            comp_results[i+1] = boatIDs[j], l_index, r_index, 'D', boatIDs[i] #if the boats ARE a match, but their launch/retrieve window is too close, consider them a Duplicate
            with open("results.txt", "a") as file:
              file.write(f"{boatIDs[j]} is a dupe of {boatIDs[i]}\n")
            boatIDs.remove(boatIDs[j]) #remove the duplicate ID from the boatIDs list so it doesn't try to compare against other batches
            #break
            
        else: #if the images are not a match
          comp_results[i+1] = boatIDs[i], l_index, 0, 'O', 0, 0, classNamei #add boat ID to the dictionary as an orphan
          with open("results.txt", "a") as file:
            file.write(f"{boatIDs[i]} is an orphan\n")
          
        j+=1

    else: #if there are no other boats to compare against (it's the last ID of the list)
      comp_results[i+1] = boatIDs[i], l_index, 0, 'O', 0, 0, classNamei #add as an orphan
      with open("results.txt", "a") as file:
              file.write(f"{boatIDs[i]} is an orphan\n")

    i+=1
  i+=1


  ##### Comparison results output #####
  print(comp_results)
  for r in range(1, len(comp_results)+1): #loop through the comp_results dictionary
    if comp_results.get(r)[3] == 'M': #if the nested dictionary value denoting status is 'M'atch
      moveID1 = comp_results.get(r)[0] # grab the Boat ID
      moveID2 = comp_results.get(r)[4] # and grab the matched boat ID

      l_index = int(comp_results.get(r)[1]) # take the launch index
      l_timestmp = datetime.datetime.fromtimestamp(l_index) # to make a launch time stamp
      l_date = str(l_timestmp).split(' ')[0] # to split and make a launch date
      l_time = str(l_timestmp).split(' ')[1] # and launch time of day
      r_index = int(comp_results.get(r)[2]) # grab the retreival index
      r_timestmp = datetime.datetime.fromtimestamp(r_index) # to make a retreival timestamp
      r_time = str(r_timestmp).split(' ')[1] # to create a retreival time

      waterminutes =  comp_results.get(r)[5] # grab the waterminutes value
      for img1 in fnmatch.filter(os.listdir(results_dir), f'{moveID1}_*'): #for each file in the results directory that match this Boat ID
        os.replace(os.path.join(results_dir, img1), os.path.join(match_dir, img1))  #move to the matches directory
      for img2 in fnmatch.filter(os.listdir(results_dir), f'{moveID2}_*'): #ditto
        os.replace(os.path.join(results_dir, img2), os.path.join(match_dir, img2)) # ditto
      with open("results.txt", "a") as file: #open the results file as "a"ppend and write out the results
              file.write(f'Boat ID {moveID1} launched on {l_date} at {l_time} and matched with Boat ID {moveID2}, with a  retreival time of {r_time}. Minutes on water: {waterminutes}\n')
      create_launch_event(comp_results.get(r)[0], comp_results.get(r)[6], comp_results.get(r)[1])
      update_retrieval_event(comp_results.get(r)[0], comp_results.get(r)[2], comp_results.get(r)[4])
      
    elif comp_results.get(r)[3] == 'D': #if the nested dictionary value denoting status is 'D'uplicate
      dupeID1 = comp_results.get(r)[0] # grab the boat ID
      dupeID2 = comp_results.get(r)[4]
      for img1 in fnmatch.filter(os.listdir(results_dir), f'{dupeID1}_*'): #find each file with that ID
        os.replace(os.path.join(results_dir, img1), os.path.join(dupe_dir, img1)) # move to the Dupe folder
      with open("results.txt", "a") as file: #write out the results
        file.write(f'Boat ID {dupeID1} is a duplicate of {dupeID2}\n')

    elif comp_results.get(r)[3] == 'O': #if the nested dictionary value denoting status is 'O'rphan
      orphanID = comp_results.get(r)[0] #grab the Boat ID
      create_launch_event(comp_results.get(r)[0], comp_results.get(r)[6], comp_results.get(r)[1])
      with open("results.txt", "a") as file: #write out the results and leave the file in place for the next run. it's just waitin' for a mate...
        file.write(f'Boat ID {orphanID} is an orphan\n')

