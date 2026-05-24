"""
Ideogram Image Generator for Social Bot
Uses V_2_TURBO model for best text accuracy + cost efficiency
Includes automatic logo overlay functionality
"""

import os
import sys
import requests
import time
import re
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load environment variables from main project .env
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)


class IdeogramImageGenerator:
    """Generate images using Ideogram API V_2_TURBO with text on image and logo overlay"""
    
    def __init__(self):
        # Reload env to ensure we have the key
        env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
        load_dotenv(env_path, override=True)
        
        self.api_key = os.getenv("IDEOGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("IDEOGRAM_API_KEY not found in environment variables. Check Biz_Agents\\.env file")
        
        self.base_url = "https://api.ideogram.ai/generate"
        self.headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # V_2_TURBO: Best balance of text accuracy + cost efficiency
        self.model = "V_2_TURBO"
        
        # Get script directory for logo paths (go up to Social_Agent folder)
        self.script_dir = Path(__file__).parent.parent.parent.parent
        
    def extract_quoted_text(self, topic):
        """Extract text from quotes in the topic string"""
        matches = re.findall(r'"([^"]+)"', topic)
        if matches:
            return ' '.join(matches)
        return None
    
    def generate_image(self, topic, quoted_text=None):
        """
        Generate professional social media image with Ideogram
        
        Args:
            topic (str): Main topic/concept for the image
            quoted_text (str): Optional text to render on the image (auto-extracted if not provided)
            
        Returns:
            str: Path to generated image, or None if failed
        """
        try:
            # Auto-extract quoted text if not provided
            if quoted_text is None:
                quoted_text = self.extract_quoted_text(topic)
            
            # Build simple, clean prompt for social media images
            if quoted_text:
                prompt = f'''social media image: {topic}

"{quoted_text}" displayed prominently
Modern professional design for Instagram, X, LinkedIn
High-quality visual, engaging aesthetic
NOT a poster - just a clean social media visual'''
            else: 
                prompt = f''' image: {topic}

Professional photography or modern visual design
High-quality, engaging, shareable
NOT a poster - just a clean image'''
            
            # Prepare API request
            payload = {
                "image_request": {
                    "prompt": prompt,
                    "aspect_ratio": "ASPECT_1_1",
                    "model": self.model,
                    "magic_prompt_option": "ON",  # Enhances quality
                    "style_type": "DESIGN"  # Best for social media posts
                }
            }
            
            print(f"🎨 Generating image ...")
            if quoted_text:
                print(f"📝 Text on image: \"{quoted_text}\"")
            
            print(f"🎨 Sending request to Ideogram API (Model: {self.model})...", flush=True)
            
            # Make API request
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=180
            )
            
            print(f"📡 API Response received (Status: {response.status_code})", flush=True)
            
            response.raise_for_status()
            result = response.json()
            
            # Extract image URL
            if "data" in result and len(result["data"]) > 0:
                image_url = result["data"][0].get("url")
                
                if image_url:
                    # Download and save image
                    img_response = requests.get(image_url, timeout=30)
                    img_response.raise_for_status()
                    
                    # Open with PIL
                    img = Image.open(BytesIO(img_response.content))
                    
                    # Create output directory
                    output_dir = self.script_dir / "data" / "generated_images"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save with timestamp
                    filename = output_dir / f"generated_{int(time.time())}.png"
                    img.save(filename, "PNG")
                    print(f"✓ Image saved to: {filename}", flush=True)
                    
                    # Overlay logos automatically
                    print(f"🖌 Applying logo overlays...", flush=True)
                    self.overlay_logos(str(filename))
                    print(f"✓ Logo process complete", flush=True)
                    
                    return str(filename)
                else:
                    print("❌ No image URL in response")
                    return None
            else:
                print("❌ No image data in response")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌  API error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error generating image: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def overlay_logos(self, image_path):
        """
        Overlay both logos on the generated image:
        - deod.png at top-right corner (10% width)
        - DECENTRAWOOD.png at bottom-middle (70% width)
        """
        try:
            # Open the generated image
            base_image = Image.open(image_path)
            base_width, base_height = base_image.size
            
            # Logo 1: Top-right corner (deod.png)
            logo_top_path = self.script_dir / "assets" / "logos" / "deod.png"
            if logo_top_path.exists():
                logo_top = Image.open(logo_top_path)
                
                # Calculate logo size (10% of image width)
                logo_width = int(base_width * 0.10)
                logo_aspect_ratio = logo_top.size[1] / logo_top.size[0]
                logo_height = int(logo_width * logo_aspect_ratio)
                
                # Resize logo
                logo_resized = logo_top.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                
                # Position at top-right with padding
                padding = int(base_width * 0.02)
                position = (base_width - logo_width - padding, padding)
                
                # Paste logo
                base_image.paste(logo_resized, position, logo_resized if logo_resized.mode == 'RGBA' else None)
                
                print(f"✓ Top-right logo applied", flush=True)
            else:
                print(f"⚠️  Top logo not found at {logo_top_path}")
            
            # Logo 2: Bottom-middle (DECENTRAWOOD.png)
            logo_bottom_path = self.script_dir / "assets" / "logos" / "DECENTRAWOOD.png"
            if logo_bottom_path.exists():
                logo_bottom = Image.open(logo_bottom_path)
                
                # Calculate logo size (70% width)
                logo_width_bottom = int(base_width * 0.70)
                logo_aspect_ratio_bottom = logo_bottom.size[1] / logo_bottom.size[0] 
                logo_height_bottom = int(logo_width_bottom * logo_aspect_ratio_bottom)
                
                # Limit height to 75% of image height
                max_logo_height = int(base_height * 0.75)
                if logo_height_bottom > max_logo_height:
                    logo_height_bottom = max_logo_height
                    logo_width_bottom = int(logo_height_bottom / logo_aspect_ratio_bottom)
                
                logo_bottom_resized = logo_bottom.resize((logo_width_bottom, logo_height_bottom), Image.Resampling.LANCZOS)
                
                # Position at bottom-middle with 40% downward shift to touch bottom edge
                x_position = (base_width - logo_width_bottom) // 2  # Center horizontally
                y_position = base_height - logo_height_bottom + int(logo_height_bottom * 0.40)
                position_bottom = (x_position, y_position)
                
                # Paste logo
                if logo_bottom_resized.mode == 'RGBA':
                    base_image.paste(logo_bottom_resized, position_bottom, logo_bottom_resized)
                else:
                    base_image.paste(logo_bottom_resized, position_bottom)
                
                print(f"✓ Bottom-middle logo (DECENTRAWOOD.png) applied!")
            else:
                print(f"⚠️  Bottom logo not found at {logo_bottom_path}")
            
            # Save the final image with both logos
            base_image.save(image_path)
            print(f"✓ Both logos overlaid successfully!")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Logo overlay failed: {str(e)}")
            print(f"   Image saved without logo overlay")
            return False


if __name__ == "__main__":
    # Test the generator
    print("=" * 60)
    
    generator = IdeogramImageGenerator()
    
    # Test 1: Image with text
    print("\nTest 1: Image with text")
    result1 = generator.generate_image(
        "Motivational sunrise over mountains",
        quoted_text="NEVER GIVE UP"
    )
    if result1:
        print(f"✅ Test 1 successful! Image saved: {result1}")
    else:
        print("❌ Test 1 failed")
    
    # Test 2: Image without text
    print("\nTest 2: Image without text")
    result2 = generator.generate_image(
        "Professional tech workspace with laptop"
    )
    if result2:
        print(f"✅ Test 2 successful! Image saved: {result2}")
    else:
        print("❌ Test 2 failed")
    
    # Test 3: Auto-extract quoted text from topic
    print("\nTest 3: Auto-extract quoted text")
    result3 = generator.generate_image(
        'Social media post about fitness with "GET FIT NOW"'
    )
    if result3:
        print(f"✅ Test 3 successful! Image saved: {result3}")
    else:
        print("❌ Test 3 failed")
    
    print("\n" + "=" * 60)
    print("✨ Testing complete!")
