
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO


app = FastAPI(
    title="Construction Intelligence Platform",
    description="AI-powered construction analysis platform",
    version="1.0.0",
)

# Allow the React frontend to connect to the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

# Load the pretrained AI model.
# The weights may download automatically on first use.
model = None

try:
    model = YOLO("yolo11n.pt")
    print("AI model loaded successfully.")
except Exception as error:
    print(f"AI model loading failed: {error}")


@app.get("/")
def home():
    return {
        "success": True,
        "message": "ConstructionAI backend is running!",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "ai_model_loaded": model is not None,
    }


async def read_image(file: UploadFile):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select an image.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 10 MB.",
        )

    try:
        image = Image.open(BytesIO(content))
        image.verify()

        # Reopen the image after verification.
        image = Image.open(BytesIO(content))

        if image.format not in ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail="Upload a JPEG, PNG, or WEBP image.",
            )

        image.load()

        return {
            "image": image.convert("RGB"),
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "size_bytes": len(content),
        }

    except HTTPException:
        raise

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )


@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    data = await read_image(file)

    return {
        "success": True,
        "filename": file.filename,
        "image_details": {
            "width": data["width"],
            "height": data["height"],
            "format": data["format"],
            "size_bytes": data["size_bytes"],
        },
        "message": "Image uploaded and validated successfully.",
    }


@app.post("/api/detect-objects")
async def detect_objects(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI model is unavailable. Check the backend terminal "
                "and your internet connection."
            ),
        )

    data = await read_image(file)

    try:
        predictions = model.predict(
            source=data["image"],
            conf=0.25,
            verbose=False,
        )

        detections = []

        for prediction in predictions:
            for box in prediction.boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())

                detections.append({
                    "object": model.names[class_id],
                    "confidence": round(confidence * 100, 2),
                    "box": [
                        round(float(value), 2)
                        for value in box.xyxy[0].tolist()
                    ],
                })

        return {
            "success": True,
            "filename": file.filename,
            "image_details": {
                "width": data["width"],
                "height": data["height"],
                "format": data["format"],
            },
            "count": len(detections),
            "detections": detections,
            "message": (
                "Object detection completed successfully."
                if detections
                else "No objects detected above the confidence threshold."
            ),
        }

    except Exception as error:
        print(f"AI detection error: {error}")

        raise HTTPException(
            status_code=500,
            detail="AI detection failed. Check the backend terminal.",
        )