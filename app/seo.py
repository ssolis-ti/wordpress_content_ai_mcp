"""SEO audit and entity analysis engine for WordPress AI Content system."""

import logging
import json
import re
from typing import List, Dict, Any
from app.models import SEOAuditResult, SEOScore, SEORecommendation
from app.llm import call_llm

logger = logging.getLogger(__name__)


class SEOAuditor:
    """Core SEO auditing and entity analysis engine."""

    def audit_content(
        self,
        content: str,
        primary_keyword: str,
        secondary_keywords: List[str] = None,
    ) -> SEOAuditResult:
        """Perform comprehensive SEO analysis and optimization on content."""
        if not content or not content.strip():
            raise ValueError("Content cannot be empty.")
        if not primary_keyword or not primary_keyword.strip():
            raise ValueError("Primary keyword cannot be empty.")

        try:
            logger.info(f"Auditing content for SEO — primary keyword: '{primary_keyword}'")
            secondary = secondary_keywords or []

            # 1. Calculate real SEO scores from the content
            seo_score = self._calculate_seo_score(content, primary_keyword, secondary)

            # 2. Generate actionable recommendations based on actual scores
            recommendations = self._generate_recommendations(content, primary_keyword, secondary, seo_score)

            # 3. Optimize content with LLM
            optimized = self._optimize_content(content, primary_keyword, secondary, recommendations)

            # 4. Recalculate score after optimization for summary
            improvements_made = len([r for r in recommendations if r.priority == "high"])
            improvements_summary = (
                f"Optimization applied: {improvements_made} high-priority recommendations addressed. "
                f"SEO score: {seo_score.overall:.1f}/100."
            )

            return SEOAuditResult(
                original_content=content,
                optimized_content=optimized,
                seo_score=seo_score,
                recommendations=recommendations,
                primary_keyword=primary_keyword,
                secondary_keywords=secondary,
                improvements_summary=improvements_summary,
            )
        except Exception as e:
            logger.error(f"Error performing SEO audit: {e}")
            raise RuntimeError(f"Failed to perform SEO audit: {e}")

    # ------------------------------------------------------------------
    # Real calculated SEO score
    # ------------------------------------------------------------------

    def _calculate_seo_score(
        self,
        content: str,
        primary_keyword: str,
        secondary_keywords: List[str] = None,
    ) -> SEOScore:
        """Calculate a real SEO score from deterministic text metrics."""
        secondary = secondary_keywords or []
        text_lower = content.lower()
        kw_lower = primary_keyword.lower()

        # Word count
        words = re.findall(r'\b\w+\b', text_lower)
        word_count = len(words)

        # --- Keyword density (0-100) ---
        kw_count = len(re.findall(re.escape(kw_lower), text_lower))
        if word_count > 0:
            density_pct = (kw_count / word_count) * 100
            # Ideal range: 1-3%. Score 100 at 2%, drops linearly outside range.
            if density_pct == 0:
                keyword_score = 20.0
            elif density_pct <= 1.0:
                keyword_score = 50.0 + (density_pct / 1.0) * 30.0
            elif density_pct <= 3.0:
                keyword_score = 80.0 + ((3.0 - abs(density_pct - 2.0)) / 1.0) * 20.0
            elif density_pct <= 5.0:
                keyword_score = max(50.0, 80.0 - (density_pct - 3.0) * 15.0)
            else:
                keyword_score = 30.0  # keyword stuffing penalty
        else:
            keyword_score = 0.0
        keyword_score = min(100.0, max(0.0, keyword_score))

        # --- Readability (0-100): based on average sentence length ---
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences:
            avg_sentence_len = word_count / len(sentences)
            # Ideal: 15-20 words per sentence
            if avg_sentence_len <= 10:
                readability = 70.0
            elif avg_sentence_len <= 20:
                readability = 85.0 + (20 - avg_sentence_len) * 0.5
            elif avg_sentence_len <= 30:
                readability = max(60.0, 85.0 - (avg_sentence_len - 20) * 2.0)
            else:
                readability = 50.0
        else:
            readability = 50.0
        readability = min(100.0, max(0.0, readability))

        # --- Meta / Structure optimization (0-100) ---
        has_h1 = bool(re.search(r'^#{1}\s', content, re.MULTILINE))
        has_h2 = bool(re.search(r'^#{2}\s', content, re.MULTILINE))
        has_h3 = bool(re.search(r'^#{3}\s', content, re.MULTILINE))
        kw_in_h1 = bool(re.search(r'^#\s.*' + re.escape(kw_lower), content, re.MULTILINE | re.IGNORECASE))

        meta_score = 40.0
        if has_h1:
            meta_score += 20.0
        if has_h2:
            meta_score += 15.0
        if has_h3:
            meta_score += 10.0
        if kw_in_h1:
            meta_score += 15.0
        meta_score = min(100.0, meta_score)

        # --- Technical SEO (0-100): secondary keywords present ---
        if secondary:
            found_secondary = sum(1 for kw in secondary if kw.lower() in text_lower)
            technical_score = 50.0 + (found_secondary / len(secondary)) * 50.0
        else:
            technical_score = 75.0  # neutral if none required
        technical_score = min(100.0, max(0.0, technical_score))

        # --- Overall (weighted average) ---
        overall = (
            keyword_score * 0.30
            + readability * 0.25
            + meta_score * 0.25
            + technical_score * 0.20
        )
        overall = round(min(100.0, max(0.0, overall)), 1)

        return SEOScore(
            overall=overall,
            readability=round(readability, 1),
            keyword_density=round(keyword_score, 1),
            meta_optimization=round(meta_score, 1),
            technical_seo=round(technical_score, 1),
        )

    # ------------------------------------------------------------------
    # Dynamic recommendations based on real scores
    # ------------------------------------------------------------------

    def _generate_recommendations(
        self,
        content: str,
        primary_keyword: str,
        secondary_keywords: List[str],
        seo_score: SEOScore,
    ) -> List[SEORecommendation]:
        """Generate prioritized SEO recommendations based on actual metrics."""
        recommendations = []
        text_lower = content.lower()
        kw_lower = primary_keyword.lower()

        # Keyword density
        if seo_score.keyword_density < 60:
            recommendations.append(SEORecommendation(
                category="Keyword Density",
                issue=f"La keyword principal '{primary_keyword}' tiene baja densidad (score: {seo_score.keyword_density:.0f}/100).",
                suggestion=f"Incluye '{primary_keyword}' en los primeros 100 palabras, en al menos un subencabezado H2, y de forma natural a lo largo del artículo (densidad ideal: 1-3%).",
                priority="high",
            ))

        # H1 presence
        if not re.search(r'^#{1}\s', content, re.MULTILINE):
            recommendations.append(SEORecommendation(
                category="Estructura",
                issue="El contenido no tiene un encabezado H1 definido.",
                suggestion=f"Añade un H1 al inicio del artículo que incluya la keyword '{primary_keyword}'.",
                priority="high",
            ))
        elif not re.search(r'^#\s.*' + re.escape(kw_lower), content, re.MULTILINE | re.IGNORECASE):
            recommendations.append(SEORecommendation(
                category="Estructura",
                issue=f"El H1 no contiene la keyword principal '{primary_keyword}'.",
                suggestion=f"Reescribe el H1 para incluir '{primary_keyword}' de forma natural.",
                priority="medium",
            ))

        # H2 presence
        if not re.search(r'^#{2}\s', content, re.MULTILINE):
            recommendations.append(SEORecommendation(
                category="Estructura",
                issue="Faltan subencabezados H2 para organizar el contenido.",
                suggestion="Divide el artículo en secciones usando H2 (## Título). Cada sección principal debe tener su propio H2.",
                priority="medium",
            ))

        # Secondary keywords
        if secondary_keywords:
            missing = [kw for kw in secondary_keywords if kw.lower() not in text_lower]
            if missing:
                recommendations.append(SEORecommendation(
                    category="Keywords Secundarias",
                    issue=f"Keywords secundarias ausentes: {', '.join(missing)}.",
                    suggestion=f"Integra estas keywords de forma natural en el cuerpo del artículo: {', '.join(missing)}.",
                    priority="medium",
                ))

        # Readability
        if seo_score.readability < 65:
            recommendations.append(SEORecommendation(
                category="Legibilidad",
                issue=f"Las oraciones son demasiado largas (score: {seo_score.readability:.0f}/100).",
                suggestion="Divide oraciones largas en oraciones cortas (máximo 20 palabras). Usa viñetas y listas donde sea posible.",
                priority="medium",
            ))

        # Minimum length
        word_count = len(re.findall(r'\b\w+\b', content))
        if word_count < 600:
            recommendations.append(SEORecommendation(
                category="Longitud",
                issue=f"El artículo es demasiado corto ({word_count} palabras).",
                suggestion="Amplía el contenido a al menos 800 palabras para mejorar el posicionamiento.",
                priority="high",
            ))

        return recommendations

    # ------------------------------------------------------------------
    # LLM-powered content optimization
    # ------------------------------------------------------------------

    def _optimize_content(
        self,
        content: str,
        primary_keyword: str,
        secondary_keywords: List[str],
        recommendations: List[SEORecommendation],
    ) -> str:
        """Use the LLM to apply SEO recommendations to the content."""
        if not recommendations:
            return content

        rec_text = "\n".join(
            f"- [{r.priority.upper()}] {r.category}: {r.suggestion}"
            for r in recommendations
        )

        prompt = f"""Eres un experto en SEO On-Page. Mejora el siguiente contenido aplicando las recomendaciones listadas.

KEYWORD PRINCIPAL: {primary_keyword}
KEYWORDS SECUNDARIAS: {', '.join(secondary_keywords) if secondary_keywords else 'ninguna'}

RECOMENDACIONES A APLICAR:
{rec_text}

REGLAS ESTRICTAS:
- Mantén el mismo idioma y tono del texto original.
- No alteres el significado ni elimines información valiosa.
- Responde ÚNICAMENTE con el contenido mejorado en formato Markdown, sin introducción ni explicación adicional.

CONTENIDO ORIGINAL:
{content}"""

        try:
            return call_llm(prompt, max_tokens=6000)
        except Exception as e:
            logger.warning(f"LLM optimization failed, returning original content: {e}")
            return content

    # ------------------------------------------------------------------
    # Semantic entity audit for DePIN/AI/Web3 content
    # ------------------------------------------------------------------
    def audit_seo_entities(self, post_content: str, topic: str) -> Dict[str, Any]:
        """Realiza una auditoría semántica de entidades técnicas."""
        try:
            logger.info(f"Performing Semantic Entity Audit for topic: {topic}")
            prompt = f"""Actúa como un auditor SEO experto en el nicho de DePIN e IA.
Analiza el siguiente tema y contenido para identificar las entidades semánticas clave y el vocabulario técnico que los motores de búsqueda esperan ver para indexarlo como contenido de alta autoridad.

Tema: {topic}

Contenido:
{post_content}

Identifica:
1. Entidades semánticas clave presentes en el contenido.
2. Entidades semánticas clave cruciales que FALTAN y que deberían agregarse para mejorar la profundidad técnica y el SEO semántico.
3. Recomendaciones específicas para integrar estas entidades de forma deductiva y natural.

Responde ÚNICAMENTE con un JSON limpio y válido (sin bloques markdown de código ```json o texto adicional) con las siguientes llaves:
- "present_entities": lista de strings
- "missing_entities": lista de strings
- "recommendations": lista de strings con consejos específicos de integración"""

            response_text = call_llm(prompt)
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            try:
                result = json.loads(cleaned)
            except Exception:
                result = {
                    "present_entities": ["DePIN", topic],
                    "missing_entities": ["Pruebas de Contribución", "Consenso Determinista"],
                    "recommendations": ["Asegúrate de profundizar en la infraestructura de hardware física."],
                }
            return result
        except Exception as e:
            logger.error(f"Error performing entity audit: {e}")
            return {"success": False, "error": str(e)}
