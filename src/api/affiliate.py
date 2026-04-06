from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import json
import sys
import os
import uuid as uuid_lib
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cache import get_products, add_product, get_accounts, get_afm_cache_path
from api.log_stream import add_log
from llm_provider import ensure_model_selected, generate_text

router = APIRouter(prefix="/affiliate", tags=["affiliate"])


class AddProductRequest(BaseModel):
    affiliate_link: str
    product_title: str = ""
    twitter_account_id: str = ""


class UpdatePitchRequest(BaseModel):
    pitch: str


class ShareRequest(BaseModel):
    pitch: str = ""


def _write_products(products: list) -> None:
    with open(get_afm_cache_path(), "w", encoding="utf-8") as f:
        json.dump({"products": products}, f, indent=4)


def _get_product_index(product_id: str) -> tuple[list, int]:
    products = get_products()
    idx = next((i for i, p in enumerate(products) if p["id"] == product_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return products, idx


@router.get("/products")
def list_products():
    return get_products()


@router.post("/products")
def create_product(body: AddProductRequest):
    if not body.affiliate_link.strip():
        raise HTTPException(status_code=400, detail="affiliate_link is required")

    product = {
        "id": str(uuid_lib.uuid4()),
        "affiliate_link": body.affiliate_link.strip(),
        "product_title": body.product_title.strip(),
        "twitter_account_id": body.twitter_account_id.strip(),
        "pitch": "",
        "shared": False,
        "shared_at": None,
    }
    add_product(product)
    return product


@router.delete("/products/{product_id}")
def delete_product(product_id: str):
    products = get_products()
    updated = [p for p in products if p["id"] != product_id]
    if len(updated) == len(products):
        raise HTTPException(status_code=404, detail="Product not found")
    _write_products(updated)
    return {"ok": True}


@router.post("/products/{product_id}/generate-pitch")
def generate_pitch(product_id: str):
    ensure_model_selected()
    products, idx = _get_product_index(product_id)
    product = products[idx]

    title = product.get("product_title") or "Amazon product"
    link = product.get("affiliate_link", "")

    add_log("info", f"Generating pitch for: {title}")
    try:
        prompt = (
            f"Write a short, compelling Twitter marketing pitch for this product. "
            f"Product: '{title}'. "
            f"Keep it under 220 characters so there's room for the link. "
            f"Return only the pitch text, no hashtags, no quotes."
        )
        pitch = generate_text(prompt)
        if not pitch:
            raise Exception("LLM returned empty pitch")

        pitch = pitch.strip().strip('"').strip()
        # Append link if not already present
        if link and link not in pitch:
            pitch = pitch.rstrip(".,") + f"\n{link}"

        products[idx]["pitch"] = pitch
        _write_products(products)
        add_log("success", "Affiliate pitch generated!")
        return {"pitch": pitch}
    except HTTPException:
        raise
    except Exception as e:
        add_log("error", f"Pitch generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/products/{product_id}/pitch")
def update_pitch(product_id: str, body: UpdatePitchRequest):
    products, idx = _get_product_index(product_id)
    products[idx]["pitch"] = body.pitch
    _write_products(products)
    return {"ok": True}


@router.post("/products/{product_id}/share")
def share_pitch(product_id: str, body: ShareRequest, background_tasks: BackgroundTasks):
    products, idx = _get_product_index(product_id)
    product = products[idx]

    twitter_account_id = product.get("twitter_account_id", "")
    if not twitter_account_id:
        raise HTTPException(status_code=400, detail="No Twitter account linked to this product")

    accounts = get_accounts("twitter")
    acc = next((a for a in accounts if a["id"] == twitter_account_id), None)
    if not acc:
        raise HTTPException(status_code=404, detail="Linked Twitter account not found")

    fp_profile = acc.get("firefox_profile", "")
    if not fp_profile:
        raise HTTPException(status_code=400, detail="Twitter account has no Firefox profile configured")

    pitch_text = body.pitch.strip() or product.get("pitch", "").strip()
    if not pitch_text:
        raise HTTPException(status_code=400, detail="No pitch text to share")

    add_log("info", f"Sharing affiliate pitch via @{acc['nickname']}...")
    background_tasks.add_task(
        _do_share,
        product_id,
        twitter_account_id,
        acc["nickname"],
        fp_profile,
        acc.get("topic", ""),
        pitch_text,
    )
    return {"status": "started", "message": "Sharing pitch in background"}


def _do_share(
    product_id: str,
    account_id: str,
    nickname: str,
    fp_profile: str,
    topic: str,
    pitch: str,
):
    try:
        from classes.Twitter import Twitter
        add_log("info", f"Launching Firefox to share affiliate pitch via @{nickname}...")
        bot = Twitter(account_id, nickname, fp_profile, topic)
        bot.post(pitch)
        bot.browser.quit()

        # Mark product as shared
        products = get_products()
        for p in products:
            if p["id"] == product_id:
                p["shared"] = True
                p["shared_at"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                break
        _write_products(products)
        add_log("success", "Affiliate pitch shared on Twitter!")
    except Exception as e:
        add_log("error", f"Share failed: {e}")
