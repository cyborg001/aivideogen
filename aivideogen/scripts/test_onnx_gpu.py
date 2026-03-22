import onnxruntime as ort
print(f"ONNX Runtime Version: {ort.__version__}")
providers = ort.get_available_providers()
print(f"Available Providers: {providers}")
if 'DmlExecutionProvider' in providers:
    print("SUCCESS: DirectML (GPU) is AVAILABLE")
else:
    print("WARNING: DirectML NOT FOUND. Using CPU.")
