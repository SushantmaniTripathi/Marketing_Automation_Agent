import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Import functions from existing modules
from Tag_insta import get_10_existing_hashtags, detect_genre
from Dalle import DALLEImageGenerator

# Load environment variables
load_dotenv()

class SocialMediaContentGenerator:
    def __init__(self):
        """Initialize the unified social media content generator"""
        self.dalle_generator = DALLEImageGenerator()
        
        # Initialize OpenAI client for caption generation
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables!")
        
        self.client = OpenAI(api_key=api_key)
        
    def generate_captions(self, topic, genre, num_captions=3):
        """Generate engaging social media captions using ChatGPT"""
        print(f"\n📝 Generating {num_captions} captions for {genre} content...")
        
        prompt = f"""Generate {num_captions} engaging social media captions for a post about: {topic}

Genre: {genre}

Requirements:
- Each caption should be 1-2 sentences (20-40 words)
- Make them engaging, professional, and platform-appropriate
- Include relevant emojis naturally
- Vary the tone: informative, inspirational, and conversational
- DO NOT include hashtags (they will be added separately)
- Make them suitable for Instagram, Twitter/X, and LinkedIn

Format: Return only the captions, numbered 1-{num_captions}, one per line."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator who writes engaging, concise captions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            captions_text = response.choices[0].message.content
            print("✅ Captions generated successfully!\n")
            
            # Parse captions into a list
            captions = []
            for line in captions_text.strip().split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering
                    caption = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ')
                    captions.append(caption)
            
            return captions[:num_captions]
            
        except Exception as e:
            print(f"⚠️  Caption generation failed: {str(e)}")
            # Fallback captions
            return [
                f"🚀 Excited to share this about {topic}!",
                f"💡 Here's what you need to know about {topic}",
                f"✨ Check out this amazing content on {topic}"
            ]
    
    def generate_complete_post(self, topic, image_size="1024x1024", enhanced_image=False):
        """Generate complete social media post: image + hashtags + captions"""
        
        print("\n" + "="*70)
        print("🎨 SOCIAL MEDIA CONTENT GENERATOR")
        print("="*70)
        print(f"📌 Topic: {topic}")
        print(f"📐 Image Size: {image_size}")
        print(f"✨ Enhanced Mode: {'Yes' if enhanced_image else 'No'}")
        print("="*70)
        
        # Step 1: Detect genre
        genre = detect_genre(topic)
        print(f"\n🎯 Detected Genre: {genre.upper()}")
        
        # Step 2: Generate image with DALL-E
        print("\n" + "─"*70)
        print("STEP 1: Generating Image")
        print("─"*70)
        
        image_result = self.dalle_generator.generate_image(
            topic=topic,
            enhanced=enhanced_image,
            size=image_size,
            use_gpt4_refinement=True
        )
        
        if not image_result:
            print("❌ Image generation failed. Aborting...")
            return None
        
        # Step 3: Generate hashtags
        print("\n" + "─"*70)
        print("STEP 2: Generating Hashtags")
        print("─"*70)
        
        try:
            hashtags = get_10_existing_hashtags(topic)
        except Exception as e:
            print(f"⚠️  Hashtag generation failed: {str(e)}")
            print("Using fallback hashtags...")
            hashtags = [f"#{topic.lower().replace(' ', '')}", "#socialmedia", "#content"]
        
        # Step 4: Generate captions
        print("\n" + "─"*70)
        print("STEP 3: Generating Captions")
        print("─"*70)
        
        captions = self.generate_captions(topic, genre, num_captions=3)
        
        # Step 5: Compile and save results
        print("\n" + "="*70)
        print("✅ CONTENT GENERATION COMPLETE!")
        print("="*70)
        
        result = {
            'topic': topic,
            'genre': genre,
            'image_url': image_result['url'],
            'image_file': image_result['filename'],
            'hashtags': hashtags,
            'captions': captions,
            'revised_prompt': image_result.get('revised_prompt', '')
        }
        
        # Save to text file
        self.save_to_file(result)
        
        # Display results
        self.display_results(result)
        
        return result
    
    def save_to_file(self, result):
        """Save the complete post content to a text file"""
        # Try fixed path first, fallback to timestamped if file is locked
        filename = r"D:\Social_Agent\post.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                self._write_content_to_file(f, result)
            print(f"\n💾 Content saved to: {filename}")
            
        except PermissionError:
            # File is open in another program, use timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in result['topic'])
            safe_topic = safe_topic.replace(' ', '_')[:50]
            filename = f"post_{safe_topic}_{timestamp}.txt"
            
            print(f"\n⚠️  post.txt is currently open in another program")
            print(f"💾 Saving to alternative file: {filename}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                self._write_content_to_file(f, result)
            print(f"✅ Content saved successfully!")
    
    def _write_content_to_file(self, f, result):
        """Helper method to write content to file"""
        f.write("="*70 + "\n")
        f.write("SOCIAL MEDIA POST - COMPLETE PACKAGE\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"📌 TOPIC: {result['topic']}\n")
        f.write(f"🎯 GENRE: {result['genre']}\n")
        f.write(f"📅 GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("─"*70 + "\n")
        f.write("🖼️  IMAGE\n")
        f.write("─"*70 + "\n")
        f.write(f"File: {result['image_file']}\n")
        f.write(f"URL: {result['image_url']}\n\n")
        
        if result['revised_prompt']:
            f.write(f"DALL-E Revised Prompt:\n{result['revised_prompt']}\n\n")
        
        f.write("─"*70 + "\n")
        f.write("📝 CAPTIONS (Choose one)\n")
        f.write("─"*70 + "\n")
        for i, caption in enumerate(result['captions'], 1):
            f.write(f"\nCaption {i}:\n{caption}\n")
        
        f.write("\n" + "─"*70 + "\n")
        f.write("🏷️  HASHTAGS\n")
        f.write("─"*70 + "\n")
        f.write(" ".join(result['hashtags']) + "\n\n")
        
        f.write("─"*70 + "\n")
        f.write("📋 READY-TO-POST FORMAT\n")
        f.write("─"*70 + "\n")
        f.write(f"{result['captions'][0]}\n\n")
        f.write(" ".join(result['hashtags']) + "\n\n")
        
        f.write("="*70 + "\n")
    
    def display_results(self, result):
        """Display the generated content in a nice format"""
        print("\n" + "="*70)
        print("📦 YOUR COMPLETE SOCIAL MEDIA POST")
        print("="*70)
        
        print(f"\n🖼️  IMAGE:")
        print(f"   File: {result['image_file']}")
        print(f"   URL: {result['image_url']}")
        
        print(f"\n📝 CAPTIONS (Choose one):")
        for i, caption in enumerate(result['captions'], 1):
            print(f"\n   {i}. {caption}")
        
        print(f"\n🏷️  HASHTAGS:")
        print(f"   {' '.join(result['hashtags'])}")
        
        print("\n" + "─"*70)
        print("📋 READY-TO-POST FORMAT:")
        print("─"*70)
        print(f"\n{result['captions'][0]}\n")
        print(" ".join(result['hashtags']))
        print("\n" + "="*70)

def main():
    """Main function with interactive menu"""
    generator = SocialMediaContentGenerator()
    
    print("\n" + "="*70)
    print("🚀 SOCIAL MEDIA CONTENT GENERATOR")
    print("="*70)
    print("Generate: Image + Hashtags + Captions - All in One!")
    print("="*70)
    
    while True:
        print("\n📋 Options:")
        print("1. Generate complete post (Standard)")
        print("2. Generate complete post (Enhanced)")
        print("3. Generate with custom size")
        print("4. Exit")
        
        choice = input("\n👉 Enter your choice (1-4): ").strip()
        
        if choice == "1":
            topic = input("\n💡 Enter your topic: ").strip()
            if topic:
                generator.generate_complete_post(topic, image_size="1024x1024", enhanced_image=False)
            else:
                print("❌ Topic cannot be empty!")
        
        elif choice == "2":
            topic = input("\n💡 Enter your topic: ").strip()
            if topic:
                print("\n✨ Generating ENHANCED version (better quality, takes longer)...")
                generator.generate_complete_post(topic, image_size="1024x1024", enhanced_image=True)
            else:
                print("❌ Topic cannot be empty!")
        
        elif choice == "3":
            topic = input("\n💡 Enter your topic: ").strip()
            if topic:
                print("\n📐 Size options:")
                print("1. Square (1024x1024) - Instagram Posts")
                print("2. Wide (1792x1024) - Twitter/LinkedIn")
                print("3. Tall (1024x1792) - Instagram Stories")
                
                size_choice = input("\n👉 Choose size (1-3): ").strip()
                sizes = {
                    "1": "1024x1024",
                    "2": "1792x1024",
                    "3": "1024x1792"
                }
                size = sizes.get(size_choice, "1024x1024")
                
                print("\n✨ Quality:")
                print("1. Standard")
                print("2. Enhanced (better quality)")
                
                quality_choice = input("\n👉 Choose (1-2): ").strip()
                enhanced = quality_choice == "2"
                
                generator.generate_complete_post(topic, image_size=size, enhanced_image=enhanced)
            else:
                print("❌ Topic cannot be empty!")
        
        elif choice == "4":
            print("\n👋 Thank you for using Social Media Content Generator!")
            print("✨ All your content is saved in the current directory")
            break
        
        else:
            print("\n❌ Invalid choice! Please enter 1-4.")

if __name__ == "__main__":
    main()
