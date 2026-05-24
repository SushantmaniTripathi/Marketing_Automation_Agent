#!/usr/bin/env python3


import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Import configuration
import config_post as config

# Import the content generator and Instagram poster
from social_media_generator import SocialMediaContentGenerator
from instagram_auto_poster import InstagramAutoPoster

# Load environment variables
load_dotenv()


class AutomatedInstagramPoster:
    """Fully automated Instagram posting system - backend only"""
    
    def __init__(self):
        """Initialize the automated poster"""
        self.generator = SocialMediaContentGenerator()
        self.poster = None
        
    def log(self, message, level="INFO"):
        """Print timestamped log messages to terminal"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "PROCESS": "⚙️",
            "WAIT": "⏳"
        }.get(level, "•")
        
        # Clean the message to avoid encoding issues
        try:
            clean_message = str(message).encode('utf-8', errors='ignore').decode('utf-8')
            output = f"[{timestamp}] {prefix} {clean_message}"
            print(output, flush=True)
        except Exception as e:
            # Fallback to simple ASCII output
            simple_message = str(message).encode('ascii', errors='ignore').decode('ascii')
            print(f"[{timestamp}] {level}: {simple_message}", flush=True)
    
    def generate_content(self, topic):
        """
        Generate complete content package
        Returns: dict with image_file, captions, hashtags, etc.
        """
        self.log(f"Starting content generation for topic: '{topic}'", "PROCESS")
        quality_text = "ENHANCED (HD)" if config.IMAGE_QUALITY_ENHANCED else "STANDARD"
        self.log(f"Quality: {quality_text} | Size: {config.IMAGE_SIZE}", "INFO")
        
        try:
            # Generate content with configured settings
            result = self.generator.generate_complete_post(
                topic=topic,
                image_size=config.IMAGE_SIZE,
                enhanced_image=config.IMAGE_QUALITY_ENHANCED
            )
            
            if not result:
                self.log("Content generation failed!", "ERROR")
                return None
            
            self.log("Content generation completed successfully!", "SUCCESS")
            self.log(f"Image saved: {result['image_file']}", "INFO")
            self.log(f"Generated {len(result['captions'])} captions", "INFO")
            self.log(f"Generated {len(result['hashtags'])} hashtags", "INFO")
            
            return result
            
        except Exception as e:
            self.log(f"Content generation error: {str(e)}", "ERROR")
            return None
    
    def post_to_instagram(self, content):
        """
        Post content to Instagram automatically
        All browser interactions happen in background
        """
        self.log("Initializing Instagram posting process...", "PROCESS")
        
        try:
            # Initialize Instagram poster
            self.poster = InstagramAutoPoster()
            
            # Setup browser (headless mode for background operation)
            self.log("Setting up browser driver...", "PROCESS")
            if not self.poster.setup_driver():
                self.log("Browser setup failed!", "ERROR")
                return False
            
            self.log("Browser driver ready", "SUCCESS")
            
            # Use configured caption index
            caption_index = min(config.SELECTED_CAPTION_INDEX, len(content['captions']) - 1)
            selected_caption = content['captions'][caption_index]
            
            # Limit hashtags to configured maximum
            hashtags = content['hashtags'][:config.MAX_HASHTAGS]
            
            self.log("Starting Instagram posting...", "PROCESS")
            self.log(f"Posting to {len(self.poster.accounts)} account(s)", "INFO")
            self.log(f"Using caption #{caption_index + 1}", "INFO")
            self.log(f"Using {len(hashtags)} hashtags", "INFO")
            
            # Post to all configured accounts
            results = self.poster.post_to_all_accounts(
                image_path=content['image_file'],
                caption=selected_caption,
                hashtags=hashtags,
                topic=content['topic']
            )
            
            # Report results
            successful = sum(1 for r in results if r['success'])
            
            if successful == len(results):
                self.log(f"Posted successfully to all {len(results)} account(s)!", "SUCCESS")
            elif successful > 0:
                self.log(f"Posted to {successful}/{len(results)} account(s)", "SUCCESS")
            else:
                self.log("Failed to post to any accounts", "ERROR")
            
            # Detailed results
            for r in results:
                status = "SUCCESS" if r['success'] else "ERROR"
                self.log(f"Account '{r['account']}': {'Posted' if r['success'] else 'Failed'}", status)
            
            return successful > 0
            
        except Exception as e:
            self.log(f"Instagram posting error: {str(e)}", "ERROR")
            return False
        
        finally:
            # Cleanup browser
            if self.poster:
                self.log("Cleaning up browser resources...", "PROCESS")
                self.poster.cleanup()
                self.log("Cleanup complete", "SUCCESS")
    
    def run(self, topic):
        """
        Main execution flow with review and regeneration
        1. Generate content
        2. User reviews content
        3. User approves or regenerates
        4. Post to Instagram
        5. Report completion
        """
        print("\n" + "="*70)
        self.log("AUTOMATED INSTAGRAM POSTING SYSTEM", "INFO")
        print("="*70)
        self.log(f"Topic: {topic}", "INFO")
        print("="*70 + "\n")
        
        start_time = time.time()
        content = None
        regeneration_count = 0
        max_regenerations = 5  # Prevent infinite loops
        
        # Loop until user approves or max regenerations reached
        while regeneration_count <= max_regenerations:
            # Step 1: Generate content
            if regeneration_count == 0:
                print("\n" + "-"*70)
                self.log("STEP 1/3: Content Generation", "PROCESS")
                print("-"*70)
            else:
                print("\n" + "-"*70)
                self.log(f"REGENERATING (Attempt {regeneration_count + 1})...", "PROCESS")
                self.log("Using more advanced and refined prompt...", "INFO")
                print("-"*70)
            
            content = self.generate_content(topic)
            
            if not content:
                self.log("Process aborted due to content generation failure", "ERROR")
                return False
            
            # Step 2: User review and approval
            print("\n" + "="*70)
            self.log("STEP 2/3: Review Generated Content", "PROCESS")
            print("="*70)
            print(f"\n📄 Content saved to: D:\\Social_Agent\\post.txt")
            print(f"📸 Image saved to: {content['image_file']}")
            print("\n💡 Please review the generated content:")
            print("   • Open post.txt to see captions and hashtags")
            print("   • Open the image file to preview the image")
            print("\n⏸️  Take your time to review...\n")
            
            # Ask for approval
            while True:
                approval = input("👉 Do you approve this content? (yes/no): ").strip().lower()
                
                if approval in ['yes', 'y']:
                    self.log("Content approved! Proceeding to posting...", "SUCCESS")
                    break
                elif approval in ['no', 'n']:
                    regeneration_count += 1
                    if regeneration_count > max_regenerations:
                        print(f"\n⚠️  Maximum regeneration attempts ({max_regenerations}) reached.")
                        final_choice = input("👉 Post current content anyway? (yes/no): ").strip().lower()
                        if final_choice in ['yes', 'y']:
                            self.log("Proceeding with current content...", "INFO")
                            break
                        else:
                            self.log("Process cancelled by user", "ERROR")
                            return False
                    else:
                        print(f"\n🔄 Regenerating content with improved prompt...")
                        print(f"   (Attempt {regeneration_count + 1}/{max_regenerations + 1})")
                        break
                else:
                    print("❌ Invalid input. Please enter 'yes' or 'no'")
            
            # If approved, break the regeneration loop
            if approval in ['yes', 'y']:
                break
        
        # Step 3: Post to Instagram
        print("\n" + "="*70)
        self.log("STEP 3/3: Instagram Posting", "PROCESS")
        print("="*70 + "\n")
        success = self.post_to_instagram(content)
        
        # Final summary
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        print("\n" + "="*70)
        if success:
            self.log("PROCESS COMPLETED SUCCESSFULLY!", "SUCCESS")
        else:
            self.log("PROCESS COMPLETED WITH ERRORS", "ERROR")
        
        print("-"*70)
        self.log(f"Total time: {minutes}m {seconds}s", "INFO")
        self.log(f"Regenerations: {regeneration_count}", "INFO")
        self.log(f"Image file: {content['image_file']}", "INFO")
        self.log(f"Details saved: D:\\Social_Agent\\post.txt", "INFO")
        print("="*70 + "\n")
        
        return success


def main():
    """Main entry point - command line interface"""
    print("\n" + "="*70)
    print("🤖 INSTAGRAM AUTO-POSTER - BACKEND MODE")
    print("="*70)
    print("All processes run automatically in the background")
    quality_text = "ENHANCED (HD)" if config.IMAGE_QUALITY_ENHANCED else "STANDARD"
    print(f"Quality: {quality_text}")
    print(f"Format: {config.IMAGE_SIZE}")
    print(f"Headless Mode: {'ON' if config.HEADLESS_MODE else 'OFF'}")
    print("="*70)
    
    # Get topic from user
    topic = input("\n💡 Enter topic for Instagram post: ").strip()
    
    if not topic:
        print("❌ Topic cannot be empty!")
        return
    
    # Show configuration
    print(f"\n📌 Topic: {topic}")
    print(f"⚙️  Quality: {quality_text}")
    print(f"📐 Size: {config.IMAGE_SIZE}")
    print(f"🏷️  Max Hashtags: {config.MAX_HASHTAGS}")
    
    # Check if auto-post is enabled
    if not config.AUTO_POST_WITHOUT_CONFIRMATION:
        print("\nWorkflow:")
        print("  1. Generate image + captions + hashtags")
        print("  2. You review the content (post.txt)")
        print("  3. You confirm to proceed")
        print("  4. Automatically post to Instagram")
        
        confirm = input("\n👉 Start content generation? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("❌ Process cancelled")
            return
    else:
        print("\n⚡ AUTO-POST MODE: Starting immediately (no confirmation)")
    
    print("\n" + "="*70)
    print("🚀 STARTING AUTOMATED PROCESS...")
    print("="*70)
    print("Workflow:")
    print("  1. Generate content (image + captions + hashtags)")
    print("  2. Save to post.txt for your review")
    print("  3. Wait for your confirmation")
    print("  4. Post to Instagram automatically")
    print("="*70 + "\n")
    
    # Run the automated process
    poster = AutomatedInstagramPoster()
    success = poster.run(topic)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
