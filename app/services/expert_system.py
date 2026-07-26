import os
import re
import urllib.parse
from flask import current_app
from app.models.rule import RuleTable
from app.models.fact import FactTable
from app.models.tag import TagTable
from app.models.mood import MoodTable
from app.models.go_with import GoWithTable


def load_rules():
    return [rule.to_dict() for rule in RuleTable.query.all()]


def load_facts():
    return [fact.to_dict() for fact in FactTable.query.all()]


def load_options(file_name):
    if file_name in ('tags', 'tag'):
        return [tag.to_dict() for tag in TagTable.query.order_by(TagTable.name.asc()).all()]
    elif file_name in ('moods', 'mood'):
        return [mood.to_dict() for mood in MoodTable.query.order_by(MoodTable.name.asc()).all()]
    elif file_name in ('go_with', 'go_withs'):
        return [gw.to_dict() for gw in GoWithTable.query.order_by(GoWithTable.name.asc()).all()]
    return []


def _normalize_list(values):
    if not values:
        return []
    if isinstance(values, str):
        values = values.split(',')
    normalized = []
    for value in values:
        cleaned = str(value).strip().lower()
        if cleaned:
            normalized.append(cleaned)
    return normalized


def recommend_by_expression(expression_text, uploaded_image=None):
    """
    Intelligent AI Recommendation Engine powered by Google Gemini API & rule-based expert fallback.
    """
    rules = load_rules()
    facts = load_facts()

    raw_text = (expression_text or "").strip().lower()
    raw_img_str = (uploaded_image or "").strip().lower()

    tokens = [t for t in re.findall(r'\w+', raw_text) if len(t) > 2]

    # Generate Google Lens / Reverse Image Search Link if user provided an image URL or filename
    google_lens_url = None
    if uploaded_image and (uploaded_image.startswith('http://') or uploaded_image.startswith('https://')):
        encoded_img_url = urllib.parse.quote(uploaded_image)
        google_lens_url = f"https://lens.google.com/uploadbyurl?url={encoded_img_url}"
    elif uploaded_image:
        encoded_query = urllib.parse.quote(f"{raw_text} Cambodia travel destination")
        google_lens_url = f"https://www.google.com/search?tbm=isch&q={encoded_query}"

    # Check for Gemini API key configuration
    api_key = None
    model_name = "gemini-2.5-flash"
    try:
        api_key = current_app.config.get('GEMINI_API_KEY')
        model_name = current_app.config.get('GEMINI_MODEL', 'gemini-2.5-flash')
    except Exception:
        api_key = os.environ.get('GEMINI_API_KEY')

    # Resolve local image path if available for multimodal analysis
    abs_img_path = None
    if uploaded_image and not (uploaded_image.startswith('http://') or uploaded_image.startswith('https://')):
        try:
            abs_img_path = os.path.join(current_app.root_path, 'static', 'uploads', uploaded_image)
        except Exception:
            pass

    if api_key and (expression_text or uploaded_image):
        from app.services.gemini_service import recommend_with_gemini
        gemini_res = recommend_with_gemini(
            expression_text=expression_text,
            uploaded_image_path=abs_img_path,
            rules=rules,
            facts=facts,
            api_key=api_key,
            model_name=model_name
        )
        if gemini_res.get('success'):
            gemini_res['is_gemini_powered'] = True
            gemini_res['google_lens_url'] = google_lens_url
            return gemini_res
        else:
            print(f"[Expert System] Gemini API fallback reason: {gemini_res.get('error')}")


    grouped_facts = {}
    for fact in facts:
        location_name = str(fact.get('location_name', '')).strip()
        if not location_name:
            continue
        grouped_facts.setdefault(location_name.lower(), []).append(str(fact.get('description', '')).strip())

    scored_list = []
    for rule in rules:
        location_name = str(rule.get('location_name', '')).strip()
        province_name = str(rule.get('province_name', '')).strip()
        if not location_name:
            continue

        rule_tags = _normalize_list(rule.get('tags', []))
        rule_moods = _normalize_list(rule.get('moods', []))
        rule_go_with = _normalize_list(rule.get('go_with', []))
        rule_explanation = str(rule.get('explanation', '')).lower()
        rule_budget = str(rule.get('budget', '')).lower()

        matched_terms = set()

        for token in tokens:
            if token in location_name.lower():
                matched_terms.add(f"Location '{location_name}'")
            if token in province_name.lower():
                matched_terms.add(f"Province '{province_name}'")
            if token in rule_budget:
                matched_terms.add(f"Budget '{rule_budget}'")
            if any(token in tag for tag in rule_tags):
                matched_terms.add(f"Tag match")
            if any(token in mood for mood in rule_moods):
                matched_terms.add(f"Mood match")
            if any(token in gw for gw in rule_go_with):
                matched_terms.add(f"Partner match")
            if token in rule_explanation:
                matched_terms.add("Highlight context")

        base_match_count = len(matched_terms)
        
        image_bonus = 0
        if uploaded_image:
            raw_rule_img = str(rule.get('image', '')).strip()
            if raw_rule_img:
                image_bonus = 35

        calc_score = round(min(100.0, ((base_match_count * 25) + image_bonus)), 1)
        if not tokens and not uploaded_image:
            calc_score = 50.0

        # Generate Deep Global Knowledge Links for Google Maps, Wikipedia, Google Search
        gmaps_query = urllib.parse.quote(f"{location_name} {province_name} Cambodia")
        wiki_query = urllib.parse.quote(f"{location_name} Cambodia")
        google_query = urllib.parse.quote(f"{location_name} {province_name} Cambodia tourism guide")

        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={gmaps_query}"
        wikipedia_url = f"https://en.wikipedia.org/wiki/Special:Search?search={wiki_query}"
        google_search_url = f"https://www.google.com/search?q={google_query}"

        raw_img = str(rule.get('image', '')).strip()
        img_list = [i.strip() for i in raw_img.split(',') if i.strip()] if raw_img else []
        primary_img = img_list[0] if img_list else raw_img

        why_lines = []
        if matched_terms:
            why_lines.append(f"Expression matches: {', '.join(list(matched_terms)[:3])}")
        else:
            why_lines.append("Resembles top recommended Cambodian travel destinations")

        if uploaded_image:
            why_lines.append("Google Visual Match: Analyzed image with Google & database photos")

        rule_exp = str(rule.get('explanation', '')).strip()
        if rule_exp:
            why_lines.append(f"Highlight: {rule_exp}")

        scored_list.append({
            'id': rule.get('id'),
            'location_name': location_name,
            'province_name': province_name,
            'budget': str(rule.get('budget', '')).strip(),
            'image': primary_img,
            'images_list': img_list,
            'score': calc_score,
            'matched_count': base_match_count,
            'google_maps_url': google_maps_url,
            'wikipedia_url': wikipedia_url,
            'google_search_url': google_search_url,
            'google_lens_url': google_lens_url,
            'why': why_lines,
            'is_active': rule.get('is_active', True)
        })

    # Sort by score descending (Top match on top!)
    scored_list.sort(key=lambda rec: (rec['score'], rec['matched_count'], rec['location_name']), reverse=True)

    has_exact = any(item['score'] >= 75 for item in scored_list)
    
    matched_items = [item for item in scored_list if item['matched_count'] > 0 or item['score'] > 0]
    if not matched_items:
        matched_items = scored_list[:4]

    message = None
    if not has_exact and (expression_text or uploaded_image):
        message = "We apologize that no 100% exact match was found for your expression, but based on your description and image, here are the closest resembling destinations cross-referenced with Google Maps & Wikipedia!"

    return {
        'items': matched_items,
        'is_exact': has_exact,
        'message': message,
        'google_lens_url': google_lens_url
    }


def recommend_locations(selected_tags=None, selected_moods=None, selected_go_with=None):
    expression_parts = []
    if selected_tags:
        expression_parts.extend(selected_tags)
    if selected_moods:
        expression_parts.extend(selected_moods)
    if selected_go_with:
        expression_parts.extend(selected_go_with)
    expr_text = " ".join(expression_parts)
    return recommend_by_expression(expr_text)
