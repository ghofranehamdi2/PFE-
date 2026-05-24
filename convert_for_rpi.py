from ultralytics import YOLO

print("Export ONNX uniquement - pas de TensorFlow...")
model = YOLO("pi_client/yolo26n.pt")

model.export(
    format="onnx",
    imgsz=416,
    simplify=True
)

print("Termine ! Fichier : pi_client/yolo26n.onnx")
