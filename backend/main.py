
import os
from io import BytesIO

import streamlit as st
import pandas as pd
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ConstructionAI",
    page_icon="🏗️",
    layout="wide",
)

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


# --------------------------------------------------
# MODEL LOADING
# --------------------------------------------------

@st.cache_resource
def load_model():
    model_path = os.getenv("YOLO_MODEL_PATH", "yolo11n.pt")
    return YOLO(model_path)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #101722;
    color: #f1f5f9;
}
[data-testid="stSidebar"] {
    background-color: #172b3b;
}
.metric-card {
    background: #1b2938;
    border: 1px solid #34475b;
    padding: 20px;
    border-radius: 12px;
}
h1, h2, h3 {
    color: #e5eef8;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("🏗️ ConstructionAI")
    st.caption("Construction Intelligence Platform")

    page = st.radio(
        "Navigation",
        ["Dashboard", "Image Analysis", "About"],
    )

    st.divider()
    st.caption("AI-powered image analysis")


# --------------------------------------------------
# LOAD AI MODEL
# --------------------------------------------------

@st.cache_resource
def get_model_status():
    try:
        return load_model(), None
    except Exception as exc:
        return None, str(exc)


with st.spinner("Checking AI model..."):
    model, model_error = get_model_status()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.title("🏗️ ConstructionAI")
st.write("AI-powered construction image analysis dashboard.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("Application")
    st.success("Streamlit is running")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("AI Model")
    if model is not None:
        st.success("YOLO model ready")
    else:
        st.error("Model unavailable")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("Image Analysis")
    st.write("Ready for image upload")
    st.markdown("</div>", unsafe_allow_html=True)

if model_error:
    st.error("The YOLO model could not be loaded.")
    with st.expander("Technical details"):
        st.code(model_error)

st.divider()


# --------------------------------------------------
# IMAGE ANALYSIS
# --------------------------------------------------

if page == "Image Analysis":
    st.header("Image Analysis")
    st.write("Upload a construction image to detect objects.")

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png", "webp"],
    )

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()

        if len(image_bytes) > MAX_FILE_SIZE:
            st.error("Image must not exceed 10 MB.")
            st.stop()

        try:
            with Image.open(BytesIO(image_bytes)) as original:
                image_format = original.format

                if image_format not in ALLOWED_FORMATS:
                    st.error("Unsupported image format.")
                    st.stop()

                image = original.convert("RGB")

        except (UnidentifiedImageError, OSError, ValueError):
            st.error("Please upload a valid image.")
            st.stop()

        st.image(
            image,
            caption="Uploaded construction image",
            use_container_width=True,
        )

        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Dimensions:** {image.width} × {image.height}")
        st.write(f"**File size:** {len(image_bytes) / 1024:.2f} KB")

        if st.button(
            "Run AI Detection",
            type="primary",
            disabled=model is None,
        ):
            try:
                with st.spinner("Analyzing image..."):
                    results = model.predict(
                        source=image,
                        conf=0.25,
                        verbose=False,
                    )

                result = results[0]
                boxes = result.boxes
                detections = []

                if boxes is not None:
                    for box in boxes:
                        class_id = int(box.cls[0].item())
                        confidence = float(box.conf[0].item())
                        coords = box.xyxy[0].tolist()

                        names = result.names
                        if isinstance(names, dict):
                            label = names.get(class_id, str(class_id))
                        else:
                            label = (
                                names[class_id]
                                if class_id < len(names)
                                else str(class_id)
                            )

                        detections.append({
                            "Object": label,
                            "Confidence (%)": round(
                                confidence * 100, 2
                            ),
                            "X1": round(float(coords[0]), 2),
                            "Y1": round(float(coords[1]), 2),
                            "X2": round(float(coords[2]), 2),
                            "Y2": round(float(coords[3]), 2),
                        })

                st.subheader("Detection Results")

                annotated = result.plot()
                annotated_image = Image.fromarray(
                    annotated[:, :, ::-1].copy()
                )

                st.image(
                    annotated_image,
                    caption="AI detection output",
                    use_container_width=True,
                )

                st.metric("Objects detected", len(detections))

                if detections:
                    st.dataframe(
                        pd.DataFrame(detections),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No objects were detected.")

                output = BytesIO()
                annotated_image.save(output, format="PNG")

                st.download_button(
                    "Download Annotated Image",
                    data=output.getvalue(),
                    file_name="construction_analysis.png",
                    mime="image/png",
                )

            except Exception:
                st.error(
                    "Detection failed. Check the model and deployment logs."
                )
                st.exception(Exception("See deployment logs for details."))


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

elif page == "About":
    st.header("About ConstructionAI")

    st.write("""
    ConstructionAI is an AI-powered image analysis prototype.

    **Features**
    - Image upload and validation
    - YOLO object detection
    - Object confidence scores
    - Bounding-box coordinates
    - Annotated image download

    Note: The default YOLO model is a general-purpose object detector.
    It does not independently certify construction safety or detect
    structural cracks reliably without a suitable trained model.
    """)


# --------------------------------------------------
# DASHBOARD HOME
# --------------------------------------------------

else:
    st.subheader("Welcome to your dashboard")
    st.write(
        "Select Image Analysis from the sidebar to upload an image "
        "and run object detection."
    )

    if model is None:
        st.warning(
            "AI detection is unavailable until the model loads successfully."
        )
    else:
        st.info("Your AI model is ready for image analysis.")
