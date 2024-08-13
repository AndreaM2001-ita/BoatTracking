import cv2
import os

from ultralytics import YOLO

def process_frames_from_videos():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # current dir
    videos_dir = os.path.join(script_dir, 'videos')
    files = os.listdir(videos_dir)  #list of all files in dir 

    video_files = [f for f in files if f.endswith('.m4v')]  #find mp4

    frames_dir = os.path.join(script_dir, 'frames')
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    # Create a new YOLO model from scratch
    #model = YOLO("yolov8n.yaml")

    # Load a pretrained YOLOv8n model
    #to use trained model take best.pt file from wights directory
    model = YOLO("yolov8n.pt")
    # Train the model
    results = model.train(data="config.yaml", epochs=3, imgsz=640)
        
    for video_file in video_files:
        video_path = os.path.join(videos_dir, video_file)

        # Open the video file
        cap = cv2.VideoCapture(video_path)

        frame_count = 0

        # Process each frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            
            # Run inference on 'bus.jpg' with arguments
            results=model.predict(frame, imgsz=(2688, 1536), conf=0.4)

            # Filter results based on confidence score
            for result in results:
                # Get predictions
                boxes = result.boxes.xyxy.numpy()  # Bounding box coordinates
                confidences = result.boxes.conf.numpy()  # Confidence scores

                # Check if any confidence score is above 50%
                if any(conf >= 0.4 for conf in confidences):
                    
                    # Create a unique filename for each frame
                    frame_filename = f"{os.path.splitext(video_file)[0]}_frame_{frame_count:04d}.jpg"
                    frame_filepath = os.path.join(frames_dir, frame_filename)
                    
                    result.save(frame_filepath)  # save to disk
                    print(f"Saved {frame_filepath}")
                    break 

            frame_count += 1

        # Release the video capture object
        cap.release()

    # Close any open windows (if you used cv2.imshow)
    # cv2.destroyAllWindows()

if __name__ == "__main__":
    process_frames_from_videos()



