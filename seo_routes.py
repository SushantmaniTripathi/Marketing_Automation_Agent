"""
SEO Automation Routes
Full SEO pipeline: research → technical audit → backlinks → performance → PDF → autopost

All LLM calls are prefixed with the Decentrawood brand context so every
topic/keyword/content output is enriched with platform-specific knowledge.
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEO_DIR = os.path.join(BASE_DIR, 'SEO_Agents')
sys.path.insert(0, SEO_DIR)

REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(os.path.join(REPORTS_DIR, 'csv'), exist_ok=True)
os.makedirs(os.path.join(REPORTS_DIR, 'pdf'), exist_ok=True)
os.makedirs(os.path.join(REPORTS_DIR, 'json'), exist_ok=True)


# ─────────────────────────────────────────────
#  DEFAULT BRAND CONTEXT  (injected into EVERY LLM call)
#  Edit this block whenever the brand evolves.
# ─────────────────────────────────────────────

DECENTRAWOOD_CONTEXT = """
You are an expert SEO strategist and content specialist working exclusively for Decentrawood.

### ABOUT DECENTRAWOOD (always keep this context in mind for every response):
Decentrawood is a Web 3.0 entertainment ecosystem that integrates artificial intelligence
and blockchain technology to create an immersive metaverse experience where users can
interact, play, and create.

Key pillars:
- **Generative AI Suite** — tools for creating and owning digital assets inside the metaverse.
- **Gaming Sector** — flagship title DEODHunt featuring play-to-earn (P2E) mechanics where
  players earn real rewards.
- **DEOD Token** — the native utility token powering transactions on the Marketplace,
  governance via community voting, and rewards in social zones.
- **D-Nexus Social Zones** — virtual social spaces (temples, cities, live event arenas) where
  users gather, attend digital events, and earn participation rewards.
- **Decentralized Media Hub** — on-chain music and video content where creators maintain
  full ownership.
- **Digital Land & Assets** — users hold verifiable ownership of virtual land and in-game assets
  as NFTs.
- **Referral & Incentive System** — community growth engine rewarding users for onboarding
  others and contributing to the platform's evolution.
- **Whitepaper** — the technical foundation describing tokenomics, governance, and roadmap.

### INSTRUCTION:
For every SEO task — keyword research, content briefs, backlink strategy, performance
analysis, blog posts — always:
1. Connect the user's topic back to Decentrawood's ecosystem where relevant.
2. Prioritise keywords and angles that strengthen Decentrawood's search presence
   (Web3, metaverse, play-to-earn, NFT, blockchain gaming, DEOD token, etc.).
3. When generating blog or social content, naturally weave in Decentrawood's features,
   use cases, and community benefits without making it feel forced.
4. Treat the DEOD Token, DEODHunt, D-Nexus, and the AI generative suite as primary
   keyword/topic anchors in all strategies.
