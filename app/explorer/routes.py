# app/explorer/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.rule import RuleTable
from app.models.fact import FactTable
from app.models.tag import TagTable
from app.models.mood import MoodTable
from app.models.go_with import GoWithTable
from app.services.expert_system import recommend_locations

explorer_bp = Blueprint('explorer', __name__, url_prefix='')


def _normalize(values):
    return {str(v).strip().lower() for v in values if str(v).strip()}


def _load_options(model):
    return [item.name.strip() for item in model.query.order_by(model.name.asc()).all() if item.name and item.name.strip()]


@explorer_bp.route('/')
def index():
    query_raw = request.args.get('query', '').strip()
    query = query_raw.lower()

    selected_tags = _normalize(request.args.getlist('tags'))
    selected_moods = _normalize(request.args.getlist('moods'))
    selected_budgets = _normalize(request.args.getlist('budgets'))
    selected_go_with = _normalize(request.args.getlist('go_with'))

    rules_db = RuleTable.query.order_by(RuleTable.id.asc()).all()
    rules = [r.to_dict() for r in rules_db]

    if query:
        rules = [
            r for r in rules
            if query in str(r.get('location_name', '')).lower()
            or query in str(r.get('province_name', '')).lower()
            or query in str(r.get('explanation', '')).lower()
        ]

    has_filters = bool(selected_tags or selected_moods or selected_go_with or selected_budgets)

    scored_rules = []
    for r in rules:
        r_tags = _normalize(r.get('tags', []))
        r_moods = _normalize(r.get('moods', []))
        r_go_with = _normalize(r.get('go_with', []))
        r_budget = str(r.get('budget', '')).strip().lower()

        matched_t = len(r_tags & selected_tags)
        matched_m = len(r_moods & selected_moods)
        matched_g = len(r_go_with & selected_go_with)
        matched_b = 1 if (selected_budgets and r_budget in selected_budgets) else 0

        selected_total = len(selected_tags) + len(selected_moods) + len(selected_go_with) + len(selected_budgets)
        matched_total = matched_t + matched_m + matched_g + matched_b
        score_percent = round((matched_total / selected_total) * 100, 1) if selected_total else None

        scored_rules.append({
            **r,
            'matched_count': matched_total,
            'selected_count': selected_total,
            'match_percent': score_percent
        })

    if has_filters:
        rules = [r for r in scored_rules if r['matched_count'] > 0]
        rules.sort(key=lambda item: (item.get('match_percent', 0), item.get('matched_count', 0)), reverse=True)
    else:
        rules = scored_rules

    tag_options = _load_options(TagTable)
    mood_options = _load_options(MoodTable)
    go_with_options = _load_options(GoWithTable)
    budget_options = ['low', 'medium', 'high']

    return render_template(
        'explorer/index.html',
        rules=rules,
        query=query_raw,
        tag_options=tag_options,
        mood_options=mood_options,
        go_with_options=go_with_options,
        budget_options=budget_options,
        selected_tags=selected_tags,
        selected_moods=selected_moods,
        selected_go_with=selected_go_with,
        selected_budgets=selected_budgets,
    )


@explorer_bp.route('/recommend', methods=['GET', 'POST'])
def recommend():
    from flask import current_app
    result = {'items': [], 'is_exact': False, 'message': None}
    has_searched = False
    expression_text = ""
    uploaded_img_name = None
    image_url = ""

    if request.method == 'POST' or request.args.get('searched') or request.args.get('expression') or request.args.get('image_url'):
        has_searched = True
        expression_text = request.form.get('expression_text') or request.args.get('expression') or ""
        image_url = request.form.get('image_url') or request.args.get('image_url') or ""
        
        image_file = request.files.get('expression_image')
        if image_file and image_file.filename:
            from app.admin.routes import _save_uploaded_image
            uploaded_img_name, _ = _save_uploaded_image(image_file)

        from app.services.expert_system import recommend_by_expression
        result = recommend_by_expression(expression_text, uploaded_img_name or image_url)

    has_gemini_key = bool(current_app.config.get('GEMINI_API_KEY'))

    return render_template(
        'explorer/recommend.html',
        expression_text=expression_text,
        uploaded_img_name=uploaded_img_name,
        image_url=image_url,
        google_lens_url=result.get('google_lens_url'),
        recommendations=result.get('items', []),
        is_exact=result.get('is_exact', False),
        apology_message=result.get('message'),
        has_searched=has_searched,
        is_gemini_powered=result.get('is_gemini_powered', False),
        ai_advice_summary=result.get('ai_advice_summary'),
        image_analysis=result.get('image_analysis'),
        has_gemini_key=has_gemini_key,
    )



@explorer_bp.route('/location/<int:rule_id>')
def location_detail(rule_id):
    rule_obj = RuleTable.query.get(rule_id)
    if not rule_obj:
        flash('Location not found', 'danger')
        return redirect(url_for('explorer.index'))

    rule = rule_obj.to_dict()
    key = str(rule.get('location_name') or '').strip().lower()

    facts_db = FactTable.query.all()
    related_facts = [
        f.to_dict() for f in facts_db
        if str(f.location_name or '').strip().lower() == key
    ]

    return render_template('explorer/detail.html', rule=rule, related_facts=related_facts)
