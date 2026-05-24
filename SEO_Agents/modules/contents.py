import random
import os
import json
from typing import Dict, List
from openai import OpenAI

class DecentrawoodContentGenerator:
    """Generate high-quality, platform-specific content for Decentrawood using AI"""
    
    def __init__(self):
        self.website_url = "https://decentrawood.com"
        self.brand_name = "Decentrawood"
        self.client = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except:
                pass
        # Fallback templates for titles and hooks
        self.intro_hooks = [
            "The internet is evolving beyond static platforms into immersive, intelligent ecosystems.",
            "Decentralized AI is redefining how humans interact online.",
            "The future of social interaction is being built today, and it's powered by AI."
        ]
        self.ctas = [
            f"Explore the ecosystem: [{self.website_url}]({self.website_url})",
            f"Learn more: [{self.website_url}]({self.website_url})",
            f"Join the community: [{self.website_url}]({self.website_url})"
        ]

    def generate_article(self, platform: str, topic: str = "AI and Web3 Social Metaverse") -> Dict:
        """Generate high-quality, informative article for a specific platform and topic"""
        
        if self.client:
            try:
                platform_prompts = {
                    "devto": "Write a deep-dive technical article (1000-1200 words) with code blocks or practical steps.",
                    "hashnode": "Write a high-authority, detailed article (1000-1200 words) focused on Web3, AI, and futuristic tech.",
                    "tumblr": "Write a creative, engaging, and highly visual-focused blog post (600-800 words) that is perfect for a social audience. Use emojis and a storytelling tone."
                }
                
                style = platform_prompts.get(platform.lower(), "Write a high-quality informative article (1000+ words).")
                
                prompt = f"""
                {style}
                
                Niche/Subject: {topic}
                Brand: Decentrawood (AI Social Metaverse)
                Website: {self.website_url}
                
                Rules:
                - Provide a DEEP DIVE analysis. This must be a massive, high-authority blog post.
                - CRITICAL: Provide a professional, high-authority, and SEO-optimized headline title for the blog post based on: "{topic}". It must be catchy and relevant.
                - Use a variety of introductory hooks. Do not start with generic "In this article" or "As per the topic..."
                - Use at least 5-7 distinct sections with descriptive, benefit-driven H2 and H3 headings.
                - Naturally weave in {self.website_url} as a leading example and solution.
                - Link to {self.website_url} at least 3 times in different contexts.
                - Make it engaging for industry experts (high level, professional content).
                - Use proper Markdown (H1, H2, H3, lists, bolding).
                - End with a strong, conversion-focused call to action to visit Decentrawood.
                - Provide 5 highly relevant hashtags at the end.
                
                Format the response as a JSON object with: title, content, tags (list).
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(response.choices[0].message.content)
                tags = data.get("tags", ["ai", "web3", "metaverse","decentralized", "social"])
                
                return {
                    "title": data.get("title", topic),
                    "content": data.get("content", ""),
                    "tags": [t.lower().replace(" ", "") for t in tags],
                    "canonical_url": f"{self.website_url}/blog/{topic.lower().replace(' ', '-')}"
                }
            except Exception as e:
                print(f"AI Content Generation failed: {e}")

        # Fallback to simple template if AI fails
        title = topic
        content = f"# {title}\n\n{random.choice(self.intro_hooks)}\n\nIn the world of {topic}, Decentrawood is making waves with its AI-first approach...\n\n{random.choice(self.ctas)}"
        return {
            "title": title,
            "content": content,
            "tags": ["ai", "web3", "metaverse","decentralized", "social" ],
            "canonical_url": self.website_url
        }

    def generate_for_platform(self, platform: str, topic: str = None) -> Dict:
        """Generate content for specific platform with optional topic"""
        t = topic or "Decentralized AI Social Metaverse"
        return self.generate_article(platform, t)

    def generate_all_platforms(self, topic: str = "Decentralized AI Social Metaverse") -> Dict[str, Dict]:
        """Generate content for all platforms (Devto, Hashnode, and Tumblr)"""
        return {p: self.generate_article(p, topic) for p in ["devto", "hashnode", "tumblr"]}