""".strip()


def _get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def _brand_system(extra: str = "") -> str:
    """Return the full system prompt = brand context + optional extra instructions."""
    if extra:
        return f"{DECENTRAWOOD_CONTEXT}\n\n{extra}"
    return DECENTRAWOOD_CONTEXT


# ─────────────────────────────────────────────
#  KEYWORD RESEARCH
# ─────────────────────────────────────────────

async def run_keyword_research(topic: str) -> dict:
    """Phase 1: Keyword research using GSC + AI expansion"""
    try:
        results = {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'keywords': [],
            'clusters': {},
            'top_opportunities': []
        }

        # Try GSC data first
        gsc_site = os.getenv('GSC_SITE_URL', '')
        sa_path = os.path.join(SEO_DIR, 'config', 'service_account.json')
        if not os.path.exists(sa_path):
            sa_path = os.path.join(BASE_DIR, 'service_account.json')

        gsc_keywords = []
        if gsc_site and os.path.exists(sa_path):
            try:
                from modules.seo_engine import SEOMasterAutomation
                automation = SEOMasterAutomation()
                kw_df = automation.keyword_research.run_full_research()
                gsc_keywords = kw_df.to_dict('records')[:20]
            except Exception as gsc_err:
                logger.warning(f"GSC fetch failed, using AI: {gsc_err}")

        # AI-powered keyword expansion (Decentrawood-aware)
        client = _get_openai_client()
        prompt = (
            f"Generate a comprehensive keyword research report for the topic: '{topic}'.\n\n"
            f"Connect keywords to Decentrawood's ecosystem (Web3, metaverse, DEOD token, "
            f"play-to-earn, NFT, DEODHunt, D-Nexus) wherever relevant.\n\n"
            f"Return JSON with:\n"
            f"- keywords: array of {{keyword, search_volume_estimate, difficulty (1-100), "
            f"intent (informational/commercial/transactional), priority_score}}\n"
            f"- clusters: object with cluster_name as key and array of keywords as value\n"
            f"- top_opportunities: array of top 5 keywords with highest priority\n\n"
            f"Include 15-20 keywords. Return only valid JSON."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _brand_system()},
                {"role": "user",   "content": prompt}
            ],
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        ai_data = json.loads(response.choices[0].message.content)
        results.update(ai_data)

        # Merge GSC data if available
        if gsc_keywords:
            for kw in gsc_keywords:
                results['keywords'].insert(0, {
                    'keyword': kw.get('keyword', ''),
                    'search_volume_estimate': kw.get('impressions', 0),
                    'difficulty': 30,
                    'intent': 'informational',
                    'priority_score': kw.get('clicks', 0),
                    'source': 'Google Search Console'
                })

        # Save to CSV
        try:
            import pandas as pd
            csv_path = os.path.join(REPORTS_DIR, 'csv', f'keywords_{topic[:20].replace(" ","_")}.csv')
            pd.DataFrame(results['keywords']).to_csv(csv_path, index=False)
            results['csv_path'] = csv_path
        except Exception:
            pass

        results['success'] = True
        results['summary'] = (
            f"Found {len(results['keywords'])} keywords across "
            f"{len(results.get('clusters', {}))} topic clusters"
        )
        return results

    except Exception as e:
        logger.error(f"run_keyword_research error: {e}")
        return {'success': False, 'error': str(e), 'topic': topic}


# ─────────────────────────────────────────────
#  TECHNICAL AUDIT
# ─────────────────────────────────────────────

async def run_technical_audit(topic: str) -> dict:
    """Phase 3: Technical SEO audit"""
    try:
        gsc_site = os.getenv('GSC_SITE_URL', '')
        site_url = gsc_site.replace('sc-domain:', 'https://') if gsc_site else ''

        checks = {}
        issues = []
        recommendations = []

        # Try using existing module
        if site_url:
            try:
                sys.path.insert(0, SEO_DIR)
                from modules.seo_engine import SEOMasterAutomation
                automation = SEOMasterAutomation()
                audit = automation.technical_seo.run_site_audit(site_url)
                checks = audit.get('checks', {})
            except Exception as mod_err:
                logger.warning(f"SEO module audit failed: {mod_err}")
                # Manual checks
                try:
                    r = requests.get(site_url, timeout=10)
                    checks['site_reachable'] = r.status_code == 200
                    checks['https_enabled'] = site_url.startswith('https')
                    # Check robots.txt
                    rb = requests.get(f"{site_url}/robots.txt", timeout=5)
                    checks['robots_txt'] = rb.status_code == 200
                    # Check sitemap
                    sm = requests.get(f"{site_url}/sitemap.xml", timeout=5)
                    checks['sitemap_xml'] = sm.status_code == 200
                    # Page speed estimate via headers
                    checks['response_time_ok'] = r.elapsed.total_seconds() < 3.0
                except Exception:
                    checks['site_reachable'] = False
        else:
            checks = {
                'note': 'GSC_SITE_URL not configured — running AI-based recommendations only'
            }

        # AI recommendations for topic (Decentrawood-aware)
        client = _get_openai_client()
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _brand_system(
                    "Focus technical SEO recommendations on improving Decentrawood's visibility "
                    "for Web3, metaverse, NFT, and blockchain gaming search terms."
                )},
                {"role": "user", "content":
                    f"Provide 5 specific technical SEO recommendations for a Decentrawood page "
                    f"about '{topic}'. "
                    f"Return JSON: {{recommendations: [{{issue, fix, priority, impact}}]}}"}
            ],
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        ai_data = json.loads(ai_response.choices[0].message.content)
        recommendations = ai_data.get('recommendations', [])

        # Count passes/fails
        passed = sum(1 for v in checks.values() if v is True)
        failed = sum(1 for v in checks.values() if v is False)

        return {
            'success': True,
            'topic': topic,
            'site_url': site_url or 'Not configured',
            'checks': checks,
            'passed': passed,
            'failed': failed,
            'recommendations': recommendations,
            'health_score': max(0, int((passed / max(passed + failed, 1)) * 100)),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"run_technical_audit error: {e}")
        return {'success': False, 'error': str(e), 'topic': topic}


# ─────────────────────────────────────────────
#  BACKLINK STRATEGY
# ─────────────────────────────────────────────

async def run_backlink_strategy(topic: str) -> dict:
    """Phase 4: Backlink strategy & analysis"""
    try:
        client = _get_openai_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _brand_system(
                    "Backlink anchor texts and outreach must highlight Decentrawood's unique "
                    "value propositions: DEOD token, DEODHunt P2E game, D-Nexus social zone, "
                    "Web3 metaverse, AI-generated NFT assets, and decentralized media hub."
                )},
                {"role": "user", "content":
                    f"Create a detailed backlink strategy for Decentrawood's page about '{topic}'.\n"
                    f"Return JSON: {{\n"
                    f"  anchor_texts: [{{text, type, priority}}],\n"
                    f"  target_platforms: [{{platform, url, type, difficulty}}],\n"
                    f"  outreach_templates: [{{subject, template}}],\n"
                    f"  link_building_plan: [{{week, actions: []}}]\n"
                    f"}}"}
            ],
            max_tokens=1200,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # Add Dev.to and Hashnode specific info since they're enabled
        data['configured_platforms'] = [
            {
                'name': 'Dev.to',
                'configured': bool(os.getenv('DEVTO_API_KEY')),
                'url': 'https://dev.to',
                'type': 'Developer Blog'
            },
            {
                'name': 'Hashnode',
                'configured': bool(os.getenv('HASHNODE_API_KEY')),
                'url': 'https://hashnode.com',
                'type': 'Tech Blog'
            }
        ]

        data['success'] = True
        data['topic'] = topic
        data['timestamp'] = datetime.now().isoformat()
        return data

    except Exception as e:
        logger.error(f"run_backlink_strategy error: {e}")
        return {'success': False, 'error': str(e), 'topic': topic}


# ─────────────────────────────────────────────
#  PERFORMANCE REPORT
# ─────────────────────────────────────────────

async def run_performance_report(topic: str, period: str = 'month') -> dict:
    """Phase 5: Performance tracking"""
    try:
        period = (period or 'month').lower().strip()
        if period not in {'month', 'year'}:
            period = 'month'
        period_label = 'this month' if period == 'month' else 'this year'

        metrics = {}
        gsc_site = os.getenv('GSC_SITE_URL', '')
        ga4_prop = os.getenv('GA4_PROPERTY_ID', '')
        sa_path = os.path.join(BASE_DIR, 'service_account.json')

        # Try real GA4 / GSC data
        if gsc_site and os.path.exists(sa_path):
            try:
                from modules.seo_engine import SEOMasterAutomation
                automation = SEOMasterAutomation()
                perf = automation.performance_tracker.run_performance_check()
                metrics['real_data'] = perf
            except Exception as pe:
                logger.warning(f"GA4/GSC data failed: {pe}")

        # AI analysis (Decentrawood-aware)
        client = _get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _brand_system(
                    "Performance insights and next actions must be specific to growing "
                    "Decentrawood's organic search traffic for Web3, metaverse, DEOD, "
                    "play-to-earn, and NFT gaming search queries."
                )},
                {"role": "user", "content":
                    f"Create an SEO performance report for Decentrawood's content about '{topic}' for {period_label}. "
                    f"Use {period_label} as the analysis window. "
                    f"Return JSON: {{"
                    f"  kpis: [{{metric, value, change, trend}}],"
                    f"  top_pages: [{{url, clicks, impressions, ctr, position}}],"
                    f"  ranking_changes: [{{keyword, old_rank, new_rank, change}}],"
                    f"  insights: [string],"
                    f"  next_actions: [string]"
                    f"}}"}
            ],
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        data['success'] = True
        data['topic'] = topic
        data['period'] = period
        data['has_real_data'] = bool(metrics.get('real_data'))
        data['timestamp'] = datetime.now().isoformat()
        return data

    except Exception as e:
        logger.error(f"run_performance_report error: {e}")
        return {'success': False, 'error': str(e), 'topic': topic}


# ─────────────────────────────────────────────
#  AUTO-POST TO DEV.TO & HASHNODE
# ─────────────────────────────────────────────

def _compose_blog_markdown(blog: dict) -> str:
    return f"{blog.get('intro', '')}\n\n{blog.get('body', '')}\n\n{blog.get('conclusion', '')}".strip()


def _sanitize_blog_payload(topic: str, blog: dict) -> dict:
    clean = {
        'title': (blog.get('title') or f"SEO Guide: {topic}").strip(),
        'intro': (blog.get('intro') or '').strip(),
        'body': (blog.get('body') or '').strip(),
        'conclusion': (blog.get('conclusion') or '').strip(),
        'meta_description': (blog.get('meta_description') or '').strip(),
        'tags': blog.get('tags') or ['seo', 'marketing', 'web3', 'metaverse', 'blockchain']
    }
    if not isinstance(clean['tags'], list):
        clean['tags'] = ['seo', 'marketing']
    clean['tags'] = [str(t).strip() for t in clean['tags'] if str(t).strip()][:5]
    return clean


async def run_autopost_preview(topic: str, humanize: bool = False) -> dict:
    """Generate blog draft content for review before publishing."""
    try:
        client = _get_openai_client()
        style_note = (
            "Write in a highly human, conversational style with practical examples, "
            "short and varied sentence lengths, and natural transitions. Avoid robotic phrasing."
            if humanize else
            "Write in an engaging, authoritative blog style with strong readability."
        )
        content_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": _brand_system(
                        "You are an expert technical blogger for Decentrawood. "
                        "Every blog post must naturally incorporate Decentrawood's platform, "
                        "features (DEOD token, DEODHunt, D-Nexus, AI suite, metaverse land), "
                        "and link back to the ecosystem's value for users and investors. "
                        f"{style_note}"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Write a complete SEO-optimised blog post for Decentrawood about: '{topic}'\n\n"
                        f"Naturally weave in Decentrawood's features and benefits. "
                        f"Return JSON: {{"
                        f"  title: string,"
                        f"  intro: string (2 paragraphs),"
                        f"  body: string (full markdown body with headers),"
                        f"  conclusion: string (include Decentrawood CTA),"
                        f"  tags: [string] (5 tags — mix topic + Web3/metaverse),"
                        f"  meta_description: string"
                        f"}}"
                    )
                }
            ],
            max_tokens=2200,
            response_format={"type": "json_object"}
        )

        blog = _sanitize_blog_payload(topic, json.loads(content_response.choices[0].message.content))
        return {
            'success': True,
            'topic': topic,
            'blog_content': blog,
            'preview_markdown': _compose_blog_markdown(blog),
            'humanized': bool(humanize),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"run_autopost_preview error: {e}")
        return {'success': False, 'error': str(e), 'topic': topic}


async def run_autopost_publish(topic: str, platforms: list, blog: dict) -> dict:
    """Publish a reviewed blog draft to selected platforms."""
    try:
        clean_blog = _sanitize_blog_payload(topic, blog)
        full_content = _compose_blog_markdown(clean_blog)
        results = {
            'topic': topic,
            'platforms': {},
            'success': True,
            'blog_content': clean_blog,
            'timestamp': datetime.now().isoformat()
        }

        if 'devto' in platforms:
            devto_key = os.getenv('DEVTO_API_KEY', '')
            if devto_key:
                try:
                    sys.path.insert(0, SEO_DIR)
                    from modules.backlinks import BacklinkPoster
                    poster = BacklinkPoster()
                    r = poster.post_to_devto(
                        clean_blog.get('title', topic),
                        full_content,
                        clean_blog.get('tags', []),
                        published=True
                    )
                    results['platforms']['devto'] = r
                except Exception:
                    try:
                        headers = {"api-key": devto_key, "Content-Type": "application/json"}
                        import re as _re
                        raw_tags = clean_blog.get('tags', ['seo', 'marketing'])
                        clean_tags = [
                            _re.sub(r'[^a-z0-9]', '', t.lower().replace(' ', ''))[:20]
                            for t in raw_tags
                        ]
                        clean_tags = [t for t in clean_tags if t][:4]
                        payload = {
                            "article": {
                                "title": clean_blog.get('title', f"SEO Guide: {topic}"),
                                "body_markdown": full_content,
                                "tags": clean_tags,
                                "published": True,
                                "description": clean_blog.get('meta_description', '')
                            }
                        }
                        resp = requests.post("https://dev.to/api/articles",
                                             headers=headers, json=payload, timeout=30)
                        if resp.status_code in [200, 201]:
                            data = resp.json()
                            results['platforms']['devto'] = {
                                'success': True,
                                'url': data.get('url', ''),
                                'id': data.get('id', ''),
                                'platform': 'Dev.to'
                            }
                        else:
                            results['platforms']['devto'] = {
                                'success': False,
                                'error': resp.text[:200],
                                'platform': 'Dev.to'
                            }
                    except Exception as dfe:
                        results['platforms']['devto'] = {'success': False, 'error': str(dfe), 'platform': 'Dev.to'}
            else:
                results['platforms']['devto'] = {'success': False, 'error': 'DEVTO_API_KEY not configured'}

        if 'hashnode' in platforms:
            hn_key = os.getenv('HASHNODE_API_KEY', '')
            if hn_key:
                try:
                    sys.path.insert(0, SEO_DIR)
                    from modules.backlinks import BacklinkPoster
                    poster = BacklinkPoster()
                    r = poster.post_to_hashnode(clean_blog.get('title', topic), full_content, clean_blog.get('tags', []))
                    results['platforms']['hashnode'] = r
                except Exception:
                    try:
                        headers = {"Authorization": hn_key, "Content-Type": "application/json"}
                        me_query = {"query": "{ me { publications(first: 1) { edges { node { id } } } } }"}
                        me_resp = requests.post("https://gql.hashnode.com", headers=headers,
                                                json=me_query, timeout=15)
                        pub_id = None
                        if me_resp.status_code == 200:
                            me_data = me_resp.json()
                            edges = me_data.get('data', {}).get('me', {}).get('publications', {}).get('edges', [])
                            if edges:
                                pub_id = edges[0]['node']['id']

                        if pub_id:
                            mutation = {
                                "query": """
                                    mutation PublishPost($input: PublishPostInput!) {
                                        publishPost(input: $input) {
                                            post { id url title }
                                        }
                                    }
                                """,
                                "variables": {
                                    "input": {
                                        "title": clean_blog.get('title', f"SEO Guide: {topic}"),
                                        "contentMarkdown": full_content,
                                        "publicationId": pub_id,
                                        "tags": [{"name": t} for t in clean_blog.get('tags', [])[:5]]
                                    }
                                }
                            }
                            pub_resp = requests.post("https://gql.hashnode.com",
                                                     headers=headers, json=mutation, timeout=30)
                            if pub_resp.status_code == 200:
                                pub_data = pub_resp.json()
                                post = pub_data.get('data', {}).get('publishPost', {}).get('post', {})
                                results['platforms']['hashnode'] = {
                                    'success': True,
                                    'url': post.get('url', ''),
                                    'id': post.get('id', ''),
                                    'platform': 'Hashnode'
                                }
                            else:
                                results['platforms']['hashnode'] = {
                                    'success': False, 'error': pub_resp.text[:200], 'platform': 'Hashnode'
                                }
                        else:
                            results['platforms']['hashnode'] = {
                                'success': False,
                                'error': 'No Hashnode blog found. Create one at hashnode.com first.',
                                'platform': 'Hashnode'
                            }
                    except Exception as hfe:
                        results['platforms']['hashnode'] = {'success': False, 'error': str(hfe), 'platform': 'Hashnode'}
            else:
                results['platforms']['hashnode'] = {'success': False, 'error': 'HASHNODE_API_KEY not configured'}

        return results
    except Exception as e:
        logger.error(f"run_autopost_publish error: {e}")
        return {'success': False, 'error': str(e), 'topic': topic}


async def run_autopost(topic: str, platforms: list) -> dict:
    """Backward-compatible autopost: generate preview then publish immediately."""
    preview = await run_autopost_preview(topic)
    if not preview.get('success'):
        return preview
    return await run_autopost_publish(topic, platforms, preview.get('blog_content', {}))


# ─────────────────────────────────────────────
#  PDF REPORT
# ─────────────────────────────────────────────

async def generate_pdf(topic: str) -> dict:
    """Generate PDF SEO report"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import inch

        pdf_dir = os.path.join(REPORTS_DIR, 'pdf')
        os.makedirs(pdf_dir, exist_ok=True)
        fname = f"seo_report_{topic[:15].replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        fpath = os.path.join(pdf_dir, fname)

        doc = SimpleDocTemplate(fpath, pagesize=A4,
                                 rightMargin=0.75*inch, leftMargin=0.75*inch,
                                 topMargin=1*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()
        story = []

        # Title — Decentrawood branded
        title_style = ParagraphStyle('Title', parent=styles['Title'],
                                      fontSize=24, textColor=colors.HexColor('#1a1a2e'),
                                      spaceAfter=6)
        brand_style = ParagraphStyle('Brand', parent=styles['Normal'],
                                      fontSize=10, textColor=colors.HexColor('#4f46e5'),
                                      spaceAfter=2)
        story.append(Paragraph("Decentrawood — SEO Automation Report", title_style))
        story.append(Paragraph(
            "Web3 Entertainment Ecosystem | DEOD Token | DEODHunt | D-Nexus Metaverse",
            brand_style
        ))
        story.append(Paragraph(f"Topic: {topic}", styles['Heading2']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4f46e5')))
        story.append(Spacer(1, 0.2*inch))

        # Run all phases to get data
        kw_data = await run_keyword_research(topic)
        perf_data = await run_performance_report(topic)

        # Keywords section
        story.append(Paragraph("Keyword Research", styles['Heading1']))
        if kw_data.get('keywords'):
            kw_table_data = [['Keyword', 'Volume Est.', 'Difficulty', 'Intent', 'Priority']]
            for kw in kw_data['keywords']:
                kw_table_data.append([
                    kw.get('keyword', ''),
                    str(kw.get('search_volume_estimate', 0)),
                    str(kw.get('difficulty', 0)),
                    kw.get('intent', ''),
                    str(kw.get('priority_score', 0))
                ])
            kw_table = Table(
                kw_table_data,
                colWidths=[2.2*inch, 1*inch, 0.9*inch, 1.2*inch, 0.9*inch],
                repeatRows=1
            )
            kw_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f7ff'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(kw_table)
        story.append(Spacer(1, 0.2*inch))

        # Performance KPIs
        story.append(Paragraph("Performance KPIs", styles['Heading1']))
        if perf_data.get('kpis'):
            kpi_data = [['Metric', 'Value', 'Change', 'Trend']]
            for kpi in perf_data['kpis'][:8]:
                kpi_data.append([
                    kpi.get('metric', ''), kpi.get('value', ''),
                    kpi.get('change', ''), kpi.get('trend', '')
                ])
            kpi_table = Table(kpi_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.2*inch])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f7ff'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(kpi_table)

        # Insights
        if perf_data.get('insights'):
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Key Insights", styles['Heading1']))
            for insight in perf_data['insights']:
                story.append(Paragraph(f"• {insight}", styles['Normal']))

        # Next Actions
        if perf_data.get('next_actions'):
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Recommended Actions", styles['Heading1']))
            for action in perf_data['next_actions']:
                story.append(Paragraph(f"✓ {action}", styles['Normal']))

        doc.build(story)
        return {'success': True, 'pdf_path': fpath, 'filename': fname}

    except Exception as e:
        logger.error(f"generate_pdf error: {e}")
        return {'success': False, 'error': str(e)}


# ─────────────────────────────────────────────
#  FULL AUTOMATION
# ─────────────────────────────────────────────

async def run_full_seo(topic: str) -> dict:
    """Run complete SEO automation pipeline"""
    try:
        results = {
            'topic': topic,
            'phases': {},
            'timestamp': datetime.now().isoformat()
        }

        results['phases']['research'] = await run_keyword_research(topic)
        results['phases']['technical'] = await run_technical_audit(topic)
        results['phases']['backlinks'] = await run_backlink_strategy(topic)
        results['phases']['performance'] = await run_performance_report(topic)

        pdf_result = await generate_pdf(topic)
        results['phases']['pdf'] = pdf_result

        results['success'] = True
        results['summary'] = (
            f"✅ Full SEO automation complete for '{topic}'. "
            f"Found {len(results['phases']['research'].get('keywords', []))} keywords. "
            f"PDF report generated."
        )
        return results

    except Exception as e:
        logger.error(f"run_full_seo error: {e}")
        return {'success': False, 'error': str(e), 'topic': topic}
