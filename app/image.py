"""Image generation engine using fal.ai for WordPress AI Content system."""

import os
import time
import logging
import random
from typing import Optional
import fal_client
from app.models import GeneratedImage

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Image generation engine using fal.ai with integrated HIFI prompt enhancement."""
    
    # Precise visual descriptions of specific technical entities to guide the model accurately
    ENTITY_DESCRIPTIONS = {
        "solana": (
            "the Solana cryptocurrency logo, which consists of three parallel, horizontal, "
            "diagonal-edged stadium shapes (gradient bars) stacked vertically with a smooth "
            "color transition from vibrant neon cyan at the top to rich violet-purple at the bottom"
        ),
        "ethereum": (
            "the Ethereum logo, visualized as a sleek, glowing geometric octahedron "
            "made of reflective glass and crystal facets"
        ),
        "bitcoin": (
            "the Bitcoin logo, a prominent, glowing gold coin marked with the classic stylized double-stroke '₿'"
        ),
        "depin": (
            "Decentralized Physical Infrastructure Networks (DePIN), visualized as a complex mesh "
            "of glowing green and blue node-to-node fiber optic connections, decentralized wireless "
            "transmission towers, and physical server clusters"
        ),
        "ai agent": (
            "an autonomous virtual AI assistant, represented as a sleek, polished humanoid chrome robot "
            "or a glowing, translucent blue holographic avatar interface"
        ),
        "agentes de ia": (
            "autonomous virtual AI assistants, represented as sleek, polished humanoid chrome robots "
            "or glowing, translucent blue holographic avatar interfaces"
        )
    }
    
    # Robust default negative prompt to avoid common artifacts and generic CGI/cheap looks
    DEFAULT_NEGATIVE_PROMPT = (
        "cartoon, anime, painting, CGI, blurry, low quality, deformed, extra limbs, "
        "ugly, noisy, signature, watermarks, bad anatomy, deformed fingers, text labels"
    )
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize image generator."""
        self.api_key = api_key or os.environ.get("FAL_KEY")
        if self.api_key:
            os.environ["FAL_KEY"] = self.api_key

    def _enhance_prompt(self, prompt: str) -> str:
        """Enrich a basic prompt with premium technical and cinematic aesthetic modifiers."""
        clean_prompt = prompt.strip()
        
        # Inject precise visual descriptions for known technical entities
        modified_prompt = clean_prompt
        for entity, description in self.ENTITY_DESCRIPTIONS.items():
            if entity in modified_prompt.lower():
                logger.info(f"Injecting precise visual description for entity: '{entity}'")
                modified_prompt += f" (Specifically displaying {description})"
        
        # Check if the prompt already has high-end modifiers to avoid double-decorating
        hifi_modifiers = ["3d render", "photorealistic", "cyberpunk", "octane", "cinematic", "premium"]
        if any(mod in clean_prompt.lower() for mod in hifi_modifiers):
            return modified_prompt
            
        # Select best aesthetic styling: Tech Vector/Illustration vs Cinematic Tech Render
        tech_words = ["base", "solana", "ethereum", "crypto", "blockchain", "depin", "ai agent", "eliza"]
        is_tech = any(word in clean_prompt.lower() for word in tech_words)
        
        if is_tech:
            # High-end technical graphic vector art style optimized for tech sites
            decorations = [
                "Vector art, vivid colors, clean lines, sharp edges",
                "minimalist tech illustration, precise geometry",
                "bold outlines, crisp shapes, flat colors",
                "linear compositions, premium corporate tech visual"
            ]
            style_suffix = "high-end graphic design illustration, professional digital art, high contrast, clean vector style."
        else:
            # Premium cinematic photorealistic 3D render style
            decorations = [
                "premium dark cyber tech aesthetic",
                "glowing digital circuitry accents",
                "volumetric lighting",
                "ultra-detailed 3D render",
                "octane render realism",
                "futuristic hologram details"
            ]
            style_suffix = "Unreal Engine 5 rendering style, high-end commercial visualization, sharp focus, 8k resolution."
        
        # Pick 3 random but highly compatible aesthetic modifiers for variety
        chosen = random.sample(decorations, min(3, len(decorations)))
        enhanced = f"{modified_prompt}. {', '.join(chosen)}. {style_suffix}"
        return enhanced

    def generate_image(
        self, 
        prompt: str, 
        image_size: str = "landscape_4_3",
        model: str = "fal-ai/flux/schnell"
    ) -> GeneratedImage:
        """Generate an image using fal.ai with automatic prompt enhancement, negative prompting, and retry resilience."""
        # Enhance prompt for premium HIFI output
        enhanced_prompt = self._enhance_prompt(prompt)
        
        if not self.api_key:
            logger.warning("FAL_KEY not set. Using simulated image generation.")
            return self._simulate_image_generation(enhanced_prompt)

        max_retries = 2
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating image with model {model} - Attempt {attempt + 1}")
                logger.info(f"Enhanced prompt: {enhanced_prompt}")
                
                result = fal_client.run(
                    model,
                    arguments={
                        "prompt": enhanced_prompt,
                        "negative_prompt": self.DEFAULT_NEGATIVE_PROMPT,
                        "image_size": image_size
                    }
                )
                
                image_url = result["images"][0]["url"]
                revised_prompt = result.get("revised_prompt", enhanced_prompt)
                
                return GeneratedImage(
                    prompt=prompt,
                    revised_prompt=revised_prompt,
                    url=image_url,
                    width=result["images"][0].get("width"),
                    height=result["images"][0].get("height")
                )
                
            except Exception as e:
                logger.warning(f"Image generation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3.0) # Wait before retry
                else:
                    logger.error(f"All image generation attempts failed. Falling back to simulation.")
                    return self._simulate_image_generation(enhanced_prompt)
                    
        return self._simulate_image_generation(enhanced_prompt)

    def _simulate_image_generation(self, prompt: str) -> GeneratedImage:
        """Simulate image generation when API is unavailable."""
        slug = prompt.lower().replace(" ", "-")[:50]
        simulated_url = f"https://pollinations.ai/p/{slug}?width=1024&height=768&seed={random.randint(1, 1000)}"
        return GeneratedImage(
            prompt=prompt,
            url=simulated_url,
            revised_prompt=f"Simulated: {prompt}"
        )
