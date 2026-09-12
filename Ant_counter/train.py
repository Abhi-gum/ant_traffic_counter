from ultralytics import YOLO

model = YOLO("yolo11n.pt")

model.train(
    data="Ant Traffic.v1i.yolov11/data.yaml",
    epochs=50,
    imgsz=640,
    batch=8
)