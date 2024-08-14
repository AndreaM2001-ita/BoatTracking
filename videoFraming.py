import cv2
import os

from ultralytics import YOLO

def process_frames_from_videos():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # current dir
    videos_dir = os.path.join(script_dir, 'videos')
    files = os.listdir(videos_dir)  # list of all files in dir 

    video_files = [f for f in files if f.endswith('.m4v')]  # find .m4v files

    frames_dir = os.path.join(script_dir, 'frames')
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    model=YOLO('trained_model.pt')

    

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
            
            results=model.predict(frame, save=True, imgsz=(1920,1080), conf=0.8)

            for result in results:
                boxes = result.boxes  # Boxes object for bounding box outputs
                
                # Create a unique filename for each frame
                frame_filename = f"{os.path.splitext(video_file)[0]}_frame_{frame_count:04d}.jpg"
                frame_filepath = os.path.join(frames_dir, frame_filename)
                

                result.save(frame_filepath)  # save to disk
                # Save the frame as an image file
                #cv2.imwrite(frame_filepath, frame)
                print(f"Saved {frame_filepath}")

                frame_count += 1

        # Release the video capture object
        cap.release()

    # Close any open windows (if you used cv2.imshow)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_frames_from_videos()