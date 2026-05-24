"""
Post Automation Routes
Instagram posting workflow: topic → hashtags → caption → image → publish
"""

import os
import sys
import re
import json
import random
import requests
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'Social_Agent'))


TREND_DOMAINS = [
    'DeFi', 'Social', 'Gaming', 'Metaverse', 'TuneHub',
    'CupidHub', 'Web3', 'AI', 'P2E'
]


def _normalize_trend_line(text: str) -> str:
    line = re.sub(r'\s+', ' ', (text or '').strip()).strip('"\' ')
    if not line:
        return ''
    # Keep it one crisp strategist sentence.
    if not re.search(r'[.!?]$', line):
        line += '.'
    return line


async def get_trending_topics(limit: int = 10) -> dict:
    """Fetch live, strategist-style trend insights from OpenAI for the last 24 hours."""
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Sample 6-8 domains each click to keep outputs varied and fresh.
        domain_count = random.randint(6, 8)
        selected_domains = random.sample(TREND_DOMAINS, domain_count)
        final_limit = 10

        prompt = (
            "You are a social media strategist for Decentrawood. "
            "Generate EXACTLY 10 top trend insights from the LAST 24 HOURS only. "
            "Use only these possible domains and vary domains across results: "
            f"{', '.join(selected_domains)}. "
            "Do not return headlines or news snippets. Each item must be one punchy, specific, "
            "actionable sentence that sounds scroll-stopping and real. "
            "Avoid generic wording, avoid repeating the same domain focus, and avoid duplicate angles. "
            "Output strict JSON with this shape: "
            "{\"trends\":[{\"line\":\"...\",\"domain\":\"...\"}]}."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You create concise, high-signal trend insights for social growth."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=900,
            response_format={"type": "json_object"}
        )

        payload = json.loads(response.choices[0].message.content or '{}')
        raw_trends = payload.get('trends') if isinstance(payload, dict) else []
        if not isinstance(raw_trends, list):
            raw_trends = []

        items = []
        seen = set()
        for idx, entry in enumerate(raw_trends):
            if isinstance(entry, dict):
                text = _normalize_trend_line(entry.get('line', ''))
                domain = str(entry.get('domain', '')).strip() or 'web3'
            else:
                text = _normalize_trend_line(str(entry))
                domain = 'web3'

            key = text.lower()
            if not text or key in seen:
                continue
            seen.add(key)
            items.append({
                'title': text,
                'topic': text,
                'url': '',
                'niche': domain.lower(),
                'score': max(1, final_limit - idx)
            })
            if len(items) >= final_limit:
                break

        if len(items) < final_limit:
            return {
                'success': False,
                'error': 'Could not generate enough live trends. Please try again.',
                'topics': []
            }

        return {
            'success': True,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'count': len(items),
            'topics': items,
            'note': f"Live ChatGPT trend scan from the last 24h across: {', '.join(selected_domains)}"
        }
    except Exception as e:
        logger.error(f"get_trending_topics error: {e}")
        return {'success': False, 'error': str(e), 'topics': []}


# ─────────────────────────────────────────────
#  STEP 1: HASHTAGS
# ─────────────────────────────────────────────

async def generate_hashtags(topic: str) -> dict:
    """Generate relevant hashtags using Instagram API + OpenAI fallback"""
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        INSTAGRAM_TOKEN = os.getenv('INSTAGRAM_TOKEN_1', '')
        INSTAGRAM_ID = os.getenv('INSTAGRAM_ID_1', '')
        GRAPH_URL = "https://graph.facebook.com/v19.0"

        # Extract keywords using AI
        try:
            kw_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content":
                    f"List 5 single-word Instagram hashtag keywords for: '{topic}'. Return comma-separated only."}],
                max_tokens=60
            )
            keywords = [k.strip().lower() for k in kw_response.choices[0].message.content.split(",")]
        except Exception:
            words = re.findall(r"[a-zA-Z]{3,}", topic.lower())
            keywords = list(dict.fromkeys(words))[:5]

        hashtags = []

        # Try Instagram Graph API
        if INSTAGRAM_TOKEN and INSTAGRAM_ID:
            for word in keywords[:5]:
                try:
                    r = requests.get(f"{GRAPH_URL}/ig_hashtag_search",
                        params={"user_id": INSTAGRAM_ID, "q": word, "access_token": INSTAGRAM_TOKEN},
                        timeout=8)
                    if r.status_code == 200:
                        data = r.json()
                        for tag in data.get('data', [])[:2]:
                            name = tag.get('name', '')
                            if name and f"#{name}" not in hashtags:
                                hashtags.append(f"#{name}")
                except Exception:
                    pass

        # Fill remainder with AI-generated fallbacks
        if len(hashtags) < 10:
            try:
                fb_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content":
                        f"Generate {10 - len(hashtags)} more Instagram hashtags for '{topic}'. "
                        f"Return as #hashtag format, comma-separated. No explanations."}],
                    max_tokens=120
                )
                fb_tags = re.findall(r'#\w+', fb_response.choices[0].message.content)
                for t in fb_tags:
                    if t not in hashtags:
                        hashtags.append(t)
            except Exception:
                pass

        hashtags = hashtags[:10]

        return {
            'success': True,
            'hashtags': hashtags,
            'hashtags_text': ' '.join(hashtags),
            'topic': topic
        }

    except Exception as e:
        logger.error(f"generate_hashtags error: {e}")
        return {'success': False, 'error': str(e)}


