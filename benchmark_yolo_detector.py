
import time
import torch
import numpy as np
from ultralytics import YOLO

def benchmark(model_path, iterations=10):
    print(f"\n--- Benchmarking {model_path} ---")
    try:
        model = YOLO(model_path)
        # Dummy image 640x640
        img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Warmup
        model(img, verbose=False, device='cpu')
        
        times = []
        for _ in range(iterations):
            start = time.time()
            model(img, verbose=False, device='cpu')
            times.append(time.time() - start)
            
        avg_time = sum(times) / iterations
        fps = 1.0 / avg_time
        print(f"Average Inference Time: {avg_time*1000:.2f} ms")
        print(f"Estimated FPS (CPU): {fps:.2f}")
        return avg_time
    except Exception as e:
        print(f"Error benchmarking {model_path}: {e}")
        return None

if __name__ == "__main__":
    v8_time = benchmark("yolov8n.pt")
    v26_time = benchmark("yolo26n.pt")
    
    if v8_time and v26_time:
        improvement = (v8_time - v26_time) / v8_time * 100
        print(f"\n🚀 YOLOv26 is {improvement:.2f}% faster than YOLOv8 on this machine!")
