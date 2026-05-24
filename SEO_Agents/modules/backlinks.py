"""
AUTOMATED BACKLINK POSTING SYSTEM
Posts content to TOP 5 free platforms for backlinks with Telegram approval

Supported Platforms (TOP 4):
1. Dev.to (DA 90) - via API
2. GitHub Gists (DA 94) - via API
3. Hashnode (DA 85) - via API
4. Telegraph (DA 92) - via API (NO KEY NEEDED!)

Removed: Medium, Reddit, Blogger, WordPress, Tumblr, Quora
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List
import logging
from modules.utils import NumpyEncoder

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class BacklinkPoster:
    """Automated posting to TOP 5 backlink platforms"""
    
    def __init__(self):
        # API Keys (add to .env file)
        self.medium_token = os.getenv("MEDIUM_API_TOKEN", "")
        self.devto_token = os.getenv("DEVTO_API_KEY", "")
        self.hashnode_token = os.getenv("HASHNODE_API_KEY", "")
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        
        # Tumblr Credentials
        self.tumblr_consumer_key = os.getenv("TUMBLR_CONSUMER_KEY", "")
        self.tumblr_consumer_secret = os.getenv("TUMBLR_CONSUMER_SECRET", "")
        self.tumblr_oauth_token = os.getenv("TUMBLR_OAUTH_TOKEN", "")
        self.tumblr_oauth_secret = os.getenv("TUMBLR_OAUTH_SECRET", "")
        self.tumblr_blog_name = os.getenv("TUMBLR_BLOG_NAME", "decentrawood")
        
        # Platform endpoints
        self.endpoints = {
            "medium": "https://api.medium.com/v1",
            "devto": "https://dev.to/api",
            "hashnode": "https://api.hashnode.com",
            "telegraph": "https://api.telegra.ph"
        }
        
        # Posting history (Stored in reports directory)
        self.history_file = os.path.join("reports", "backlink_posts_history.json")
        self.load_history()
    
    def load_history(self):
        """Load posting history"""
        try:
            # Ensure reports directory exists
            os.makedirs("reports", exist_ok=True)
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except:
            self.history = []
    
    def save_history(self):
        """Save posting history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2, cls=NumpyEncoder)
    
    # ========================================================================
    # MEDIUM.COM POSTING
    # ========================================================================
    
    def post_to_medium(self, title: str, content: str, tags: List[str], 
                       canonical_url: str = None, publish_status: str = "draft") -> Dict:
        """
        Post article to Medium
        
        Setup:
        1. Go to https://medium.com/me/settings
        2. Scroll to "Integration tokens"
        3. Create new token
        4. Add to .env: MEDIUM_API_TOKEN=your_token
        
        Args:
            publish_status: "public" for published, "draft" for draft (default: "draft")
        """
        if not self.medium_token:
            return {"success": False, "error": "Medium API token not configured", "platform": "Medium"}
        
        try:
            # Get user ID
            headers = {
                "Authorization": f"Bearer {self.medium_token}",
                "Content-Type": "application/json"
            }
            
            user_response = requests.get(
                f"{self.endpoints['medium']}/me",
                headers=headers
            )
            user_id = user_response.json()["data"]["id"]
            
            # Create post
            post_data = {
                "title": title,
                "contentFormat": "markdown",
                "content": content,
                "tags": tags[:5],  # Max 5 tags
                "publishStatus": publish_status,  # "public" or "draft"
                "canonicalUrl": canonical_url
            }
            
            response = requests.post(
                f"{self.endpoints['medium']}/users/{user_id}/posts",
                headers=headers,
                json=post_data
            )
            
            result = response.json()
            
            if response.status_code == 201:
                post_url = result["data"]["url"]
                status = "published" if publish_status == "public" else "draft"
                logger.info(f"✅ Posted to Medium: {post_url} ({status})")
                
                # Save to history
                self.history.append({
                    "platform": "medium",
                    "title": title,
                    "url": post_url,
                    "canonical_url": canonical_url,
                    "timestamp": datetime.now().isoformat(),
                    "status": status
                })
                self.save_history()
                
                return {
                    "success": True,
                    "platform": "Medium",
                    "url": post_url,
                    "status": status
                }
            else:
                err_msg = result.get("errors", [{}])[0].get("message", "") if isinstance(result, dict) else ""
                return {"success": False, "error": err_msg or f"HTTP {response.status_code}: {str(result)[:200]}", "platform": "Medium"}
        
        except Exception as e:
            logger.error(f"Medium posting error: {e}")
            return {"success": False, "error": str(e), "platform": "Medium"}
    
    # ========================================================================
    # DEV.TO POSTING
    # ========================================================================
    
    def post_to_devto(self, title: str, content: str, tags: List[str],
                      canonical_url: str = None, published: bool = False) -> Dict:
        """
        Post article to Dev.to
        
        Setup:
        1. Go to https://dev.to/settings/extensions
        2. Generate API key
        3. Add to .env: DEVTO_API_KEY=your_key
        
        Args:
            published: True for published, False for draft (default: False)
        """
        if not self.devto_token:
            return {"success": False, "error": "Dev.to API key not configured", "platform": "Dev.to"}
        
        try:
            headers = {
                "api-key": self.devto_token,
                "Content-Type": "application/json"
            }
            
            # Dev.to requires tags to be lowercase, letters/digits/underscores only, no spaces
            import re as _re
            clean_tags = [
                _re.sub(r'[^a-z0-9]', '', t.lower().replace(' ', ''))[:20]
                for t in tags
            ]
            clean_tags = [t for t in clean_tags if t][:4]  # Max 4 non-empty tags

            post_data = {
                "article": {
                    "title": title,
                    "body_markdown": content,
                    "published": published,  # True or False
                    "tags": clean_tags
                    # Note: canonical_url removed to avoid "already taken" errors
                }
            }
            
            response = requests.post(
                f"{self.endpoints['devto']}/articles",
                headers=headers,
                json=post_data
            )
            
            result = response.json()
            
            if response.status_code == 201:
                post_url = result["url"]
                status = "published" if published else "draft"
                logger.info(f"✅ Posted to Dev.to: {post_url} ({status})")
                
                self.history.append({
                    "platform": "devto",
                    "title": title,
                    "url": post_url,
                    "canonical_url": canonical_url,
                    "timestamp": datetime.now().isoformat(),
                    "status": status
                })
                self.save_history()
                
                return {
                    "success": True,
                    "platform": "Dev.to",
                    "url": post_url,
                    "status": status
                }
            else:
                err_msg = ""
                if isinstance(result, dict):
                    err_msg = result.get("error", "") or result.get("message", "") or str(result)[:300]
                return {"success": False, "error": err_msg or f"HTTP {response.status_code}", "platform": "Dev.to"}
        
        except Exception as e:
            logger.error(f"Dev.to posting error: {e}")
            return {"success": False, "error": str(e), "platform": "Dev.to"}
    
    # ========================================================================
    # HASHNODE POSTING
    # ========================================================================
    
    def post_to_hashnode(self, title: str, content: str, tags: List[str],
                         canonical_url: str = None) -> Dict:
        """
        Post article to Hashnode
        
        Setup:
        1. Go to https://hashnode.com/settings/developer
        2. Generate Personal Access Token
        3. Add to .env: HASHNODE_API_KEY=your_token
        
        Note: Automatically fetches your publication ID
        """
        if not self.hashnode_token:
            return {"success": False, "error": "Hashnode API key not configured", "platform": "Hashnode"}
        
        try:
            headers = {
                "Authorization": self.hashnode_token,
                "Content-Type": "application/json"
            }
            
            # Step 1: Get user's publication ID
            user_query = """
            query Me {
                me {
                    publications(first: 1) {
                        edges {
                            node {
                                id
                                title
                            }
                        }
                    }
                }
            }
            """
            
            user_response = requests.post(
                "https://gql.hashnode.com/",
                headers=headers,
                json={"query": user_query},
                timeout=30
            )
            
            user_result = user_response.json()
            
            # Extract publication ID
            if "errors" in user_result:
                error_msg = user_result["errors"][0].get("message", "Unknown error")
                return {"success": False, "error": f"Hashnode API: {error_msg}", "platform": "Hashnode"}
            
            try:
                publication_id = user_result["data"]["me"]["publications"]["edges"][0]["node"]["id"]
            except (KeyError, IndexError):
                return {
                    "success": False, 
                    "error": "No Hashnode blog found. To use Hashnode:\n1. Go to hashnode.com\n2. Click 'Start blogging'\n3. Create your blog (takes 2 min)\n\nOr skip Hashnode and use other platforms!", 
                    "platform": "Hashnode",
                    "skippable": True
                }
            
            # Step 2: Publish the post with publication ID
            mutation = """
            mutation PublishPost($input: PublishPostInput!) {
                publishPost(input: $input) {
                    post {
                        id
                        title
                        slug
                        url
                    }
                }
            }
            """
            
            # Prepare tags (Hashnode uses tag IDs or slugs)
            tag_slugs = [tag.lower().replace(" ", "-") for tag in tags[:5]]
            
            variables = {
                "input": {
                    "title": title,
                    "contentMarkdown": content,
                    "tags": [{"slug": tag, "name": tag.replace("-", " ").title()} for tag in tag_slugs],
                    "publicationId": publication_id  # Now we have it!
                }
            }
            
            # Use correct Hashnode GraphQL endpoint
            response = requests.post(
                "https://gql.hashnode.com/",  # Correct endpoint
                headers=headers,
                json={"query": mutation, "variables": variables},
                timeout=30
            )
            
            result = response.json()
            
            # Check for errors
            if "errors" in result:
                error_msg = result["errors"][0].get("message", "Unknown error")
                logger.error(f"Hashnode API error: {error_msg}")
                return {"success": False, "error": f"Hashnode API: {error_msg}", "platform": "Hashnode"}
            
            if "data" in result and result["data"] and "publishPost" in result["data"]:
                post_data = result["data"]["publishPost"]["post"]
                post_url = post_data["url"]
                logger.info(f"✅ Posted to Hashnode: {post_url}")
                
                self.history.append({
                    "platform": "hashnode",
                    "title": title,
                    "url": post_url,
                    "canonical_url": canonical_url,
                    "timestamp": datetime.now().isoformat(),
                    "status": "published"
                })
                self.save_history()
                
                return {
                    "success": True,
                    "platform": "Hashnode",
                    "url": post_url,
                    "status": "published"
                }
            else:
                return {"success": False, "error": f"Unexpected response: {result}", "platform": "Hashnode"}
        
        except requests.exceptions.Timeout:
            logger.error("Hashnode API timeout")
            return {"success": False, "error": "Connection timeout - try again", "platform": "Hashnode"}
        except Exception as e:
            logger.error(f"Hashnode posting error: {e}")
            return {"success": False, "error": str(e), "platform": "Hashnode"}
    
    # ========================================================================
    # GITHUB GIST POSTING
    # ========================================================================
    
    def post_to_github_gist(self, title: str, content: str, 
                            description: str = "") -> Dict:
        """
        Create GitHub Gist (great for code snippets and technical content)
        
        Setup:
        1. Go to https://github.com/settings/tokens
        2. Generate new token with 'gist' scope
        3. Add to .env: GITHUB_TOKEN=your_token
        """
        if not self.github_token:
            return {"success": False, "error": "GitHub token not configured"}
        
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            gist_data = {
                "description": description or title,
                "public": True,
                "files": {
                    f"{title.replace(' ', '_')}.md": {
                        "content": content
                    }
                }
            }
            
            response = requests.post(
                "https://api.github.com/gists",
                headers=headers,
                json=gist_data
            )
            
            result = response.json()
            
            if response.status_code == 201:
                gist_url = result["html_url"]
                logger.info(f"✅ Created GitHub Gist: {gist_url}")
                
                self.history.append({
                    "platform": "github_gist",
                    "title": title,
                    "url": gist_url,
                    "timestamp": datetime.now().isoformat(),
                    "status": "published"
                })
                self.save_history()
                
                return {
                    "success": True,
                    "platform": "GitHub Gist",
                    "url": gist_url,
                    "status": "published"
                }
            else:
                err_msg = result.get("message", str(result)[:200]) if isinstance(result, dict) else str(result)[:200]
                return {"success": False, "error": err_msg}
        
        except Exception as e:
            logger.error(f"GitHub Gist error: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # CONTENT GENERATION (DECENTRAWOOD-SPECIFIC)
    # ========================================================================
    
    def generate_article_from_brief(self, brief: Dict, website_url: str) -> Dict:
        """
        Generate article content from content brief
        
        NOW USES DECENTRAWOOD-SPECIFIC TEMPLATES
        - Platform-optimized formatting
        - Varied content (never duplicate)
        - Proper link placement
        - Canonical URLs
        """
        
        try:
            from .contents import DecentrawoodContentGenerator
            
            # Use Decentrawood-specific generator
            generator = DecentrawoodContentGenerator()
            
            # Generate content for Medium by default (will be adapted per platform)
            article_data = generator.generate_medium_article()
            
            return article_data
            
        except ImportError:
            # Fallback to generic generation if decentrawood_content_generator not available
            keyword = brief.get("primary_keyword", "")
            secondary_keywords = brief.get("secondary_keywords", [])
            headings = brief.get("heading_structure", [])
            
            # Create markdown article
            article = f"""# {brief.get('meta_title', keyword.title())}

{brief.get('meta_description', '')}

"""
            
            # Add introduction
            article += f"""## Introduction

In this comprehensive guide, we'll explore everything you need to know about {keyword}. Whether you're just getting started or looking to deepen your understanding, this article covers all the essential aspects.

"""
            
            # Add main content sections
            for heading in headings[1:]:  # Skip H1
                if heading.startswith("H2:"):
                    section_title = heading.replace("H2: ", "")
                    article += f"""## {section_title}

[Content about {section_title.lower()}. This section provides detailed information and practical insights.]

"""
                elif heading.startswith("H3:"):
                    subsection_title = heading.replace("H3: ", "")
                    article += f"""### {subsection_title}

[Detailed explanation of {subsection_title.lower()}.]

"""
            
            # Add related keywords section
            if secondary_keywords:
                article += f"""## Related Topics

You might also be interested in:
"""
                for kw in secondary_keywords[:5]:
                    article += f"- {kw}\n"
                article += "\n"
            
            # Add backlink to your website
            article += f"""## Learn More

For more information and resources, visit [{website_url}]({website_url}).

"""
            
            # Add footer
            article += f"""---

*Originally published at [{website_url}]({website_url})*
"""
            
            # Extract tags from keywords
            tags = [keyword] + secondary_keywords[:4]
            tags = [tag.replace(" ", "").lower() for tag in tags]
            
            return {
                "title": brief.get('meta_title', keyword.title()),
                "content": article,
                "tags": tags,
                "canonical_url": f"{website_url}{brief.get('target_url', '/')}"
            }
    
    def generate_platform_specific_content(self, platform: str) -> Dict:
        """
        Generate platform-specific content for Decentrawood
        
        Each platform gets optimized content:
        - Medium: Long-form, professional
        - Dev.to: Tech-focused
        - Hashnode: Web3 tone
        - GitHub: Technical with code
        - Telegraph: Clean, minimal
        """
        
        try:
            from decentrawood_content_generator import DecentrawoodContentGenerator
            
            generator = DecentrawoodContentGenerator()
            return generator.generate_for_platform(platform)
            
        except ImportError:
            # Fallback
            return {
                "title": "Decentrawood: AI-Powered Social Metaverse",
                "content": "Learn more at https://decentrawood.com",
                "tags": ["ai", "web3", "metaverse"]
            }
    
    # ========================================================================
    # TELEGRAPH POSTING (NO API KEY NEEDED!)
    # ========================================================================
    
    def post_to_telegraph(self, title: str, content: str, 
                          author_name: str = "SEO Bot") -> Dict:
        """
        Post article to Telegraph (Telegram's publishing platform)
        
        Setup:
        NO SETUP NEEDED! Telegraph API is public and free.
        """
        try:
            import time
            
            # Retry logic for Telegraph (can be slow sometimes)
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Step 1: Create account (or use existing)
                    account_response = requests.post(
                        f"{self.endpoints['telegraph']}/createAccount",
                        json={
                            "short_name": author_name,
                            "author_name": author_name
                        },
                        timeout=15  # 15 second timeout
                    )
                    
                    if account_response.status_code != 200:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        return {"success": False, "error": "Failed to create Telegraph account", "platform": "Telegraph"}
                    
                    access_token = account_response.json()["result"]["access_token"]
                    
                    # Step 2: Convert markdown to Telegraph HTML format
                    # Telegraph uses a simple HTML-like format
                    html_content = content.replace("# ", "<h3>").replace("## ", "<h4>")
                    html_content = html_content.replace("\n\n", "</p><p>")
                    html_content = f"<p>{html_content}</p>"
                    
                    # Step 3: Create page
                    page_data = {
                        "access_token": access_token,
                        "title": title,
                        "author_name": author_name,
                        "content": [{"tag": "p", "children": [html_content]}],
                        "return_content": False
                    }
                    
                    page_response = requests.post(
                        f"{self.endpoints['telegraph']}/createPage",
                        json=page_data,
                        timeout=15  # 15 second timeout
                    )
                    
                    result = page_response.json()
                    
                    if page_response.status_code == 200 and "result" in result:
                        page_url = f"https://telegra.ph/{result['result']['path']}"
                        logger.info(f"✅ Posted to Telegraph: {page_url}")
                        
                        self.history.append({
                            "platform": "telegraph",
                            "title": title,
                            "url": page_url,
                            "timestamp": datetime.now().isoformat(),
                            "status": "published"
                        })
                        self.save_history()
                        
                        return {
                            "success": True,
                            "platform": "Telegraph",
                            "url": page_url,
                            "status": "published"
                        }
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        err_msg = result.get("error", str(result)[:200]) if isinstance(result, dict) else str(result)[:200]
                        return {"success": False, "error": err_msg, "platform": "Telegraph"}
                
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        logger.warning(f"Telegraph timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error("Telegraph API timeout after retries")
                        return {"success": False, "error": "Connection timeout - Telegraph may be slow, try again later", "platform": "Telegraph"}
                
                except requests.exceptions.ConnectionError:
                    if attempt < max_retries - 1:
                        logger.warning(f"Telegraph connection error, retrying... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error("Telegraph connection error after retries")
                        return {"success": False, "error": "Connection failed - check internet connection", "platform": "Telegraph"}
            
            return {"success": False, "error": "Max retries exceeded", "platform": "Telegraph"}
        
        except Exception as e:
            logger.error(f"Telegraph posting error: {e}")
            return {"success": False, "error": str(e), "platform": "Telegraph"}

    # ========================================================================
    # TUMBLR POSTING
    # ========================================================================
    
    def post_to_tumblr(self, title: str, content: str, tags: List[str]) -> Dict:
        """
        Post article to Tumblr
        
        Setup:
        1. Go to https://www.tumblr.com/settings/apps
        2. Register an application
        3. Get Consumer Key and Secret
        4. Use an OAuth tool to get Token and Token Secret
        5. Add all 4 keys to .env
        """
        if not all([self.tumblr_consumer_key, self.tumblr_consumer_secret, 
                   self.tumblr_oauth_token, self.tumblr_oauth_secret]):
            return {
                "success": False, 
                "error": "Tumblr API keys partially or fully missing in .env", 
                "platform": "Tumblr"
            }
            
        try:
            import pytumblr
            
            client = pytumblr.TumblrRestClient(
                self.tumblr_consumer_key,
                self.tumblr_consumer_secret,
                self.tumblr_oauth_token,
                self.tumblr_oauth_secret
            )
            
            # Create a text post
            response = client.create_text(
                self.tumblr_blog_name,
                state="published",
                slug=title.lower().replace(" ", "-"),
                title=title,
                body=content,
                tags=tags[:10]  # Tumblr handles tags well
            )
            
            if "id" in response:
                post_id = response["id"]
                post_url = f"https://{self.tumblr_blog_name}.tumblr.com/post/{post_id}"
                logger.info(f"✅ Posted to Tumblr: {post_url}")
                
                self.save_to_history("tumblr", title, post_url)
                
                return {
                    "success": True,
                    "platform": "Tumblr",
                    "url": post_url,
                    "status": "published"
                }
            else:
                return {"success": False, "error": response, "platform": "Tumblr"}
                
        except ImportError:
            return {"success": False, "error": "pytumblr library not installed", "platform": "Tumblr"}
        except Exception as e:
            logger.error(f"Tumblr posting error: {e}")
            return {"success": False, "error": str(e), "platform": "Tumblr"}

    def save_to_history(self, platform: str, title: str, url: str, canonical_url: str = None, status: str = "published"):
        """Utility to save post to history"""
        self.history.append({
            "platform": platform,
            "title": title,
            "url": url,
            "canonical_url": canonical_url,
            "timestamp": datetime.now().isoformat(),
            "status": status
        })
        self.save_history()

    # ========================================================================
    # BATCH POSTING
    # ========================================================================
    
    def post_to_multiple_platforms(self, article_data: Dict, 
                                   platforms: List[str] = None) -> List[Dict]:
        """Post to multiple platforms at once (TOP 3 platforms)"""
        
        if platforms is None:
            # Default: TOP 3 platforms
            platforms = ["devto", "hashnode", "tumblr"]
        
        results = []
        
        for platform in platforms:
            if platform == "medium":
                result = self.post_to_medium(
                    title=article_data["title"],
                    content=article_data["content"],
                    tags=article_data["tags"],
                    canonical_url=article_data.get("canonical_url")
                )
            elif platform == "devto":
                result = self.post_to_devto(
                    title=article_data["title"],
                    content=article_data["content"],
                    tags=article_data["tags"],
                    canonical_url=article_data.get("canonical_url")
                )
            elif platform == "hashnode":
                result = self.post_to_hashnode(
                    title=article_data["title"],
                    content=article_data["content"],
                    tags=article_data["tags"],
                    canonical_url=article_data.get("canonical_url")
                )
            elif platform == "tumblr":
                result = self.post_to_tumblr(
                    title=article_data["title"],
                    content=article_data["content"],
                    tags=article_data["tags"]
                )
            elif platform == "github_gist":
                result = self.post_to_github_gist(
                    title=article_data["title"],
                    content=article_data["content"],
                    description=article_data.get("canonical_url", "")
                )
            elif platform == "telegraph":
                result = self.post_to_telegraph(
                    title=article_data["title"],
                    content=article_data["content"]
                )
            else:
                result = {"success": False, "error": f"Unknown platform: {platform}"}
            
            results.append(result)
        
        return results
    
    def get_posting_summary(self) -> Dict:
        """Get summary of all posts"""
        total_posts = len(self.history)
        platforms = {}
        
        for post in self.history:
            platform = post["platform"]
            platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            "total_posts": total_posts,
            "platforms": platforms,
            "recent_posts": self.history[-10:] if self.history else []
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    poster = BacklinkPoster()
    
    # Example: Post to Medium
    article = {
        "title": "Complete Guide to Web3 Content Platforms",
        "content": """# Complete Guide to Web3 Content Platforms

Web3 is revolutionizing content creation...

## What is Web3?

[Content here]

## Benefits

[Content here]

---

*Learn more at https://decentrawood.com*
""",
        "tags": ["web3", "blockchain", "content", "decentralized"],
        "canonical_url": "https://decentrawood.com/guides/web3-platforms"
    }
    
    # Post to multiple platforms
    results = poster.post_to_multiple_platforms(article, ["medium", "devto"])
    
    for result in results:
        if result["success"]:
            print(f"✅ Posted to {result['platform']}: {result['url']}")
        else:
            print(f"❌ Failed to post to platform: {result['error']}")
