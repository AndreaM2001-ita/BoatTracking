import cv2
import os

from ultralytics import YOLO


script_dir = os.path.dirname('/content/')  # current dir
videos_dir = os.path.join(script_dir, 'videos')
files = os.listdir(videos_dir)  # list of all files in dir

video_files = [f for f in files if f.endswith('.m4v')]  # find .m4v files

frames_dir = os.path.join(script_dir, 'frames')
if not os.path.exists(frames_dir):
    os.makedirs(frames_dir)

model=YOLO('trained_model.pt')

# Process each video file
for video_file in video_files:
    video_path = os.path.join(videos_dir, video_file)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Define the output video path
    output_video_path = os.path.join(frames_dir, f"output_{video_file}")
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'m4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run the model to get predictions
        results = model.predict(frame, save=True, imgsz=(1920, 1080), conf=0.8)
        
        # Draw boxes on the frame
        for result in results:
            for box in result.boxes:
                # Extract bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                # Extract confidence score
                confidence = box.conf[0]
                
                # Draw rectangle and label on the frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Write the frame into the output video
        out.write(frame)

    # Release video capture and writer objects
    cap.release()
    out.release()
