import os
import json
import re
from PIL import Image
import urllib.parse

def recommend_with_gemini(expression_text, uploaded_image_path, rules, facts, api_key, model_name="gemini-2.5-flash"):
    """
    Query Google Gemini API for intelligent Cambodian travel destination recommendations.
    Supports natural language analysis and multimodal image/photo input.
    """
    if not api_key:
        return {'success': False, 'error': 'GEMINI_API_KEY is not configured.'}

    # Format database rules & facts into structured grounding context for Gemini
    facts_by_location = {}
    for f in facts:
        loc = str(f.get('location_name', '')).strip().lower()
        if loc:
            desc = str(f.get('description', '')).strip()
            if desc:
                facts_by_location.setdefault(loc, []).append(desc)

    destinations_context = []
    rule_by_id = {}
    for r in rules:
        r_id = r.get('id')
        loc_name = str(r.get('location_name', '')).strip()
        prov_name = str(r.get('province_name', '')).strip()
        if not loc_name or not r_id:
            continue

        rule_by_id[r_id] = r

        loc_facts = facts_by_location.get(loc_name.lower(), [])
        dest_summary = (
            f"ID: {r_id} | Name: {loc_name} | Province: {prov_name} | "
            f"Budget: {r.get('budget', 'N/A')} | Tags: {', '.join(r.get('tags', []))} | "
            f"Moods: {', '.join(r.get('moods', []))} | Go With: {', '.join(r.get('go_with', []))} | "
            f"Explanation: {r.get('explanation', '')}"
        )
        if loc_facts:
            dest_summary += f" | Additional Facts: {' '.join(loc_facts[:2])}"

        destinations_context.append(dest_summary)

    formatted_destinations = "\n".join(destinations_context)

    # Build prompt
    prompt = f"""
You are the official Smart AI Travel Advisor for Cambodia Tourism.
Your task is to analyze the user's travel request and/or photo vibe, and recommend the best matching Cambodian destinations from the AVAILABLE DATABASE listed below.

AVAILABLE DATABASE DESTINATIONS:
{formatted_destinations}

USER QUERY / TRAVEL VIBE:
"{expression_text or 'Recommend the best travel destinations in Cambodia for me based on vibe and popularity.'}"

INSTRUCTIONS:
1. Examine the user's text and any provided image.
2. Select up to 4 best matching destinations from the AVAILABLE DATABASE DESTINATIONS by their exact integer ID.
3. Assign a match confidence score (percentage 50.0 to 100.0) for each recommendation based on how well it fits.
4. Provide a customized, concise reason ("why") for why each place is recommended.
5. Provide a warm, helpful paragraph of personalized AI advice ("ai_advice_summary").
6. If an image is provided, provide a short visual assessment ("image_analysis") describing the photo's vibe and how it matches Cambodia travel.

OUTPUT REQUIREMENT:
You MUST output ONLY a single valid JSON object with NO markdown wrapper, matching this exact structure:
{{
  "ai_advice_summary": "Your personalized travel advice paragraph...",
  "image_analysis": "Description of image vibe (or empty string if no image)...",
  "recommendations": [
    {{
      "id": 1,
      "score": 95.0,
      "why": "This destination offers..."
    }}
  ]
}}
"""

    contents = []

    # Handle image input if available
    img_obj = None
    if uploaded_image_path and os.path.exists(uploaded_image_path):
        try:
            img_obj = Image.open(uploaded_image_path)
            contents.append(img_obj)
        except Exception as e:
            print(f"[Gemini Service] Image opening error: {e}")

    contents.append(prompt)

    response_text = ""

    # Strategy 1: Try google-genai SDK first
    try:
        from google import genai
        try:
            client = genai.Client(
                api_key=api_key,
                http_options={'headers': {'User-Agent': 'aistudio-build'}}
            )
        except Exception:
            client = genai.Client(api_key=api_key)

        # Fall back to gemini-2.5-flash or gemini-1.5-flash if specified model fails
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            response_text = res.text
        except Exception as err:
            print(f"[Gemini Service] google-genai model {model_name} failed: {err}, trying fallback model gemini-1.5-flash")
            res = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents
            )
            response_text = res.text

    except ImportError:
        # Strategy 2: Fall back to google.generativeai SDK
        try:
            import google.generativeai as genai_old
            genai_old.configure(api_key=api_key)
            
            model = genai_old.GenerativeModel(model_name)
            res = model.generate_content(contents)
            response_text = res.text
        except Exception as err_old:
            return {'success': False, 'error': f"Gemini API call failed: {str(err_old)}"}
    except Exception as e:
        return {'success': False, 'error': f"Gemini API call failed: {str(e)}"}

    if not response_text:
        return {'success': False, 'error': 'Empty response from Gemini API.'}

    # Clean JSON output
    cleaned_json_str = response_text.strip()
    if cleaned_json_str.startswith("```json"):
        cleaned_json_str = cleaned_json_str[7:]
    if cleaned_json_str.startswith("```"):
        cleaned_json_str = cleaned_json_str[3:]
    if cleaned_json_str.endswith("```"):
        cleaned_json_str = cleaned_json_str[:-3]
    cleaned_json_str = cleaned_json_str.strip()

    try:
        data = json.loads(cleaned_json_str)
    except json.JSONDecodeError as json_err:
        # Match using regex if JSON parse failed
        print(f"[Gemini Service] JSON parse warning: {json_err}. Raw: {cleaned_json_str[:100]}...")
        match = re.search(r'\{.*\}', cleaned_json_str, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
            except Exception:
                return {'success': False, 'error': 'Could not parse Gemini JSON response.'}
        else:
            return {'success': False, 'error': 'Invalid format from Gemini.'}

    # Enrich recommendations with database rule fields
    items = []
    rec_list = data.get('recommendations', [])
    for rec in rec_list:
        r_id = rec.get('id')
        if not r_id:
            continue

        r = rule_by_id.get(int(r_id))
        if not r:
            continue

        loc_name = str(r.get('location_name', '')).strip()
        prov_name = str(r.get('province_name', '')).strip()
        score = float(rec.get('score', 75.0))
        why = rec.get('why', '')

        # Generate Google links
        gmaps_query = urllib.parse.quote(f"{loc_name} {prov_name} Cambodia")
        wiki_query = urllib.parse.quote(f"{loc_name} Cambodia")
        google_query = urllib.parse.quote(f"{loc_name} {prov_name} Cambodia tourism guide")

        raw_img = str(r.get('image', '')).strip()
        img_list = [i.strip() for i in raw_img.split(',') if i.strip()] if raw_img else []
        primary_img = img_list[0] if img_list else raw_img

        why_lines = [f"🤖 Gemini AI: {why}"] if why else [f"Matched by Gemini AI ({score}% match)"]

        items.append({
            'id': r.get('id'),
            'location_name': loc_name,
            'province_name': prov_name,
            'budget': str(r.get('budget', '')).strip(),
            'image': primary_img,
            'images_list': img_list,
            'score': round(score, 1),
            'matched_count': 1,
            'google_maps_url': f"https://www.google.com/maps/search/?api=1&query={gmaps_query}",
            'wikipedia_url': f"https://en.wikipedia.org/wiki/Special:Search?search={wiki_query}",
            'google_search_url': f"https://www.google.com/search?q={google_query}",
            'google_lens_url': None,
            'why': why_lines,
            'is_active': r.get('is_active', True)
        })

    items.sort(key=lambda x: x['score'], reverse=True)

    return {
        'success': True,
        'ai_advice_summary': data.get('ai_advice_summary', ''),
        'image_analysis': data.get('image_analysis', ''),
        'items': items,
        'is_exact': any(i['score'] >= 80 for i in items),
        'message': None
    }
