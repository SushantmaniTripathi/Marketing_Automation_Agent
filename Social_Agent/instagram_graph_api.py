import os
import asyncio
import requests
import base64
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

def _print(msg):
    """Safe print that handles Windows CP1252 terminals without crashing on emojis."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


class InstagramGraphAPI:
    """Official Instagram Graph API - Reliable, no IP blocking"""
    
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_TOKEN_1')
        self.instagram_account_id = os.getenv('INSTAGRAM_ID_1')
        self.base_url = "https://graph.facebook.com/v21.0"
    
    async def _upload_to_hosting(self, image_path):
        """Upload local image to a temporary public URL for Instagram to access.
        Uses FreeImage.host (primary) — confirmed accessible by Facebook's CDN.
        Falls back to ImgBB if IMGBB_API_KEY is set in .env.
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found at: {image_path}")
            _print(f"[ERROR] Image file not found at: {image_path}")
            return None

        # -- Service 1: FreeImage.host (Primary - Facebook CDN can reach this) --
        try:
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()

            response = await asyncio.to_thread(
                requests.post,
                "https://freeimage.host/api/1/upload",
                data={
                    "key": "6d207e02198a847aa98d0a2a901485a5",  # public demo key
                    "action": "upload",
                    "source": img_b64,
                    "format": "json"
                },
                timeout=45
            )
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image", {}).get("url", "")
                if image_url and image_url.startswith("http"):
                    _print(f"[OK] Image hosted on FreeImage: {image_url}")
                    logger.info(f"Image hosted on FreeImage: {image_url}")
                    return image_url
        except Exception as e:
            logger.warning(f"FreeImage hosting failed: {e}")
            _print(f"[WARN] FreeImage hosting failed: {e}")

        # -- Service 2: ImgBB (Fallback - requires IMGBB_API_KEY in .env) --
        imgbb_key = os.getenv("IMGBB_API_KEY", "")
        if imgbb_key:
            try:
                _print("[INFO] Attempting fallback hosting on ImgBB...")
                with open(image_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()

                response = await asyncio.to_thread(
                    requests.post,
                    "https://api.imgbb.com/1/upload",
                    data={"key": imgbb_key, "image": img_b64},
                    timeout=45
                )
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("data", {}).get("url", "")
                    if image_url:
                        _print(f"[OK] Image hosted on ImgBB: {image_url}")
                        logger.info(f"Image hosted on ImgBB: {image_url}")
                        return image_url
            except Exception as e:
                logger.warning(f"ImgBB hosting failed: {e}")
                _print(f"[ERROR] ImgBB hosting failed: {e}")
        else:
            logger.warning("ImgBB fallback skipped: IMGBB_API_KEY not set in .env")

        logger.error("All image hosting services failed")
        return None

    async def post_to_instagram(self, image_path, caption, hashtags, progress_callback=None):
        """Post content to Instagram using official Graph API"""
        try:
            # Validate credentials
            if not self.access_token or not self.instagram_account_id:
                error_msg = f"❌ Missing Graph API credentials"
                if progress_callback:
                    await progress_callback(error_msg)
                _print("[ERROR] Missing Graph API credentials")
                return False
            
            if progress_callback:
                await progress_callback("📤 Uploading image to temporary hosting...")
            
            # Get public URL for the image
            image_url = await self._upload_to_hosting(image_path)
            
            if not image_url:
                error_msg = "❌ Failed to host image. Please try again."
                if progress_callback:
                    await progress_callback(error_msg)
                return False
            
            _print(f"[OK] Image hosted at: {image_url}")

            if progress_callback:
                await progress_callback("Creating Instagram post...")

            
            # Prepare caption with hashtags
            full_caption = f"{caption}\n\n{' '.join(hashtags[:30])}"
            
            # Step 1: Create media container
            _print("Step 1: Creating media container...")
            container_url = f"{self.base_url}/{self.instagram_account_id}/media"
            
            container_params = {
                'access_token': self.access_token,
                'caption': full_caption,
                'image_url': image_url
            }
            
            print(f"Creating media container for account: {self.instagram_account_id}")
            response = await asyncio.to_thread(
                requests.post,
                container_url,
                params=container_params,
                timeout=60
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_obj = error_data.get('error', {})
                error_msg = error_obj.get('message', 'Unknown error')
                error_code = error_obj.get('code', '?')
                full_msg = f"[code {error_code}] {error_msg}"
                logger.error(f"Container creation failed: {response.status_code} - {response.text}")
                if progress_callback:
                    await progress_callback(f"❌ Upload failed: {full_msg}")
                _print(f"Container creation failed: {response.status_code} - {response.text}")
                return False
            
            container_data = response.json()
            creation_id = container_data.get('id')
            
            if not creation_id:
                if progress_callback:
                    await progress_callback("❌ Failed to create media container")
                _print(f"[ERROR] No creation ID in response: {container_data}")
                return False
            
            _print(f"Media container created: {creation_id}")
            
            # Step 2: Publish the container
            if progress_callback:
                await progress_callback("🚀 Publishing to Instagram...")
            
            _print("Step 2: Publishing media...")
            publish_url = f"{self.base_url}/{self.instagram_account_id}/media_publish"
            publish_params = {
                'access_token': self.access_token,
                'creation_id': creation_id
            }
            
            publish_response = await asyncio.to_thread(
                requests.post,
                publish_url,
                params=publish_params,
                timeout=60
            )
            
            if publish_response.status_code != 200:
                error_data = publish_response.json() if publish_response.text else {}
                error_obj = error_data.get('error', {})
                error_msg = error_obj.get('message', 'Unknown error')
                error_code = error_obj.get('code', '?')
                full_msg = f"[code {error_code}] {error_msg}"
                logger.error(f"Publish failed: {publish_response.status_code} - {publish_response.text}")
                if progress_callback:
                    await progress_callback(f"❌ Publish failed: {full_msg}")
                _print(f"Publish failed: {publish_response.status_code} - {publish_response.text}")
                return False
            
            publish_data = publish_response.json()
            media_id = publish_data.get('id')
            
            if not media_id:
                if progress_callback:
                    await progress_callback("❌ Failed to publish post")
                _print(f"No media ID in response: {publish_data}")
                return False
            
            _print(f"[OK] Post published successfully! Media ID: {media_id}")
            
            if progress_callback:
                await progress_callback("✅ Post published successfully via Official Instagram API!")
            
            return True
            
        except requests.exceptions.Timeout:
            error_msg = "❌ Request timeout - Instagram server not responding"
            if progress_callback:
                await progress_callback(error_msg)
            _print(f"[ERROR] Request timeout - Instagram server not responding")
            return False
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Network error: {str(e)[:100]}"
            if progress_callback:
                await progress_callback(error_msg)
            _print(f"[ERROR] Request exception: {e}")
            return False
        except Exception as e:
            error_msg = f"❌ Posting failed: {str(e)[:100]}"
            if progress_callback:
                await progress_callback(error_msg)
            _print(f"[ERROR] Exception: {type(e).__name__}: {e}")
            return False
