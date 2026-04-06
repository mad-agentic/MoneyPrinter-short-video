from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import re
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cache import get_accounts
from api.log_stream import add_log
from llm_provider import ensure_model_selected, generate_text

router = APIRouter(prefix="/twitter", tags=["twitter"])


class GeneratePostRequest(BaseModel):
    topic: str = ""


class PostRequest(BaseModel):
    text: str
    topic: str = ""


def _get_twitter_account(account_id: str) -> dict:
    accounts = get_accounts("twitter")
    acc = next((a for a in accounts if a["id"] == account_id), None)
    if not acc:
        raise HTTPException(status_code=404, detail="Twitter account not found")
    return acc


@router.get("/{account_id}/posts")
def get_posts(account_id: str):
    acc = _get_twitter_account(account_id)
    return acc.get("posts", [])


@router.post("/{account_id}/generate-post")
def generate_post(account_id: str, body: GeneratePostRequest):
    ensure_model_selected()
    acc = _get_twitter_account(account_id)
    topic = body.topic or acc.get("topic", "general topics")

    add_log("info", f"Generating Twitter post for topic: {topic}")
    try:
        text = generate_text(
            f"Generate a Twitter post about: {topic}. "
            "Limit to 2 sentences. Choose a specific sub-topic. "
            "Return only the post text, no quotes or extra commentary."
        )
        if not text:
            raise HTTPException(status_code=500, detail="LLM returned empty response")

        text = re.sub(r"\*", "", text).replace('"', "").strip()
        if len(text) >= 260:
            text = text[:257].rsplit(" ", 1)[0] + "..."

        add_log("success", f"Post generated ({len(text)} chars)")
        return {"post": text}
    except HTTPException:
        raise
    except Exception as e:
        add_log("error", f"Failed to generate post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/post")
def post_to_twitter(account_id: str, body: PostRequest, background_tasks: BackgroundTasks):
    acc = _get_twitter_account(account_id)
    fp_profile = acc.get("firefox_profile", "")
    if not fp_profile:
        raise HTTPException(status_code=400, detail="Firefox profile not configured for this account")

    add_log("info", f"Queuing Twitter post for @{acc['nickname']}...")
    background_tasks.add_task(
        _do_post,
        account_id,
        acc["nickname"],
        fp_profile,
        body.topic or acc.get("topic", ""),
        body.text,
    )
    return {"status": "started", "message": "Posting to Twitter in background"}


def _do_post(account_id: str, nickname: str, fp_profile: str, topic: str, text: str):
    try:
        from classes.Twitter import Twitter
        add_log("info", f"Launching Firefox for Twitter (@{nickname})...")
        bot = Twitter(account_id, nickname, fp_profile, topic)
        bot.post(text)
        bot.browser.quit()
        add_log("success", "Posted to Twitter successfully!")
    except Exception as e:
        add_log("error", f"Twitter post failed: {e}")
