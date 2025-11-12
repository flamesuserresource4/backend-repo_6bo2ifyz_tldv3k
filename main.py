import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Chocolate

app = FastAPI(title="Handmade Chocolate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Handmade Chocolate API is running"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# -------------------- Chocolate Endpoints --------------------

class ChocolateCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    cacao_percent: Optional[int] = None
    image: Optional[str] = None
    tags: Optional[List[str]] = []
    in_stock: bool = True

@app.post("/api/chocolates")
def create_chocolate(payload: ChocolateCreate):
    try:
        chocolate = Chocolate(**payload.model_dump())
        inserted_id = create_document("chocolate", chocolate)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chocolates")
def list_chocolates(category: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    try:
        filter_dict = {}
        if category:
            filter_dict["category"] = category
        if q:
            # Simple text search across name and tags
            filter_dict["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"tags": {"$in": [q]}}
            ]
        docs = get_documents("chocolate", filter_dict, limit)
        # Convert ObjectId to string for JSON
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chocolates/{choc_id}")
def get_chocolate(choc_id: str):
    try:
        if db is None:
            raise Exception("Database not available")
        doc = db["chocolate"].find_one({"_id": ObjectId(choc_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Chocolate not found")
        doc["id"] = str(doc.get("_id"))
        doc.pop("_id", None)
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chocolates/seed")
def seed_chocolates():
    try:
        if db is None:
            raise Exception("Database not available")
        count = db["chocolate"].count_documents({})
        if count > 0:
            return {"inserted": 0, "message": "Collection already has data"}
        samples = [
            {
                "name": "Sea Salt Caramel Truffle",
                "description": "Silky caramel center with a kiss of sea salt, enrobed in dark chocolate.",
                "price": 3.5,
                "category": "Truffle",
                "cacao_percent": 70,
                "image": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?q=80&w=1600&auto=format&fit=crop",
                "tags": ["caramel", "salted", "dark"],
                "in_stock": True,
            },
            {
                "name": "Hazelnut Praline Bonbon",
                "description": "Roasted hazelnut praline with a creamy finish, dipped in milk chocolate.",
                "price": 3.0,
                "category": "Bonbon",
                "cacao_percent": 45,
                "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?q=80&w=1600&auto=format&fit=crop",
                "tags": ["hazelnut", "praline", "milk"],
                "in_stock": True,
            },
            {
                "name": "Raspberry Velvet Heart",
                "description": "Tart raspberry ganache balanced with rich dark chocolate in a heart shell.",
                "price": 3.2,
                "category": "Bonbon",
                "cacao_percent": 64,
                "image": "https://images.unsplash.com/photo-1585145197082-583a1a5b86b8?q=80&w=1600&auto=format&fit=crop",
                "tags": ["raspberry", "fruit", "dark"],
                "in_stock": True,
            },
            {
                "name": "Almond Crunch Bar",
                "description": "Toasted almond nibs folded into a crisp 72% dark chocolate bar.",
                "price": 6.5,
                "category": "Bar",
                "cacao_percent": 72,
                "image": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?q=80&w=1600&auto=format&fit=crop",
                "tags": ["almond", "bar", "dark"],
                "in_stock": True,
            },
        ]
        result = db["chocolate"].insert_many(samples)
        return {"inserted": len(result.inserted_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
