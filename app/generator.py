"""Blog post content generation engine for WordPress AI Content system."""

import os
import re
import logging
from typing import List
from app.models import BlogPost, ContentMetadata, ContentTone, SEOScore
from app.llm import call_llm

logger = logging.getLogger(__name__)

# Map string tone values to ContentTone enum
_TONE_MAP = {t.value: t for t in ContentTone}


def _parse_tone(tone_str: str) -> ContentTone:
    """Convert a tone string to ContentTone enum with fallback to PROFESSIONAL."""
    return _TONE_MAP.get(tone_str.lower().strip(), ContentTone.PROFESSIONAL)


class ContentGeneratorEngine:
    """Core blog post generation engine."""

    def generate_blog_post(
        self,
        topic: str,
        target_keywords: List[str] = None,
        word_count: int = 1200,
        tone: str = "professional",
        target_audience: str = "general",
    ) -> BlogPost:
        """Generate a complete SEO-optimized blog post."""
        # Input validation
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty.")
        if word_count < 100:
            raise ValueError(f"word_count must be at least 100, got {word_count}.")
        if word_count > 10000:
            raise ValueError(f"word_count must not exceed 10000, got {word_count}.")

        try:
            logger.info(f"Generating blog post — topic: '{topic}', words: {word_count}, tone: {tone}")
            keywords = target_keywords or [topic]
            content_tone = _parse_tone(tone)

            # 1. Generate text content via LLM
            prompt = f"""Escribe un artículo técnico y profesional en español sobre el siguiente tema: "{topic}".
Público objetivo: {target_audience}
Tono del contenido: {tone}
Largo aproximado: {word_count} palabras.
Palabras clave principales a integrar: {', '.join(keywords)}

REGLAS DE FORMATO:
- Usa Markdown estructurado con un H1 al inicio, luego H2 y H3 para subsecciones.
- **Prohibido** usar subencabezados genéricos como "Introducción", "Cuerpo" o "Conclusión". Todos los subencabezados deben ser contextualmente descriptivos e informativos.
- El H1 debe contener la keyword principal.
- Incluye la keyword principal en los primeros 100 palabras.
- Mantén una prosa fluida, de alta fidelidad, evitando redundancias e introducciones artificiales.
- Responde ÚNICAMENTE con el artículo en Markdown, sin texto adicional ni explicación."""

            content = call_llm(prompt, max_tokens=min(8000, word_count * 6))

            # 2. Generate meta description via LLM
            meta_desc = self._generate_meta_description(topic, keywords, content)

            # 3. Build slug
            slug = self._generate_slug(topic)

            # 4. Build metadata
            metadata = ContentMetadata(
                title=topic,
                meta_description=meta_desc,
                slug=slug,
                categories=["Noticias"],
                tags=keywords,
                reading_time_minutes=max(1, word_count // 200),
            )

            # 5. Calculate real SEO score
            from app.seo import SEOAuditor
            seo_score = SEOAuditor()._calculate_seo_score(content, keywords[0], keywords[1:])

            return BlogPost(
                metadata=metadata,
                content=content,
                tone=content_tone,
                target_audience=target_audience,
                word_count=word_count,
                target_keywords=keywords,
                seo_score=seo_score,
                seo_recommendations=[],
                images_suggestions=[f"Futuristic image representing {topic}"],
            )

        except (ValueError, RuntimeError):
            raise
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise RuntimeError(f"Failed to generate blog post: {e}")

    def _generate_meta_description(
        self, topic: str, keywords: List[str], content: str = ""
    ) -> str:
        """Generate an SEO-friendly meta description using the LLM."""
        try:
            excerpt = content[:500] if content else ""
            prompt = f"""Escribe una meta descripción SEO-friendly para un artículo sobre "{topic}".
Keywords a incluir: {', '.join(keywords[:3])}.
{f'Extracto del artículo: {excerpt}' if excerpt else ''}

REGLAS:
- Exactamente entre 140 y 160 caracteres.
- Incluye la keyword principal al inicio.
- Usa lenguaje activo y persuasivo.
- Responde ÚNICAMENTE con la meta descripción, sin comillas ni texto adicional."""
            meta = call_llm(prompt, max_tokens=100).strip().strip('"').strip("'")
            # Fallback if too long or too short
            if len(meta) > 160 or len(meta) < 50:
                meta = f"Análisis exhaustivo sobre {topic}. Descubre {', '.join(keywords[:2])} y su impacto."
            return meta[:160]
        except Exception:
            return f"Análisis exhaustivo sobre {topic}. Descubre {', '.join(keywords[:2])} y su impacto."

    def _generate_slug(self, topic: str) -> str:
        """Generate a URL-friendly slug from a topic string."""
        if not topic:
            import time
            return f"post-{int(time.time())}"
        slug = topic.lower()
        slug = re.sub(r'[áàäâ]', 'a', slug)
        slug = re.sub(r'[éèëê]', 'e', slug)
        slug = re.sub(r'[íìïî]', 'i', slug)
        slug = re.sub(r'[óòöô]', 'o', slug)
        slug = re.sub(r'[úùüû]', 'u', slug)
        slug = re.sub(r'ñ', 'n', slug)
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        return slug[:60]
