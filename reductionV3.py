import os
import fnmatch

#enumerate detections in the results folder
script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(script_dir, 'result_tracks')
detections = os.listdir(results_dir)

# There will be other files in the detections directory, but the loop below needs to start from the 'first' "Boat" file that is present.
# First we need to set an ID of a known Boat detection
lowest_ID = int(fnmatch.filter(detections, 'Boat_*')[0].split("_")[1])

# Then we iterate through all the Boat files to find the lowest ID number to set 'd' to
for file in detections:
    if file.startswith('Boat'):
        file_split = file.split("_")
        if int(file_split[1]) >= lowest_ID:
            continue
        else:
            lowest_ID = int(file_split[1])

d = lowest_ID

count = 0
keep_array = []

while len(fnmatch.filter(detections, f'Boat_{d}_*')):
    coord_array = []
    #det_len = len(fnmatch.filter(detections, f'*_{d}_*')) # number of images of that particular boat ID
    print(d)
    img_array = fnmatch.filter(detections, f'Boat_{d}_*') # create an array of those images
    print(img_array)
    img_count = int(len(img_array))
    print(img_count)

    if img_count < 10:
        for img in img_array:
            print(img)
            os.remove(os.path.join(results_dir, img))

    else:
        del img_array[img_count-5:]
        img_count = int(len(img_array))

        red_remove = img_count % 5
        del img_array[0:red_remove]
        red_scale = int(img_count / 5)
        red_count = 0
        while red_count < (red_scale*5):
            keep_array.append(img_array[red_count])
            coord_array.append(img_array[red_count])
            red_count = red_count + red_scale

    x = []
    y = []
    if len(coord_array) > 1:
        for img in coord_array:
            img_split = img.replace('.jpg', '').split("_")
            x.append(int(img_split[3]))
            y.append(int(img_split[4]))
        x_move = abs(x[0]-x[4])
        y_move = abs(y[0]-y[4])
        print(f'Boat {d} has moved {x_move} and {y_move} X and Y pixels, respectively')
        if (x_move < 20) & (y_move < 20):
            for img in img_array:
                print(f'Boat {d} is considered stationary and has been removed')
                os.remove(os.path.join(results_dir, img))

    d+=1 

remainder = os.listdir(results_dir)

for file in remainder:
    if file.startswith('Boat'):
        if file not in keep_array:
            os.remove(os.path.join(results_dir, file))
        else:
            new_name = file.replace('Boat_', '')
            os.rename(os.path.join(results_dir, file), os.path.join(results_dir, new_name))

