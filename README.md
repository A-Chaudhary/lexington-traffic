# lexington-traffic
Downloads real-time traffic camera video from any specific intersection in the Lexington-Fayette Urban County from https://trafficvid.lexingtonky.gov/publicmap/

YOLO_v4 on the Darknet framework is run to detect cars in the video feed.

## Object Detection Output for yolov4.weights

<img src="/media_77/output/output_media_w1682618446_22319.gif" width="75%">

### TODO
* [x] Extract Source of Lexington Traffic Cameras
* [x] Save Video File from Parsed chunklist
* [ ] Find Traffic Camera with Optimal Positioning
* [x] Prevent Repeat Video Files with Different Source
* [x] Setup CUDA, OpenCV, Darknet, and Yolo v4
* [x] Run Object Detection on Video
* [ ] Apply Kalman Filtering and DeepSORT
* [ ] Calculate Benefit from Reduced Car Idling 
* [ ] Extrapolate to City Wide Scale

### References
* [Darknet Framework](http://pjreddie.com/darknet/)
* [Yolo v4 Repository](https://github.com/AlexeyAB/darknet)
