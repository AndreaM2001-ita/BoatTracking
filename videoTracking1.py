from collections import defaultdict
import cv2
import os
import numpy as np
from ultralytics import YOLO

def track_video(video_path, output_path, currentModel):
    # load the model
    model = YOLO(currentModel)
    # open the video file
    cap = cv2.VideoCapture(video_path)
    track_history = defaultdict(lambda: [])

    # get the video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # define the codec and create VideoWriter object
    out = cv2.VideoWriter(
        output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame_width, frame_height)
    )
    # loop through the video frames
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            results = model.track(frame, persist=True,imgsz=(frame_width, frame_height), conf=0.5)
            boxes = results[0].boxes.xywh.cpu()
            track_ids = (
                results[0].boxes.id.int().cpu().tolist()
                if results[0].boxes.id is not None
                else None
            )
            annotated_frame = results[0].plot()
            # plot the tracks
            if track_ids:
                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = box
                    track = track_history[track_id]
                    track.append((float(x), float(y)))  # x, y center point
                    if len(track) > 30:  # retain 30 tracks for 30 frames
                        track.pop(0)
                    # draw the tracking lines
                    points = np.array(track).astype(np.int32).reshape((-1, 1, 2))
                    cv2.polylines(
                        annotated_frame,
                        [points],
                        isClosed=False,
                        color=(230, 230, 230),
                        thickness=2,
                    )
            # write the annotated frame
            out.write(annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break
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

    # Example: analyze all .m4v videos in the 'videos' folder
    for video_file in os.listdir(videos_dir):
        if video_file.endswith('.m4v'):
            video_path = os.path.join(videos_dir, video_file)
            output_path = os.path.join(output_dir, f"output_{video_file}")
            track_video(video_path, output_path, "trainedPrototypewithCars2.pt")