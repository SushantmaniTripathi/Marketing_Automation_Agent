"""
Digital Marketing Automation - Web Backend
Flask API server replacing Telegram bot interface
"""

import os
import sys
import json
import asyncio
import logging
import logging.handlers
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'Social_Agent'))
sys.path.insert(0, os.path.join(BASE_DIR, 'SEO_Agents'))

# Setup logging
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

file_handler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(LOG_DIR, 'app.log'),
    when='midnight', interval=1, backupCount=2, encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DMA_Web")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dma-secret-2024")
CORS(app)

# ─────────────────────────────────────────────
#  ROUTES — FRONTEND & AUTH
# ─────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def login():
    """Verify login credentials against .env"""
    try:
        data = request.json or {}
        username = data.get('username', '')
        password = data.get('password', '')
        
        env_username = os.getenv('ADMIN_USERNAME', 'ADMIN')
        env_password = os.getenv('ADMIN_PASSWORD', 'BIZ')
        
        if username == env_username and password == env_password:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'})
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/post/generated-image/<path:filename>')
def serve_generated_image(filename):
    """Serve generated images from Social_Agent/data/generated_images"""
    img_dir = os.path.join(BASE_DIR, 'Social_Agent', 'data', 'generated_images')
    return send_from_directory(img_dir, filename)


# ─────────────────────────────────────────────
#  POST AUTOMATION ENDPOINTS
# ─────────────────────────────────────────────

@app.route('/api/post/hashtags', methods=['POST'])
def get_hashtags():
    """Step 1: Generate hashtags from topic"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400

        from post_routes import generate_hashtags
        result = asyncio.run(generate_hashtags(topic))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Hashtag error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/post/trends', methods=['GET'])
def get_post_trends():
    """Step 1 helper: Fetch today's trend headlines/topics for Decentrawood niches"""
    try:
        from post_routes import get_trending_topics
        result = asyncio.run(get_trending_topics())
        return jsonify(result)
    except Exception as e:
        logger.error(f"Post trends error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/post/caption', methods=['POST'])
def get_caption():
    """Step 2: Generate caption"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400

        from post_routes import generate_caption
        result = asyncio.run(generate_caption(topic))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Caption error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/post/image', methods=['POST'])
def get_image():
    """Step 3: Generate AI image"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        old_image_path = data.get('old_image_path', None)  # for regenerate cleanup
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400

        from post_routes import generate_image
        result = asyncio.run(generate_image(topic, old_image_path))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Image gen error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/post/delete-image', methods=['DELETE'])
def delete_image():
    """Delete a generated image file from disk"""
    try:
        data = request.json
        image_path = data.get('image_path', '')
        if not image_path:
            return jsonify({'success': False, 'error': 'image_path required'}), 400
        # Safety: only allow deleting files inside Social_Agent/data/generated_images
        allowed_dir = os.path.realpath(os.path.join(BASE_DIR, 'Social_Agent', 'data', 'generated_images'))
        target = os.path.realpath(image_path)
        if not target.startswith(allowed_dir):
            return jsonify({'success': False, 'error': 'Path not allowed'}), 403
        if os.path.isfile(target):
            os.remove(target)
            logger.info(f"Deleted image: {target}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Delete image error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/post/publish', methods=['POST'])
def publish_post():
    """Step 4: Publish to Instagram"""
    try:
        data = request.json
        image_path = data.get('image_path')
        caption = data.get('caption', '')
        hashtags = data.get('hashtags', [])
        schedule_time = data.get('schedule_time')  # Optional ISO string

        if not image_path or not caption:
            return jsonify({'success': False, 'error': 'image_path and caption are required'}), 400

        from post_routes import publish_to_instagram
        result = asyncio.run(publish_to_instagram(image_path, caption, hashtags, schedule_time))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Publish error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ─────────────────────────────────────────────
#  SEO AUTOMATION ENDPOINTS
# ─────────────────────────────────────────────

@app.route('/api/seo/research', methods=['POST'])
def seo_research():
    """SEO Step: Keyword Research"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400

        from seo_routes import run_keyword_research
        result = asyncio.run(run_keyword_research(topic))
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO research error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seo/technical', methods=['POST'])
def seo_technical():
    """SEO Step: Technical Audit"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        from seo_routes import run_technical_audit
        result = asyncio.run(run_technical_audit(topic))
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO technical error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seo/backlinks', methods=['POST'])
def seo_backlinks():
    """SEO Step: Backlink Strategy"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        from seo_routes import run_backlink_strategy
        result = asyncio.run(run_backlink_strategy(topic))
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO backlinks error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seo/performance', methods=['POST'])
def seo_performance():
    """SEO Step: Performance Report"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        period = str(data.get('period', 'month')).strip().lower()
        if period not in {'month', 'year'}:
            period = 'month'
        from seo_routes import run_performance_report
        result = asyncio.run(run_performance_report(topic, period))
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO performance error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seo/autopost', methods=['POST'])
def seo_autopost():
    """SEO Step: Auto-Post to Dev.to & Hashnode"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        platforms = data.get('platforms', ['devto', 'hashnode'])
        from seo_routes import run_autopost
        result = asyncio.run(run_autopost(topic, platforms))
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO autopost error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seo/autopost/preview', methods=['POST'])
def seo_autopost_preview():
    """SEO Step: Generate blog draft for review before publishing"""
    try:
        data = request.json or {}
        topic = data.get('topic', '').strip()
        humanize = bool(data.get('humanize', False))
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400

        from seo_routes import run_autopost_preview
        result = asyncio.run(run_autopost_preview(topic, humanize=humanize))
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO autopost preview error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seo/autopost/publish', methods=['POST'])
def seo_autopost_publish():
    """SEO Step: Publish reviewed draft to selected platforms"""
    try:
        data = request.json or {}
        topic = data.get('topic', '').strip()
        platforms = data.get('platforms', ['devto', 'hashnode'])
        blog = data.get('blog', {})
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        if not isinstance(blog, dict) or not blog.get('title'):
            return jsonify({'success': False, 'error': 'Blog draft is required before publish'}), 400

        from seo_routes import run_autopost_publish
        result = asyncio.run(run_autopost_publish(topic, platforms, blog))
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO autopost publish error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seo/pdf', methods=['POST'])
def seo_pdf():
    """SEO Step: Generate PDF Report"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        from seo_routes import generate_pdf
        result = asyncio.run(generate_pdf(topic))
        if result.get('success') and result.get('pdf_path'):
            return send_file(result['pdf_path'], as_attachment=True,
                             download_name=f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO PDF error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/seo/full', methods=['POST'])
def seo_full():
    """SEO: Full automation pipeline"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        from seo_routes import run_full_seo
        result = asyncio.run(run_full_seo(topic))
        return jsonify(result)
    except Exception as e:
        logger.error(f"SEO full error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ─────────────────────────────────────────────
#  HEALTH CHECK
# ─────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    checks = {
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'ideogram': bool(os.getenv('IDEOGRAM_API_KEY')),
        'instagram': bool(os.getenv('INSTAGRAM_TOKEN_1')),
        'gsc': bool(os.getenv('GSC_SITE_URL')),
        'devto': bool(os.getenv('DEVTO_API_KEY')),
        'hashnode': bool(os.getenv('HASHNODE_API_KEY')),
    }
    return jsonify({'status': 'ok', 'services': checks})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    logger.info(f"🚀 DMA Web starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
