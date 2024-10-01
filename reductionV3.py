def reduce():
    import os
    import fnmatch

    # set script and results directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'result_tracks')

    #enumerate detections in the results folder
    detections = os.listdir(results_dir)

    # There will be other files in the detections directory, but the loop below needs to start from the 'first' "Boat" file that is present.
    # First we need to set an ID of a known Boat detection
    lowest_ID = int(fnmatch.filter(detections, 'Boat_*')[0].split("_")[1])

    # Then we iterate through all the Boat files to find the lowest ID number to set 'd' to. We need to make sure that we aren't processing BoatID "176" before ID "2"
    for file in detections: # for all boats in the list
        if file.startswith('Boat'): #if the file name starts with "Boat"
            file_split = file.split("_") # split the file by underscores to isolate its ID  number
            if int(file_split[1]) >= lowest_ID: # if the ID number (second value) is equal to or greater than the current known lowestID, keep going
                continue
            else:
                lowest_ID = int(file_split[1]) #otherwise, set the current ID number to the new lowestID

    d = lowest_ID # set d as lowest ID now that we know it

    #Instantiate some variables for use later
    count = 0
    keep_array = []

    while len(fnmatch.filter(detections, f'Boat_{d}_*')): #starting from the lowest ID, while there are images of that ID number
        coord_array = [] # create a coord array
        img_array = fnmatch.filter(detections, f'Boat_{d}_*') # create an list of those images
        img_count = int(len(img_array)) #find the number of images in that list

        if img_count < 10: #if there are less than 10 images in that list...
            for img in img_array: #loop through the image list
                os.remove(os.path.join(results_dir, img)) # and remove those images

        else: #otherwise, if there are 10 or more images in that list, do the following:
            del img_array[img_count-5:] # remove the last 5 images from the list - they'll most likely be junk images from DeepSORTs 'max_age' variable trying to reacquire the track
            img_count = int(len(img_array)) #recount the image list

            red_remove = img_count % 5 # find the remainder after dividing the list by 5. We need to have a number of images that are divisible by 5 for later.
            del img_array[0:red_remove] #remove images from the excess images from the front of the list
            red_scale = int(img_count / 5) # find a scaling number for the images (we'll need this for later)
            red_count = 0 # set this to 0
            while red_count < (red_scale*5): # while red_count is below the total number of images
                keep_array.append(img_array[red_count]) # add an image to the keep list and coord list
                coord_array.append(img_array[red_count])
                red_count = red_count + red_scale # increase red_count by the red_scale so we jump through the list in equal bounds

        # set an X and Y list to empty
        x = []
        y = []
        if len(coord_array) > 1: # if there are images that we want to keep
            for img in coord_array: # for every image in that list
                img_split = img.replace('.jpg', '').split("_") # remove the file extension and split the file by underscores. This will give us access to the X and Y coords that are encoded into the file name
                x.append(int(img_split[3])) # append the X and Y values to the x and y lists
                y.append(int(img_split[4]))
            x_move = abs(x[0]-x[4]) #find x and y displacement by finding the absolute difference between the first and last x and y coordinate values
            y_move = abs(y[0]-y[4])
            print(f'Boat {d} has moved {x_move} and {y_move} X and Y pixels, respectively')
            if (x_move < 20) & (y_move < 20): # if the boat has moved LESS than 20 pixels in EITHER x or y
                for img in img_array: # for every image of that boat
                    print(f'Boat {d} is considered stationary and has been removed')
                    os.remove(os.path.join(results_dir, img)) #remove it

        d+=1 # increment the boat ID number to check

    # Once we have removed the stationary boats and the boats without sufficient detection images
    remainder = os.listdir(results_dir) # re-enumerate the results directory

    for file in remainder: # for those remaining files
        if file.startswith('Boat'): # if they start with "Boat"
            if file not in keep_array: #if they are NOT in the keep list
                os.remove(os.path.join(results_dir, file)) #remove them - this will get rid of the 'in-between' images of the valid boat detections, leaving only the sample of 5 images that we want to keep.
            else:
                new_name = file.replace('Boat_', '') #if the filename IS in the keep list, rename it by removing the "Boat_" at the start
                os.rename(os.path.join(results_dir, file), os.path.join(results_dir, new_name))

