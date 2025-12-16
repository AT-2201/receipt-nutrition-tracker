from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import uuid
import os
from app.ocr_service import extract_text_from_image
from app.parse_service import parse_receipt_text
from app.ocr_service import extract_text_from_image
from app.nutrition_service import compute_nutrition_for_item
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.models import Receipt, ReceiptItem, Nutrition
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Receipt Nutrition Tracker API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class UploadResponse(BaseModel):
    receipt_id: str
    filename: str
    status: str


class OCRResponse(BaseModel):
    receipt_id: str
    raw_text: str


class ParsedReceiptResponse(BaseModel):
    receipt_id: str
    items: list


class NutritionResponse(BaseModel):
    receipt_id: str
    nutrition: list


@app.post("/receipts/upload", response_model=UploadResponse)
async def upload_receipt(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are allowed.")

    # Create a unique ID for this receipt
    receipt_id = str(uuid.uuid4())

    # Save file to uploads folder
    file_ext = file.filename.split(".")[-1]
    saved_filename = f"{receipt_id}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    # Write file to disk
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return UploadResponse(
        receipt_id=receipt_id,
        filename=saved_filename,
        status="uploaded"
    )


@app.post("/receipts/ocr/{receipt_id}", response_model=OCRResponse)
async def run_ocr(receipt_id: str):
    # Find the saved image
    files = os.listdir(UPLOAD_DIR)
    matching_files = [f for f in files if f.startswith(receipt_id)]

    if not matching_files:
        raise HTTPException(status_code=404, detail="Receipt image not found.")

    image_path = os.path.join(UPLOAD_DIR, matching_files[0])

    # Extract OCR text
    raw_text = extract_text_from_image(image_path)

    return OCRResponse(
        receipt_id=receipt_id,
        raw_text=raw_text
    )


@app.post("/receipts/parse/{receipt_id}", response_model=ParsedReceiptResponse)
async def parse_receipt(receipt_id: str):
    # Find saved file
    files = os.listdir(UPLOAD_DIR)
    matching_files = [f for f in files if f.startswith(receipt_id)]

    if not matching_files:
        raise HTTPException(status_code=404, detail="Receipt image not found.")

    image_path = os.path.join(UPLOAD_DIR, matching_files[0])

    # Step 1: OCR
    raw_text = extract_text_from_image(image_path)

    # Step 2: Parse structured items
    items = parse_receipt_text(raw_text)

    return ParsedReceiptResponse(
        receipt_id=receipt_id,
        items=items
    )


@app.post("/receipts/nutrition/{receipt_id}", response_model=NutritionResponse)
async def generate_nutrition(
    receipt_id: str,
    db: Session = Depends(get_db)
):
    try:
        print("➡️ Nutrition endpoint called:", receipt_id)

        files = os.listdir(UPLOAD_DIR)
        matching = [f for f in files if f.startswith(receipt_id)]
        if not matching:
            raise HTTPException(status_code=404, detail="Receipt image not found")

        image_path = os.path.join(UPLOAD_DIR, matching[0])

        print("🧠 Running OCR...")
        raw_text = extract_text_from_image(image_path)

        print("📦 Parsing items...")
        items = parse_receipt_text(raw_text)

        print("💾 Saving to DB...")
        receipt = db.query(Receipt).filter_by(receipt_id=receipt_id).first()
        if not receipt:
            receipt = Receipt(receipt_id=receipt_id, user_id=1)
            db.add(receipt)
            db.commit()

        nutrition_results = []

        for item in items:
            item_row = ReceiptItem(
                receipt_id=receipt_id,
                item_name=item["item_name"],
                quantity=item["quantity"],
                unit=item["unit"],
                price=item["price"]
            )
            db.add(item_row)
            db.commit()
            db.refresh(item_row)

            nutrition = compute_nutrition_for_item(item)
            if nutrition:
                db.add(Nutrition(
                    item_id=item_row.item_id,
                    quantity_grams=nutrition["quantity_grams"],
                    calories=nutrition["calories"],
                    protein=nutrition["protein"],
                    carbs=nutrition["carbs"],
                    fat=nutrition["fat"]
                ))
                db.commit()
                nutrition_results.append(nutrition)

        print("✅ Nutrition processing complete")

        return NutritionResponse(
            receipt_id=receipt_id,
            nutrition=nutrition_results
        )

    except Exception as e:
        print("❌ ERROR in nutrition endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

