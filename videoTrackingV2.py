import ultralytics
import torch
from collections import defaultdict
import time
import cv2
import os
from PIL import Image
import colorsys
import numpy as np
from ultralytics import YOLO
import datetime
import calendar

from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort
from deep_sort.sort.tracker import Tracker

#from skimage.metrics import structural_similarity

deep_sort_weights = 'deep_sort/deep/checkpoint/ckpt.t7'
tracker = DeepSort(model_path=deep_sort_weights, max_age=5) #leaving max_age at 5 cuts down on new IDs being assigned to boats when there's a momentary loss of track

def track_video(video_path, output_path, time_since_epoch, hour, currentModel):
    # load the model
    model = YOLO(currentModel)
    modelNames= model.names
    # open the video file
    cap = cv2.VideoCapture(video_path)

    # get the video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # define the codec and create VideoWriter object
    out = cv2.VideoWriter(
        output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame_width, frame_height)
    )

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    frames = []

    unique_track_ids = set()

    i = 0
    counter, fps, elapsed = 0, 0, 0
    start_time = time.perf_counter()

    resultsIDs = []
    resultsFrames = []
    class_names = []

    for j in range(len(modelNames)):
        class_names.append(modelNames[j])

    # loop through the video frames
    while True:
        success, frame = cap.read()
        if frame is None:
            print("End of Video")
            r=0
            last_id = 0
            while r < len(resultsIDs): # iterate through all the IDs in the resultsIDs array
                if last_id >= resultsIDs[r]: #if we see the same Boat ID again (a duplicate ID)
                    r+=1 #increment r and reloop
                    continue
                else: #if we see a new boat ID
                    frame_seconds = round(resultsFrames[r]*7.6, 0) #calculate, from the frames array, how many seconds from the start of the video this was (7.6s per frame curently)
                    frameEpoch = time_since_epoch+frame_seconds-28800 #add elapsed seconds to epoch time, minus 8 hours for GMT conversion - haven't figured out how to remove that +8 GMT thing yet
                    Timestmp = datetime.datetime.fromtimestamp(frameEpoch) # create a time stamp from the new epoch time
                    print(f"BoatID {resultsIDs[r]} detected at {Timestmp}")
                    last_id=resultsIDs[r] #record this boat ID as the last seen ID for the loop to reiterate
                    r+=1
            print(f"Total frames {i}")
            print(f'Next Boat ID should be {last_id+1}')

            # Write a file that will tell the tracker what the next ID should be when it runs again to avoid duplicate IDs being written to results folder
            with open("nextID.txt", "w") as file:
                file.write(f"{last_id+1}")
            if not os.path.exists("results.txt"):
                with open("results.txt", "w") as file:
                    file.write("")

            break

        if success:
            #####
            # A good portion of this next section is taken from 
            # https://github.com/AarohiSingla/Tracking-and-counting-Using-YOLOv8-and-DeepSORT
            # with some alterations and additions
            #####
            og_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = og_frame.copy()

            results = model(frame, device=0, classes=(0, 1, 2, 3, 4, 5), show_conf=True, conf=0.5)
            #boxes = results[0].boxes.xywh.cpu()

            
            for result in results:
                boxes = result.boxes  # Boxes object for bbox outputs
                probs = result.probs  # Class probabilities for classification outputs
                cls = boxes.cls.tolist()  # Convert tensor to list
                #print(cls)
                xyxy = boxes.xyxy
                #print(xyxy)
                conf = boxes.conf
                xywh = boxes.xywh  # box with xywh format, (N, 4)
                #print(xywh)
                for class_index in cls:
                    class_name = class_names[int(class_index)]
                    #    #print("Class:", class_name)
                    #image_path = f"result_detects/frame_{i}.jpg"
                    #print(f"writing frame {i}")
                    #cv2.imwrite(image_path, cv2.cvtColor(og_frame, cv2.COLOR_RGB2BGR))

            pred_cls = np.array(cls)
            conf = conf.detach().cpu().numpy()
            xyxy = xyxy.detach().cpu().numpy()
            bboxes_xywh = xywh
            bboxes_xywh = xywh.cpu().numpy()
            bboxes_xywh = np.array(bboxes_xywh, dtype=float)

            tracks = tracker.update(bboxes_xywh, conf, og_frame)
        
            for track in tracker.tracker.tracks:
                track_id = track.track_id
                print(track_id)
                hits = track.hits
                x1, y1, x2, y2 = track.to_tlbr()  # Get bounding box coordinates in (x1, y1, x2, y2) format
                w = x2 - x1  # Calculate width
                h = y2 - y1  # Calculate height

                blue_color = (0, 0, 255)  # (B, G, R)
                red_color = (255, 0, 0)  # (B, G, R)
                green_color = (0, 255, 0)  # (B, G, R)

                # Determine color based on track_id
                color_id = track_id % 3
                if color_id == 0:
                    color = red_color
                elif color_id == 1:
                    color = blue_color
                else:
                    color = green_color

                cv2.rectangle(og_frame, (int(x1), int(y1)), (int(x1 + w), int(y1 + h)), color, 2)

                text_color = (0, 0, 0)  # Black color for text
                cv2.putText(og_frame, f"{class_name}-{track_id}-{conf}", (int(x1) + 10, int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

                # Add the track_id to the set of unique track IDs
                unique_track_ids.add(track_id)
                resultsFrames.append(i)
                resultsIDs.append(track_id)
                frame_seconds = int(i*7.6) #calculate, from the frames array, how many seconds from the start of the video this was (7.6s per frame curently)
                frameEpoch = int(time_since_epoch+frame_seconds-28800)

                ##### This hasn't been implimented yet.
                # The idea here is the results written out below will have coordinate information added to the file name
                # This way, later on, they can be tested to see if the boat track moved at all during the video
                # Boats that do not moved are assumed to be moored and removed from consideration
                coX = int((x1+x2)/2)
                coY = int((y1+y2)/2)
                
                #image_path = f"result_tracks/Boat_{track_id}_{frameEpoch}.jpg"
                image_path = f"result_tracks/Boat_{track_id}_{frameEpoch}_{coX}_{coY}.jpg"
                print(f"writing frame {i}")
                cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)[int(y1-20):int(y1+h+20), int(x1-20):int(x1+w+20)])

        boat_count = len(unique_track_ids)

        


        # Update FPS and place on frame
        current_time = time.perf_counter()
        elapsed = (current_time - start_time)
        counter += 1
        if elapsed > 1:
            fps = counter / elapsed
            counter = 0
            start_time = current_time

        # Draw boat count on frame
        cv2.putText(og_frame, f"Boat Count: {boat_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

        # Append the frame to the list
        frames.append(og_frame)

        # Write the frame to the output video file
        out.write(cv2.cvtColor(og_frame, cv2.COLOR_RGB2BGR))

        i+=1
            
            # write the annotated frame
            #out.write(annotated_frame)
            #if cv2.waitKey(1) & 0xFF == ord("q"):
            #    break
        #else:
        #    break
    # release the video capture object and close the display window
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Processed video saved to {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  # current dir
    videos_dir = os.path.join(script_dir, 'videos')
    output_dir = os.path.join(script_dir, 'output')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    Timestmp = []
    # Example: analyze all .m4v videos in the 'videos' folder
    for video_file in os.listdir(videos_dir):
        if video_file.endswith('.m4v'):
            # Get date and time from the video file
            #Date_ToD_sep = video_file.split(" ") #split the file name using the space as a delimiter, this should seperate the date from the hour
            Date = video_file.split(" ")[0].split("-") #delimit the date portion of the above using the - . This should give day, month, year; in that order
            hour = video_file.split(" ")[1]
            #Create usable timestamp from above variables
            Timestmp = datetime.datetime(int(Date[2]), int(Date[1]), int(Date[0]), int(hour), 0, 0) #Timestamp requires Year, Month, Day, so the order is back to front from the above, then hr,min,sec

            time_since_epoch = calendar.timegm(Timestmp.timetuple()) #This gives an artificial epoch time that will be used as "the start of the video" which we can add 'video time' to later

            video_path = os.path.join(videos_dir, video_file)
            output_path = os.path.join(output_dir, f"output_{video_file}")

            track_video(video_path, output_path, time_since_epoch, hour, "trainedPrototype3.pt")
