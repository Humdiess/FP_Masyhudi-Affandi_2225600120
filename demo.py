import os
from pathlib import Path
import cv2
from ultralytics import YOLO

# Semua path dihitung dari folder tempat demo.py berada
BASE = Path(__file__).resolve().parent

VIDEO_IN = BASE / "demo" / "in" / "demo5-ar.mp4"
VIDEO_OUT = BASE / "demo" / "out" / "demo_hasil6.mp4"
MODEL_PATH = BASE / "best.pt"
TINGGI_TAMPIL = 800  # tinggi jendela preview saja, hasil tetap ukuran asli

if not VIDEO_IN.exists():
    raise SystemExit(f"File tidak ditemukan: {VIDEO_IN}")

VIDEO_OUT.parent.mkdir(parents=True, exist_ok=True)  # buat folder out kalau belum ada

model = YOLO(str(MODEL_PATH))
cap = cv2.VideoCapture(str(VIDEO_IN))
fps = cap.get(cv2.CAP_PROP_FPS) or 30

out = None
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # ukuran output diambil dari frame asli
    if out is None:
        h, w = frame.shape[:2]
        out = cv2.VideoWriter(
            str(VIDEO_OUT), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)
        )

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        imgsz=640,
        conf=0.20,
        verbose=False,
    )
    annotated = results[0].plot()

    out.write(annotated)

    skala = TINGGI_TAMPIL / annotated.shape[0]
    preview = cv2.resize(annotated, None, fx=skala, fy=skala)
    cv2.imshow("YOLOv8 Local Video Tracking", preview)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
if out:
    out.release()
cv2.destroyAllWindows()
print(f"Selesai. Hasil tersimpan di: {VIDEO_OUT}")
