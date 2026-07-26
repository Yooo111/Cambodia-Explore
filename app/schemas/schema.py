BUDGET_CHOICES = {'low', 'medium', 'high'}


def normalize_text(value):
    return ' '.join(str(value or '').strip().split())


def _normalize_list(values):
    if not values:
        return []
    return [normalize_text(value) for value in values if normalize_text(value)]


def _to_bool(value):
    if isinstance(value, bool):
        return value
    text = normalize_text(value).lower()
    return text in {'1', 'true', 'yes', 'on'}


def validate_rule_payload(payload):
    data = {
        'name': normalize_text(payload.get('name')),
        'location_name': normalize_text(payload.get('location_name')),
        'province_name': normalize_text(payload.get('province_name')),
        'budget': normalize_text(payload.get('budget')).lower(),
        'is_active': _to_bool(payload.get('is_active', True)),
        'image': normalize_text(payload.get('image')),
        'explanation': normalize_text(payload.get('explanation')),
        'tags': _normalize_list(payload.get('tags', [])),
        'moods': _normalize_list(payload.get('moods', [])),
        'go_with': _normalize_list(payload.get('go_with', [])),
    }

    errors = []
    if not data['location_name']:
        errors.append('Location name is required')
    if not data['province_name']:
        errors.append('Province name is required')
    if data['budget'] not in BUDGET_CHOICES:
        errors.append('Budget must be low, medium, or high')
    if not (data['tags'] or data['moods'] or data['go_with']):
        errors.append('Select at least one condition (tag, mood, or go with)')

    return data, errors


def validate_fact_payload(payload):
    data = {
        'location_name': normalize_text(payload.get('location_name')),
        'description': normalize_text(payload.get('description')),
    }

    errors = []
    if not data['location_name']:
        errors.append('Location is required')
    if not data['description']:
        errors.append('Description is required')

    return data, errors


def validate_taxonomy_payload(payload):
    data = {
        'name': normalize_text(payload.get('name')),
        'type': normalize_text(payload.get('type')),
        'description': normalize_text(payload.get('description')),
    }

    errors = []
    if not data['name']:
        errors.append('Name is required')
    if not data['type']:
        errors.append('Type is required')

    return data, errors
