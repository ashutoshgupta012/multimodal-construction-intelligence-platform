
import streamlit as st
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ConstructionAI",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Multimodal Construction Intelligence Platform")
st.write("Upload a construction image and let AI detect objects in it.")

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


# ---------------- LOAD AI MODEL ----------------
@st.cache_resource
def load_model():
    return YOLO("yolo11n.pt")


# ---------------- SIDEBAR ----------------
st.sidebar.title("ConstructionAI")
st.sidebar.write("AI-Powered Construction Analysis")
page = st.sidebar.radio(
    "Choose Module",
    ["Dashboard", "Image Analysis", "Safety Monitor",
     "Crack Analysis", "Cost Estimator", "AI Assistant"]
)


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome to your Construction Intelligence Platform.")

    col1, col2, col3 = st.columns(3)
    col1.metric("AI Model", "YOLO11n")
    col2.metric("Image Limit", "10 MB")
    col3.metric("Analysis", "Object Detection")

    st.info(
        "Select Image Analysis from the sidebar to upload an image "
        "and run AI object detection."
    )


# ---------------- IMAGE ANALYSIS ----------------
elif page == "Image Analysis":
    st.header("AI Image Analysis")
    st.write("Upload a JPEG, PNG, or WEBP image to detect objects.")

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png", "webp"]
    )

    confidence = st.slider(
        "Detection confidence",
        min_value=0.10,
        max_value=0.90,
        value=0.25,
        step=0.05
    )

    if uploaded_file is not None:
        content = uploaded_file.getvalue()

        if len(content) == 0:
            st.error("The uploaded file is empty.")

        elif len(content) > MAX_FILE_SIZE:
            st.error("Image size must not exceed 10 MB.")

        else:
            try:
                image = Image.open(BytesIO(content))
                image.verify()

                image = Image.open(BytesIO(content))

                if image.format not in ALLOWED_FORMATS:
                    st.error("Please upload a JPEG, PNG, or WEBP image.")
                    st.stop()

                image.load()
                image = image.convert("RGB")

                st.subheader("Uploaded Image")
                st.image(image, use_container_width=True)

                col1, col2, col3 = st.columns(3)
                col1.metric("Width", f"{image.width} px")
                col2.metric("Height", f"{image.height} px")
                col3.metric("File Size", f"{len(content) / 1024:.1f} KB")

                if st.button("Analyze Image", type="primary"):
                    try:
                        with st.spinner("Loading AI model and detecting objects..."):
                            model = load_model()
                            results = model.predict(
                                source=image,
                                conf=confidence,
                                verbose=False
                            )

                        result = results[0]
                        detections = []

                        for box in result.boxes:
                            class_id = int(box.cls[0].item())
                            score = float(box.conf[0].item())
                            coordinates = [
                                round(float(value), 2)
                                for value in box.xyxy[0].tolist()
                            ]

                            detections.append({
                                "Object": model.names[class_id],
                                "Confidence": f"{score * 100:.2f}%",
                                "Bounding Box": str(coordinates)
                            })

                        st.subheader("Detection Results")

                        # Ultralytics returns an image in BGR format.
                        annotated_image = result.plot()[:, :, ::-1].copy()
                        st.image(
                            annotated_image,
                            caption="AI Object Detection",
                            use_container_width=True
                        )

                        st.metric("Objects Detected", len(detections))

                        if detections:
                            st.dataframe(
                                detections,
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.warning(
                                "No objects detected above the selected "
                                "confidence threshold."
                            )

                    except Exception as error:
                        st.error(f"AI analysis failed: {error}")

            except (
                UnidentifiedImageError,
                OSError,
                ValueError
            ):
                st.error("The uploaded file is not a valid image.")


# ---------------- OTHER MODULES ----------------
elif page == "Safety Monitor":
    st.header("Safety Monitor")
    st.info(
        "A dedicated construction safety detection model is not "
        "configured in this version."
    )
    st.write(
        "The general YOLO model should not be treated as a validated "
        "PPE or construction safety monitoring system."
    )


elif page == "Crack Analysis":
    st.header("Crack Analysis")
    st.info(
        "A specialized crack detection model is not configured yet. "
        "General object detection cannot reliably measure structural cracks."
    )


elif page == "Cost Estimator":
    st.header("Construction Cost Estimator")

    area = st.number_input(
        "Building area (square feet)",
        min_value=1.0,
        value=1000.0
    )

    rate = st.number_input(
        "Estimated cost per square foot (₹)",
        min_value=1.0,
        value=1800.0
    )

    quality = st.selectbox(
        "Construction quality",
        ["Basic", "Standard", "Premium"]
    )

    multipliers = {
        "Basic": 0.85,
        "Standard": 1.0,
        "Premium": 1.30
    }

    if st.button("Calculate Estimated Cost", type="primary"):
        total = area * rate * multipliers[quality]

        st.subheader("Estimated Construction Cost")
        st.metric("Total Estimated Cost", f"₹{total:,.2f}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Materials (55%)", f"₹{total * 0.55:,.2f}")
        col2.metric("Labour (25%)", f"₹{total * 0.25:,.2f}")
        col3.metric("Finishing (20%)", f"₹{total * 0.20:,.2f}")

        st.caption(
            "Illustrative estimate only. Actual costs vary by location, "
            "materials, design, and labour rates."
        )


# ---------------- AI ASSISTANT ----------------
elif page == "AI Assistant":
    st.header("Construction AI Assistant")

    question = st.text_input(
        "Ask a construction-related question",
        placeholder="e.g. What is concrete curing?"
    )

    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            q = question.lower()

            answers = {
                "concrete": (
                    "Concrete is made from cement, water, sand, and "
                    "aggregates. The correct mix depends on the intended "
                    "use and engineering specifications."
                ),
                "curing": (
                    "Concrete curing maintains adequate moisture and "
                    "temperature so concrete can develop strength. Follow "
                    "the project's specifications and applicable standards."
                ),
                "safety": (
                    "Construction sites require appropriate PPE, hazard "
                    "assessments, safe access, and compliance with local "
                    "safety regulations."
                ),
                "cement": (
                    "Cement is a binding material used in concrete and "
                    "mortar. Select the type according to project "
                    "requirements and applicable standards."
                ),
                "crack": (
                    "Cracks can have different causes. Their width, pattern, "
                    "location, and progression matter. Have potentially "
                    "structural cracks assessed by a qualified engineer."
                )
            }

            answer = next(
                (value for keyword, value in answers.items() if keyword in q),
                "I do not have a specific answer for that question yet. "
                "Please consult a qualified construction professional "
                "for project-specific engineering advice."
            )

            st.markdown("**Answer:**")
            st.write(answer)
