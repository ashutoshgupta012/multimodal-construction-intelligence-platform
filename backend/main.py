
import os
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app = FastAPI(
    title="ConstructionAI API",
    description="Multimodal Construction Intelligence Platform",
    version="1.0.0",
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

# Set FRONTEND_URL in Render to your deployed Vercel URL.
# Example: https://your-project.vercel.app
frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if frontend_url:
    allowed_origins.append(frontend_url)

# Optional: allow additional origins separated by commas.
extra_origins = os.getenv("EXTRA_FRONTEND_URLS", "")

for origin in extra_origins.split(","):
    origin = origin.strip().rstrip("/")
    if origin and origin not in allowed_origins:
        allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# --------------------------------------------------
# YOLO MODEL
# --------------------------------------------------

model = None
model_error = None

try:
    model_path = os.getenv("YOLO_MODEL_PATH", "yolo11n.pt")
    model = YOLO(model_path)
    print(f"YOLO model loaded successfully: {model_path}")

except Exception as error:
    model_error = str(error)
    print(f"Warning: YOLO model could not be loaded: {model_error}")


# --------------------------------------------------
# IMAGE VALIDATION HELPER
# --------------------------------------------------

async def read_image(file: UploadFile):
    """
    Read and validate an uploaded image.

    Returns:
        image: A PIL RGB image
        image_format: Original image format
        image_bytes: Original image bytes
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a file with a valid filename.",
        )

    content_type = (file.content_type or "").lower()

    if content_type and not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image.",
        )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 10 MB.",
        )

    try:
        # Verify image integrity before processing.
        with Image.open(BytesIO(image_bytes)) as check_image:
            image_format = check_image.format

            if image_format not in ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported image format. Use JPEG, PNG, or WEBP.",
                )

            check_image.verify()

        # Reopen the verified image for actual processing.
        with Image.open(BytesIO(image_bytes)) as opened_image:
            image = opened_image.convert("RGB")

        return image, image_format, image_bytes

    except HTTPException:
        raise

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid or supported image.",
        )


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "success": True,
        "message": "ConstructionAI backend is running.",
        "docs": "/docs",
        "health": "/api/health",
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ConstructionAI API",
        "ai_model_loaded": model is not None,
        "ai_model_error": model_error if model is None else None,
    }


# --------------------------------------------------
# IMAGE ANALYSIS
# --------------------------------------------------

@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    image, image_format, image_bytes = await read_image(file)

    width, height = image.size

    return {
        "success": True,
        "filename": file.filename,
        "format": image_format,
        "width": width,
        "height": height,
        "size_bytes": len(image_bytes),
        "size_mb": round(len(image_bytes) / (1024 * 1024), 2),
        "message": "Image uploaded and validated successfully.",
    }


# --------------------------------------------------
# YOLO OBJECT DETECTION
# --------------------------------------------------

@app.post("/api/detect-objects")
async def detect_objects(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI detection model is unavailable. "
                "Check the Render deployment logs and model configuration."
            ),
        )

    image, image_format, image_bytes = await read_image(file)

    try:
        # Run object detection.
        results = model.predict(
            source=image,
            conf=0.25,
            verbose=False,
        )

        detections = []

        if results:
            result = results[0]
            boxes = result.boxes

            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0].item())
                    confidence = float(box.conf[0].item())

                    coordinates = box.xyxy[0].tolist()

                    class_names = result.names
                    if isinstance(class_names, dict):
                        object_name = class_names.get(
                            class_id,
                            str(class_id),
                        )
                    else:
                        object_name = (
                            class_names[class_id]
                            if class_id < len(class_names)
                            else str(class_id)
                        )

                    detections.append(
                        {
                            "object": object_name,
                            "confidence": round(confidence * 100, 2),
                            "box": {
                                "x1": round(float(coordinates[0]), 2),
                                "y1": round(float(coordinates[1]), 2),
                                "x2": round(float(coordinates[2]), 2),
                                "y2": round(float(coordinates[3]), 2),
                            },
                        }
                    )

        return {
            "success": True,
            "filename": file.filename,
            "format": image_format,
            "width": image.width,
            "height": image.height,
            "size_bytes": len(image_bytes),
            "count": len(detections),
            "detections": detections,
            "message": (
                "Object detection completed successfully."
                if detections
                else "No objects were detected in this image."
            ),
        }

    except HTTPException:
        raise

    except Exception as error:
        print(f"Object detection error: {error}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the image.",
        )
