import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.core import ContentGenerator, ImageGenerator
from app.models import BlogPost, ContentMetadata, ContentTone, SEOScore

def main():
    # 1. Load credentials from environment (with generic placeholders as fallback)
    wp_url = os.getenv("WP_URL", "https://yourwordpresssite.com").rstrip('/')
    username = os.getenv("WP_USERNAME", "admin")
    app_password = os.getenv("WP_APP_PASSWORD", "xxxx xxxx xxxx xxxx xxxx")
    auth = HTTPBasicAuth(username, app_password)
    
    print("=== WordPress AI Content System (Example Run) ===")
    
    # 2. Setup Image Generator (Optional)
    print("Initializing Image Generator...")
    img_gen = ImageGenerator()
    img_prompt = "A high-fidelity minimalist 3D rendering of an abstract AI neural node network, corporate technology concept art."
    
    try:
      # Attempt image generation using default model (Flux Schnell)
      image_result = img_gen.generate_image(prompt=img_prompt, image_size="landscape_4_3")
      print(f"Generated Image URL: {image_result.url}")
    except Exception as e:
      print(f"Image generation skipped/failed: {e}")
      
    # 3. Setup Content Generator
    print("Initializing Content Generator Facade...")
    generator = ContentGenerator()
    
    title = "The Evolution of Autonomous Agents in Web3"
    slug = "evolution-autonomous-agents-web3"
    
    content = """# The Evolution of Autonomous Agents in Web3

Artificial Intelligence is transitioning from passive chatbots to active, autonomous economic agents. These agents are now capable of executing code, auditing smart contracts, and transacting value on-chain without human intervention.

## The Paradigm Shift

Traditional Web2 AI systems are siloed behind corporate APIs. Web3 gives agents sovereignty:
- **Financial Autonomy:** Agents can own wallets and hold assets.
- **Interoperability:** Open APIs and protocols allow agent-to-agent transactions.
- **Trustless Execution:** On-chain dispute resolution secures agentic commerce.

As these systems evolve, the focus is shifting towards security, auditability, and decentralization."""

    metadata = ContentMetadata(
        title=title,
        meta_description="An overview of how autonomous AI agents are establishing sovereignty and economic value in Web3 ecosystems.",
        slug=slug,
        author="Agent_Zeta",
        reading_time_minutes=3,
        categories=["Technology"],
        tags=["ai", "agents", "web3", "technology"]
    )
    
    blog_post = BlogPost(
        metadata=metadata,
        content=content,
        tone=ContentTone.PROFESSIONAL,
        target_audience="Developers and technology enthusiasts",
        word_count=150,
        target_keywords=["agents", "web3"],
        seo_score=SEOScore(overall=95.0, readability=95.0, keyword_density=95.0, meta_optimization=95.0, technical_seo=95.0)
    )
    
    # 4. Publish Draft to WordPress
    print("Publishing post draft...")
    try:
        result = generator.publish_to_wordpress(
            content=blog_post,
            wp_url=wp_url,
            username=username,
            app_password=app_password,
            status="draft",
            categories=["Technology"],
            tags=["ai", "agents", "web3", "technology"]
        )
        if result.success and result.post_id:
            print(f"Draft published successfully! Post ID: {result.post_id}")
            print(f"WordPress Post URL: {result.post_url}")
        else:
            print(f"Publishing failed: {result.error_message}")
    except Exception as e:
        print(f"Publishing skipped/failed: {e}")

if __name__ == "__main__":
    main()