# ─────────────────────────────────────────────
#  STEP 2: CAPTION
# ─────────────────────────────────────────────

async def generate_caption(topic: str) -> dict:
    """Generate engaging Instagram caption using OpenAI"""
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": (
                    "You are an expert Instagram content creator. "
                    "Write engaging, authentic captions. Use emojis naturally. "
                    "Keep it between 100-200 words. End with a call to action."
                )
            }, {
                "role": "user",
                "content": f"Write an Instagram caption about: {topic}"
            }],
            max_tokens=300
        )

        caption = response.choices[0].message.content.strip()
        return {'success': True, 'caption': caption, 'topic': topic}

    except Exception as e:
        logger.error(f"generate_caption error: {e}")
        return {'success': False, 'error': str(e)}


# ─────────────────────────────────────────────
#  STEP 3: IMAGE GENERATION
# ─────────────────────────────────────────────

async def generate_image(topic: str, old_image_path: str = None) -> dict:
    """Generate image using IdeogramImageGenerator (Social_Agent module).
    Deletes old_image_path before generating a new one if provided.
    """
    try:
        # Delete old image before generating new one (regenerate flow)
        if old_image_path and os.path.isfile(old_image_path):
            try:
                os.remove(old_image_path)
                logger.info(f"Deleted old image: {old_image_path}")
            except Exception as de:
                logger.warning(f"Could not delete old image: {de}")

        ideogram_path = os.path.join(BASE_DIR, 'Social_Agent', 'src', 'modules', 'ai', 'ideogram_gen.py')
        if not os.path.exists(ideogram_path):
            return {'success': False, 'error': 'Ideogram module not found'}

        import importlib.util
        spec = importlib.util.spec_from_file_location("ideogram_gen", ideogram_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        gen = mod.IdeogramImageGenerator()

        # generate_image is synchronous — do NOT await it
        result = gen.generate_image(topic)

        if result and os.path.isfile(result):
            return {'success': True, 'image_path': result, 'topic': topic}

        return {'success': False, 'error': 'Image generation failed — no output file'}

    except Exception as e:
        logger.error(f"generate_image error: {e}")
        return {'success': False, 'error': str(e)}


# ─────────────────────────────────────────────
#  STEP 4: PUBLISH TO INSTAGRAM
# ─────────────────────────────────────────────

async def publish_to_instagram(image_path: str, caption: str, hashtags: list, schedule_time=None) -> dict:
    """Publish post to Instagram via Graph API"""
    try:
        ig_module_path = os.path.join(BASE_DIR, 'Social_Agent', 'instagram_graph_api.py')
        if not os.path.exists(ig_module_path):
            return {'success': False, 'error': 'Instagram Graph API module not found'}

        import importlib.util
        spec = importlib.util.spec_from_file_location("instagram_graph_api", ig_module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # InstagramGraphAPI reads credentials from env itself — no constructor args
        api = mod.InstagramGraphAPI()

        full_caption = f"{caption}\n\n{' '.join(hashtags)}"

        # Correct method name is post_to_instagram
        success = await api.post_to_instagram(
            image_path=image_path,
            caption=full_caption,
            hashtags=[]
        )

        if success:
            return {
                'success': True,
                'message': '✅ Post published successfully to Instagram!'
            }
        else:
            return {'success': False, 'error': 'Instagram publish returned failure — check logs'}

    except Exception as e:
        logger.error(f"publish_to_instagram error: {e}")
        return {'success': False, 'error': str(e)}
