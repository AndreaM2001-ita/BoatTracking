import cv2
import os
from ultralytics import YOLO

def analyze_video(video_path, output_path, model_path):
    # Load the pretrained YOLO model
    model = YOLO(model_path)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run inference on the frame
        results = model.predict(frame, imgsz=(width, height), conf=0.5)
        
        # Draw bounding boxes and labels on the frame
        for result in results:
            for box in result.boxes:
                # Get bounding box coordinates and confidence
                x1, y1, x2, y2 = map(int, box.xyxy[0].numpy())
                confidence = box.conf[0].item()
                
                # Get the class ID and class name
                class_id = int(box.cls[0])
                class_name = result.names[class_id]  # Get the class name from the result object
                
                # Create the label with both class name and confidence
                label = f"{class_name} {confidence:.2f}"
                
                # Draw the bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Put the label above the bounding box
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        # Write the frame to the output video
        out.write(frame)
    
    # Release video objects
    cap.release()
    out.release()
    print(f"Processed video saved to {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  # current dir
    videos_dir = os.path.join(script_dir, 'videos')
    output_dir = os.path.join(script_dir, 'output')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Example: analyze all .m4v videos in the 'videos' folder
    for video_file in os.listdir(videos_dir):
        if video_file.endswith('.m4v'):
            video_path = os.path.join(videos_dir, video_file)
            output_path = os.path.join(output_dir, f"output_{video_file}")
            analyze_video(video_path, output_path, "trainedPrototypewithCars2.pt")