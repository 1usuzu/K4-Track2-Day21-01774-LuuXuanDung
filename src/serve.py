from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os

app = FastAPI()

ARTIFACT_BUCKET = os.environ.get("ARTIFACT_BUCKET", "")
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """
    Tai file model.joblib tu cloud storage ve may khi server khoi dong.
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # Thu tai bang boto3 (AWS S3)
    try:
        import boto3
        s3 = boto3.client("s3")
        s3.download_file(ARTIFACT_BUCKET, MODEL_KEY, MODEL_PATH)
        print(f"Model downloaded from S3: {ARTIFACT_BUCKET}/{MODEL_KEY}")
        return
    except Exception as e_s3:
        pass

    # Thu tai bang google-cloud-storage (GCP)
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(ARTIFACT_BUCKET)
        blob = bucket.blob(MODEL_KEY)
        blob.download_to_filename(MODEL_PATH)
        print("Model downloaded from GCS.")
        return
    except Exception as e_gcs:
        pass


if ARTIFACT_BUCKET:
    try:
        download_model()
    except Exception as e:
        print(f"Warning during download_model: {e}")

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
elif os.path.exists("models/model.joblib"):
    model = joblib.load("models/model.joblib")
else:
    model = None


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """
    Endpoint kiem tra suc khoe server.
    GitHub Actions goi endpoint nay sau khi deploy de xac nhan server dang chay.

    Tra ve: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f10]}
    Dau ra  : JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}

    Thu tu 10 dac trung (khop voi thu tu trong FEATURE_NAMES cua test):
        age, workclass, education_num, marital_status, occupation,
        relationship, sex, capital_gain, capital_loss, hours_per_week
    """
    # TODO 6: Kiem tra so luong dac trung
    if len(req.features) != 10:
        raise HTTPException(status_code=400, detail="Expected 10 features (adult income)")

    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # TODO 7: Goi model.predict([req.features]) de lay ket qua du doan
    pred = int(model.predict([req.features])[0])

    # TODO 8: Tra ve dict chua "prediction" (int) va "label" (string)
    label = "thu_nhap_cao" if pred == 1 else "thu_nhap_thap"
    return {"prediction": pred, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
