"""WordPress publishing and optimization engine for WordPress AI Content system."""

import os
import logging
import requests
import json
import re
from datetime import datetime
from pathlib import Path
from requests.auth import HTTPBasicAuth
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from app.models import BlogPost, WordPressPublishResult, ContentMetadata, ContentTone

load_dotenv()
logger = logging.getLogger(__name__)


def _load_category_map() -> Dict[str, int]:
    """Load WordPress category name→ID map from data/categories.json."""
    candidates = [
        Path(__file__).parent.parent / "data" / "categories.json",
        Path("data/categories.json"),
    ]
    for path in candidates:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Filter out comment keys
                return {k: v for k, v in data.items() if not k.startswith("_")}
            except Exception as e:
                logger.warning(f"Could not load categories.json from {path}: {e}")
    # Generic fallback category map if categories.json is missing
    logger.warning("categories.json not found, using built-in fallback map.")
    return {}


_CATEGORY_MAP: Dict[str, int] = _load_category_map()

class WordPressPublisher:
    """Core WordPress publishing, category management and structural schema optimizer."""
    
    def publish(
        self,
        content: BlogPost,
        wp_url: str,
        username: str,
        app_password: str,
        status: str = "draft",
        categories: List[str] = None,
        tags: List[str] = None
    ) -> WordPressPublishResult:
        """Connect to WordPress instance and publish or update posts/pages."""
        if not wp_url or not wp_url.strip():
            raise ValueError("WordPress site URL cannot be empty.")
        if not username or not username.strip():
            raise ValueError("WordPress username cannot be empty.")
        if not app_password or not app_password.strip():
            raise ValueError("WordPress Application Password cannot be empty.")
        
        from app.models import ContentStatus
        try:
            ContentStatus(status)
        except ValueError:
            raise ValueError(f"Invalid status '{status}'. Must be one of {[s.value for s in ContentStatus]}.")

        try:
            logger.info(f"Publishing to WordPress: {content.metadata.title}")
            
            base_url = wp_url.rstrip('/')
            api_url = f"{base_url}/wp-json/wp/v2/posts"
            auth = HTTPBasicAuth(username, app_password)
            
            import markdown
            html_content = markdown.markdown(content.content)
            
            payload = {
                "title": content.metadata.title,
                "content": html_content,
                "status": status,
                "slug": content.metadata.slug,
                "excerpt": content.metadata.meta_description
            }
            
            # Resolve Categories using configurable map
            cats = categories or content.metadata.categories
            if cats:
                cat_ids = []
                for cat in cats:
                    try:
                        cat_ids.append(int(cat))
                    except ValueError:
                        mapped = _CATEGORY_MAP.get(str(cat).lower())
                        if mapped:
                            cat_ids.append(mapped)
                        else:
                            logger.warning(f"Unknown category name '{cat}', skipping.")
                if cat_ids:
                    payload["categories"] = cat_ids
            
            response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"}, auth=auth, timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return WordPressPublishResult(
                    success=True,
                    post_id=data.get("id"),
                    post_url=data.get("link"),
                    published_at=datetime.now()
                )
            else:
                return WordPressPublishResult(
                    success=False,
                    error_message=f"WP REST Error {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            logger.error(f"Error publishing to WordPress: {e}")
            return WordPressPublishResult(success=False, error_message=str(e))

    def get_wordpress_categories(self, wp_url: str, username: str, app_password: str) -> Dict[str, Any]:
        """Retrieve all categories from the WordPress instance."""
        try:
            base_url = wp_url.rstrip('/')
            api_url = f"{base_url}/wp-json/wp/v2/categories"
            auth = HTTPBasicAuth(username, app_password)
            
            response = requests.get(api_url, auth=auth, timeout=30)
            if response.status_code == 200:
                return {"success": True, "categories": response.json()}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_wordpress_post(
        self,
        post_id: int,
        wp_url: str,
        username: str,
        app_password: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
        slug: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update an existing WordPress post."""
        try:
            base_url = wp_url.rstrip('/')
            api_url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
            auth = HTTPBasicAuth(username, app_password)
            
            payload = {}
            if title is not None:
                payload["title"] = title
            if content is not None:
                import markdown
                payload["content"] = markdown.markdown(content)
            if status is not None:
                payload["status"] = status
            if slug is not None:
                payload["slug"] = slug
            if categories is not None:
                cat_ids = []
                for cat in categories:
                    try:
                        cat_ids.append(int(cat))
                    except ValueError:
                        mapped = _CATEGORY_MAP.get(str(cat).lower())
                        if mapped:
                            cat_ids.append(mapped)
                if cat_ids:
                    payload["categories"] = cat_ids
                    
            if not payload:
                return {"success": False, "error": "No update fields provided."}
                
            response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"}, auth=auth, timeout=30)
            if response.status_code in [200, 201]:
                return {"success": True, "post_id": post_id}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def inject_json_ld_schema(self, post_id: int, wp_url: str, username: str, app_password: str) -> Dict[str, Any]:
        """Inject TechArticle JSON-LD structured data into an existing WordPress post."""
        try:
            base_url = wp_url.rstrip('/')
            api_url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
            auth = HTTPBasicAuth(username, app_password)
            
            get_response = requests.get(api_url, auth=auth, timeout=30)
            if get_response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch post: {get_response.text}"}
                
            post_data = get_response.json()
            post_title = post_data.get("title", {}).get("rendered", "Untitled Post")
            post_link = post_data.get("link", f"{wp_url}/?p={post_id}")
            post_content = post_data.get("content", {}).get("rendered", "")
            post_date = post_data.get("date", datetime.now().isoformat())
            post_modified = post_data.get("modified", datetime.now().isoformat())
            
            clean_content = re.sub(r'<script type="application/ld\+json">.*?</script>', '', post_content, flags=re.DOTALL)
            
            site_name = os.getenv("WP_SITE_NAME", wp_url.rstrip('/').replace('https://', '').replace('http://', ''))
            site_logo = os.getenv("WP_SITE_LOGO", "")
            author_name = os.getenv("WP_AUTHOR_NAME", "WordPress AI Content Agent")
            author_url = os.getenv("WP_AUTHOR_URL", wp_url)

            schema = {
                "@context": "https://schema.org",
                "@type": "TechArticle",
                "mainEntityOfPage": {"@type": "WebPage", "@id": post_link},
                "headline": post_title,
                "author": {
                    "@type": "Person",
                    "name": author_name,
                    "url": author_url,
                },
                "publisher": {
                    "@type": "Organization",
                    "name": site_name,
                    **({
                        "logo": {"@type": "ImageObject", "url": site_logo}
                    } if site_logo else {}),
                },
                "datePublished": post_date,
                "dateModified": post_modified,
                "description": f"Technical article published on {site_name}: {post_title}.",
            }
            
            schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
            schema_script = f'\n<script type="application/ld+json">\n{schema_json}\n</script>\n'
            
            updated_html = clean_content.strip() + schema_script
            update_response = requests.post(api_url, json={"content": updated_html}, headers={"Content-Type": "application/json"}, auth=auth, timeout=30)
            
            if update_response.status_code in [200, 201]:
                return {"success": True, "post_id": post_id, "schema": schema}
            else:
                return {"success": False, "error": update_response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def suggest_internal_links(self, post_id: int, wp_url: str, username: str, app_password: str) -> Dict[str, Any]:
        """Suggest contextual internal links by analyzing recently published posts."""
        try:
            base_url = wp_url.rstrip('/')
            api_url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
            auth = HTTPBasicAuth(username, app_password)
            
            get_response = requests.get(api_url, auth=auth, timeout=30)
            if get_response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch post: {get_response.text}"}
                
            post_data = get_response.json()
            post_content = post_data.get("content", {}).get("rendered", "")
            post_title = post_data.get("title", {}).get("rendered", "Untitled Post")
            
            posts_api_url = f"{base_url}/wp-json/wp/v2/posts?per_page=12"
            history_response = requests.get(posts_api_url, auth=auth, timeout=30)
            
            other_posts_info = []
            if history_response.status_code == 200:
                for item in history_response.json():
                    pid = item.get("id")
                    if pid == post_id:
                        continue
                    p_title = item.get("title", {}).get("rendered", "")
                    p_url = item.get("link", "")
                    if pid and p_title and p_url:
                        other_posts_info.append({"post_id": pid, "title": p_title, "url": p_url})
            
            if not other_posts_info:
                return {"success": True, "post_id": post_id, "suggestions": []}
                
            from app.llm import call_llm
            site_name = os.getenv("WP_SITE_NAME", wp_url.rstrip('/'))
            prompt = f"""Actúa como un experto en SEO On-Page para el sitio {site_name}.
Sugerir enlaces internos contextuales.

Artículo Objetivo (Título): {post_title}
Contenido del Artículo Objetivo: {post_content[:4000]}

Artículos Ya Publicados:
{json.dumps(other_posts_info, ensure_ascii=False, indent=2)}

REGLA CRÍTICA DE ANCHOR TEXT:
El "anchor_text" sugerido debe ser una frase o palabra corta de 1 a 4 palabras (por ejemplo: "red Base", "Solana", "Eliza", "agentes de IA", "Capa 2") que exista LITERALMENTE, EXACTAMENTE e IDÉNTICAMENTE dentro del Contenido del Artículo Objetivo para que el reemplazo pueda ejecutarse. No uses títulos de los artículos publicados como anchor_text a menos que aparezcan idénticamente en el cuerpo.

Responde ÚNICAMENTE con un JSON limpio y válido (sin bloques markdown de código ```json o texto adicional) con las siguientes llaves:
- "suggestions": lista de objetos, donde cada objeto tiene las llaves:
  - "anchor_text": frase exacta de 1 a 4 palabras presente literalmente en el Artículo Objetivo a enlazar
  - "target_url": URL del post destino
  - "context": oración resultante
  - "justification": por qué es valioso para el SEO"""

            response_text = call_llm(prompt)
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            try:
                suggestions = json.loads(cleaned)
            except Exception:
                suggestions = {"suggestions": []}
                
            return {"success": True, "post_id": post_id, "suggestions": suggestions.get("suggestions", [])}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def apply_internal_links(self, post_id: int, wp_url: str, username: str, app_password: str) -> Dict[str, Any]:
        """Suggest and automatically apply contextual internal links in the post HTML body."""
        try:
            # 1. Get suggestions
            sug_res = self.suggest_internal_links(post_id, wp_url, username, app_password)
            if not sug_res.get("success") or not sug_res.get("suggestions"):
                return {"success": False, "error": "No suggestions found to apply."}
                
            suggestions = sug_res["suggestions"]
            
            # 2. Get post data
            base_url = wp_url.rstrip('/')
            api_url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
            auth = HTTPBasicAuth(username, app_password)
            
            get_response = requests.get(api_url, auth=auth, timeout=30)
            if get_response.status_code != 200:
                return {"success": False, "error": "Failed to fetch post to apply links."}
                
            post_data = get_response.json()
            post_content = post_data.get("content", {}).get("rendered", "")
            
            # 3. Apply links in HTML content
            updated_content = post_content
            applied_links = []
            
            for sug in suggestions:
                anchor = sug.get("anchor_text", "").strip()
                target_url = sug.get("target_url", "").strip()
                if not anchor or not target_url:
                    continue
                
                # Check if already linked
                if f'href="{target_url}"' in updated_content or f'href=\'{target_url}\'' in updated_content:
                    continue
                
                # Simple case-insensitive replacement for first occurrence of the anchor text,
                # ensuring we only replace if it's not already part of an HTML tag.
                pattern = re.compile(re.escape(anchor), re.IGNORECASE)
                
                # Check if anchor is present
                match = pattern.search(updated_content)
                if match:
                    # Check if match is inside an existing anchor tag <a>...</a>
                    # Simple heuristic: find if there's a close </a> or open <a before/after
                    start, end = match.span()
                    before = updated_content[:start]
                    # If we are inside an <a> tag or any HTML tag <...>, skip replacement
                    if before.rfind('<a') > before.rfind('</a>') or before.rfind('<') > before.rfind('>'):
                        continue
                        
                    replacement = f'<a href="{target_url}">{match.group(0)}</a>'
                    updated_content = updated_content[:start] + replacement + updated_content[end:]
                    applied_links.append({"anchor_text": anchor, "target_url": target_url})
            
            if not applied_links:
                return {"success": True, "post_id": post_id, "applied": [], "message": "All suggestions were already linked or not found."}
                
            # 4. Update on WordPress
            update_response = requests.post(api_url, json={"content": updated_content}, headers={"Content-Type": "application/json"}, auth=auth, timeout=30)
            if update_response.status_code in [200, 201]:
                return {"success": True, "post_id": post_id, "applied": applied_links}
            else:
                return {"success": False, "error": update_response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_wordpress_posts(
        self,
        wp_url: str,
        username: str,
        app_password: str,
        per_page: int = 10,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Retrieve a paginated list of posts from WordPress."""
        try:
            base_url = wp_url.rstrip('/')
            api_url = f"{base_url}/wp-json/wp/v2/posts"
            auth = HTTPBasicAuth(username, app_password)
            params = {"per_page": min(per_page, 100), "page": page, "_fields": "id,title,link,status,date,excerpt"}
            response = requests.get(api_url, auth=auth, params=params, timeout=30)
            if response.status_code == 200:
                posts = response.json()
                total = int(response.headers.get("X-WP-Total", len(posts)))
                total_pages = int(response.headers.get("X-WP-TotalPages", 1))
                return {
                    "success": True,
                    "posts": posts,
                    "total": total,
                    "total_pages": total_pages,
                    "current_page": page,
                }
            else:
                return {"success": False, "error": f"WP REST Error {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"Error fetching WordPress posts: {e}")
            return {"success": False, "error": str(e)}

    def create_simple_post(
        self,
        title: str,
        content: str,
        wp_url: str,
        username: str,
        app_password: str,
        status: str = "draft",
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Publish a simple post from plain markdown without requiring a BlogPost object."""
        try:
            import markdown as md_lib
            base_url = wp_url.rstrip('/')
            api_url = f"{base_url}/wp-json/wp/v2/posts"
            auth = HTTPBasicAuth(username, app_password)

            payload: Dict[str, Any] = {
                "title": title,
                "content": md_lib.markdown(content),
                "status": status,
            }

            if categories:
                cat_ids = []
                for cat in categories:
                    try:
                        cat_ids.append(int(cat))
                    except ValueError:
                        mapped = _CATEGORY_MAP.get(str(cat).lower())
                        if mapped:
                            cat_ids.append(mapped)
                if cat_ids:
                    payload["categories"] = cat_ids

            if tags:
                payload["tags_input"] = tags

            response = requests.post(
                api_url, json=payload,
                headers={"Content-Type": "application/json"},
                auth=auth, timeout=30,
            )
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "post_id": data.get("id"),
                    "post_url": data.get("link"),
                    "status": status,
                }
            else:
                return {"success": False, "error": f"WP REST Error {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"Error creating simple WordPress post: {e}")
            return {"success": False, "error": str(e)}
