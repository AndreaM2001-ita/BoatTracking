import cv2
import os

# Define the path to the input video folder and output folder
#input_folder = 'videos'
output_folder = 'frames'

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

script_dir = os.path.dirname(os.path.abspath(__file__))  # current dir
input_folder = os.path.join(script_dir, 'videos')

print(input_folder)
# Get the list of video files in the input folder
video_files = [f for f in os.listdir(input_folder) if f.endswith(('.m4v'))]

if not video_files:
    print("Error: No video files found in the 'videos' folder.")
    exit()

# Process each video file
for video_file in video_files:
    video_path = os.path.join(input_folder, video_file)
    print(f"Processing video: {video_file}")
    
    # Create a subfolder for each video
    video_output_folder = os.path.join(output_folder, os.path.splitext(video_file)[0])
    os.makedirs(video_output_folder, exist_ok=True)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        continue

    # Frame counter
    frame_number = 0
    
    # Read and save frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Exit loop when video ends
        
        # Construct frame filename and save the image
        frame_filename = f"frame_{frame_number:04d}.png"
        frame_path = os.path.join(video_output_folder, frame_filename)
        cv2.imwrite(frame_path, frame)
        
        print(f"Saved {frame_path}")
        frame_number += 1

    # Release the video capture object
    cap.release()
    print(f"Finished processing {video_file}\n")

print("All frames extracted from all videos successfully.")