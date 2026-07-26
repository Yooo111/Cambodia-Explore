# app/admin/routes.py
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from app.models.user import UserTable
from app.models.role import RoleTable
from app.models.permission import PermissionTable
from app.models.rule import RuleTable
from app.models.fact import FactTable
from app.models.tag import TagTable
from app.models.mood import MoodTable
from app.models.go_with import GoWithTable
from app.models.taxonomy import TaxonomyTable
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.permission_service import PermissionService
from app.forms.user_forms import UserCreateForm, UserEditForm, UserConfirmDeleteForm
from app.forms.role_forms import RoleCreateForm, RoleEditForm, RoleConfirmDeleteForm
from app.forms.permission_forms import PermissionCreateForm, PermissionEditForm, PermissionConfirmDeleteForm
from app.schemas.schema import validate_rule_payload, validate_fact_payload, validate_taxonomy_payload

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def _parse_list(field_name):
    return [v.strip() for v in request.form.getlist(field_name) if v.strip()]


def _save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename:
        return "", None
    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return "", "Image must be jpg, jpeg, png, or webp"
    filename = f"{uuid.uuid4().hex}.{extension}"
    upload_folder = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, filename))
    return filename, None


@admin_bp.route('/')
@login_required
def dashboard():
    metrics = {
        'total_users': UserTable.query.count(),
        'total_roles': RoleTable.query.count(),
        'total_permissions': PermissionTable.query.count(),
        'total_rules': RuleTable.query.count(),
        'total_facts': FactTable.query.count(),
        'total_tags': TagTable.query.count(),
        'total_moods': MoodTable.query.count(),
        'total_go_with': GoWithTable.query.count(),
        'total_taxonomy': TaxonomyTable.query.count(),
    }
    return render_template('admin/dashboard.html', metrics=metrics)


# ==================== USERS ====================
@admin_bp.route('/users')
@login_required
def users_index():
    users = UserService.get_user_all()
    return render_template('admin/users/index.html', users=users)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def users_create():
    form = UserCreateForm()
    if form.validate_on_submit():
        data = {
            "username": form.username.data,
            "email": form.email.data,
            "full_name": form.full_name.data,
            "is_active": form.is_active.data,
        }
        password = form.password.data
        role_id = form.role_id.data or None
        user = UserService.create_user(data, password, role_id)
        flash(f"User '{user.username}' created successfully.", "success")
        return redirect(url_for('admin.users_index'))
    return render_template('admin/users/create.html', form=form)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def users_edit(user_id):
    user = UserService.get_user_by_id(user_id)
    if not user:
        abort(404)
    form = UserEditForm(original_user=user, obj=user)
    if form.validate_on_submit():
        data = {
            "username": form.username.data,
            "email": form.email.data,
            "full_name": form.full_name.data,
            "is_active": form.is_active.data,
        }
        password = form.password.data or None
        role_id = form.role_id.data or None
        UserService.update_user(user, data, password, role_id)
        flash(f"User '{user.username}' updated successfully.", "success")
        return redirect(url_for('admin.users_index'))
    return render_template('admin/users/edit.html', form=form, user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['GET', 'POST'])
@login_required
def users_delete(user_id):
    user = UserService.get_user_by_id(user_id)
    if not user:
        abort(404)
    if request.method == 'POST':
        UserService.delete_user(user)
        flash("User deleted successfully.", "success")
        return redirect(url_for('admin.users_index'))
    form = UserConfirmDeleteForm()
    return render_template('admin/users/delete_confirm.html', user=user, form=form)


# ==================== ROLES ====================
@admin_bp.route('/roles')
@login_required
def roles_index():
    roles = RoleService.get_role_all()
    return render_template('admin/roles/index.html', roles=roles)


@admin_bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
def roles_create():
    form = RoleCreateForm()
    if form.validate_on_submit():
        data = {"name": form.name.data, "description": form.description.data}
        permission_ids = form.permission_ids.data or []
        role = RoleService.create_role(data, permission_ids)
        flash(f"Role '{role.name}' created successfully.", "success")
        return redirect(url_for('admin.roles_index'))
    return render_template('admin/roles/create.html', form=form)


@admin_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
def roles_edit(role_id):
    role = RoleService.get_role_by_id(role_id)
    if not role:
        abort(404)
    form = RoleEditForm(original_role=role, obj=role)
    if form.validate_on_submit():
        data = {"name": form.name.data, "description": form.description.data}
        permission_ids = form.permission_ids.data or []
        RoleService.update_role(role, data, permission_ids)
        flash(f"Role '{role.name}' updated successfully.", "success")
        return redirect(url_for('admin.roles_index'))
    return render_template('admin/roles/edit.html', form=form, role=role)


@admin_bp.route('/roles/<int:role_id>/delete', methods=['GET', 'POST'])
@login_required
def roles_delete(role_id):
    role = RoleService.get_role_by_id(role_id)
    if not role:
        abort(404)
    if request.method == 'POST':
        RoleService.delete_role(role)
        flash("Role deleted successfully.", "success")
        return redirect(url_for('admin.roles_index'))
    form = RoleConfirmDeleteForm()
    return render_template('admin/roles/delete_confirm.html', role=role, form=form)


# ==================== PERMISSIONS ====================
@admin_bp.route('/permissions')
@login_required
def permissions_index():
    permissions = PermissionService.get_permission_all()
    return render_template('admin/permissions/index.html', permissions=permissions)


@admin_bp.route('/permissions/create', methods=['GET', 'POST'])
@login_required
def permissions_create():
    form = PermissionCreateForm()
    if form.validate_on_submit():
        data = {
            "code": form.code.data,
            "name": form.name.data,
            "module": form.module.data,
            "description": form.description.data,
        }
        perm = PermissionService.create_permission(data)
        flash(f"Permission '{perm.name}' created successfully.", "success")
        return redirect(url_for('admin.permissions_index'))
    return render_template('admin/permissions/create.html', form=form)


@admin_bp.route('/permissions/<int:permission_id>/edit', methods=['GET', 'POST'])
@login_required
def permissions_edit(permission_id):
    perm = PermissionService.get_permission_by_id(permission_id)
    if not perm:
        abort(404)
    form = PermissionEditForm(original_permission=perm, obj=perm)
    if form.validate_on_submit():
        data = {
            "code": form.code.data,
            "name": form.name.data,
            "module": form.module.data,
            "description": form.description.data,
        }
        PermissionService.update_permission(perm, data)
        flash(f"Permission '{perm.name}' updated successfully.", "success")
        return redirect(url_for('admin.permissions_index'))
    return render_template('admin/permissions/edit.html', form=form, permission=perm)


@admin_bp.route('/permissions/<int:permission_id>/delete', methods=['GET', 'POST'])
@login_required
def permissions_delete(permission_id):
    perm = PermissionService.get_permission_by_id(permission_id)
    if not perm:
        abort(404)
    if request.method == 'POST':
        PermissionService.delete_permission(perm)
        flash("Permission deleted successfully.", "success")
        return redirect(url_for('admin.permissions_index'))
    form = PermissionConfirmDeleteForm()
    return render_template('admin/permissions/delete_confirm.html', permission=perm, form=form)


# ==================== RULES ====================
@admin_bp.route('/rules')
@login_required
def rules_index():
    rules = [r.to_dict() for r in RuleTable.query.order_by(RuleTable.id.asc()).all()]
    return render_template('admin/rules/index.html', rules=rules)


@admin_bp.route('/rules/create', methods=['GET', 'POST'])
@login_required
def rules_create():
    tags = [t.to_dict() for t in TagTable.query.order_by(TagTable.name.asc()).all()]
    moods = [m.to_dict() for m in MoodTable.query.order_by(MoodTable.name.asc()).all()]
    go_withs = [g.to_dict() for g in GoWithTable.query.order_by(GoWithTable.name.asc()).all()]
    if request.method == 'POST':
        candidate = {
            'name': request.form.get('rule_name', ''),
            'location_name': request.form.get('location_name', ''),
            'province_name': request.form.get('province_name', ''),
            'budget': request.form.get('budget', ''),
            'is_active': request.form.get('is_active', ''),
            'image': '',
            'explanation': request.form.get('rule_explanation', ''),
            'tags': _parse_list('tags'),
            'moods': _parse_list('moods'),
            'go_with': _parse_list('go_with')
        }
        normalized, errors = validate_rule_payload(candidate)
        if errors:
            flash(errors[0], 'danger')
            return render_template('admin/rules/create.html', rule=normalized, tags=tags, moods=moods, go_withs=go_withs)
        
        uploaded_files = request.files.getlist('image_files') or [request.files.get('image_file')]
        saved_images = []
        for file_item in uploaded_files:
            if file_item and file_item.filename:
                img_name, img_err = _save_uploaded_image(file_item)
                if img_err:
                    flash(img_err, 'danger')
                    return render_template('admin/rules/create.html', rule=normalized, tags=tags, moods=moods, go_withs=go_withs)
                if img_name:
                    saved_images.append(img_name)

        final_image_str = ", ".join(saved_images) if saved_images else ""

        rule = RuleTable(
            name=normalized.get('name', ''),
            location_name=normalized['location_name'],
            province_name=normalized['province_name'],
            budget=normalized['budget'],
            is_active=normalized['is_active'],
            image=final_image_str,
            explanation=normalized.get('explanation', '')
        )
        rule.tags = normalized.get('tags', [])
        rule.moods = normalized.get('moods', [])
        rule.go_with = normalized.get('go_with', [])
        db.session.add(rule)
        db.session.commit()
        flash('Rule created successfully', 'success')
        return redirect(url_for('admin.rules_index'))
    return render_template('admin/rules/create.html', rule=None, tags=tags, moods=moods, go_withs=go_withs)


@admin_bp.route('/rules/<int:rule_id>/edit', methods=['GET', 'POST'])
@login_required
def rules_edit(rule_id):
    tags = [t.to_dict() for t in TagTable.query.order_by(TagTable.name.asc()).all()]
    moods = [m.to_dict() for m in MoodTable.query.order_by(MoodTable.name.asc()).all()]
    go_withs = [g.to_dict() for g in GoWithTable.query.order_by(GoWithTable.name.asc()).all()]
    rule = RuleTable.query.get(rule_id)
    if not rule:
        abort(404)
    if request.method == 'POST':
        existing_imgs = rule.images_list
        remove_imgs = request.form.getlist('remove_images')
        kept_imgs = [img for img in existing_imgs if img not in remove_imgs]

        candidate = {
            'name': request.form.get('rule_name', ''),
            'location_name': request.form.get('location_name', ''),
            'province_name': request.form.get('province_name', ''),
            'budget': request.form.get('budget', ''),
            'is_active': request.form.get('is_active', ''),
            'image': ", ".join(kept_imgs),
            'explanation': request.form.get('rule_explanation', ''),
            'tags': _parse_list('tags'),
            'moods': _parse_list('moods'),
            'go_with': _parse_list('go_with')
        }
        normalized, errors = validate_rule_payload(candidate)
        if errors:
            flash(errors[0], 'danger')
            return render_template('admin/rules/edit.html', rule={'id': rule_id, **normalized}, tags=tags, moods=moods, go_withs=go_withs)

        uploaded_files = request.files.getlist('image_files') or [request.files.get('image_file')]
        new_saved = []
        for file_item in uploaded_files:
            if file_item and file_item.filename:
                img_name, img_err = _save_uploaded_image(file_item)
                if img_err:
                    flash(img_err, 'danger')
                    return render_template('admin/rules/edit.html', rule={'id': rule_id, **normalized}, tags=tags, moods=moods, go_withs=go_withs)
                if img_name:
                    new_saved.append(img_name)

        all_imgs = kept_imgs + new_saved
        rule.name = normalized.get('name', '')
        rule.location_name = normalized['location_name']
        rule.province_name = normalized['province_name']
        rule.budget = normalized['budget']
        rule.is_active = normalized['is_active']
        rule.explanation = normalized.get('explanation', '')
        rule.tags = normalized.get('tags', [])
        rule.moods = normalized.get('moods', [])
        rule.go_with = normalized.get('go_with', [])
        rule.image = ", ".join(all_imgs) if all_imgs else ""
        db.session.commit()
        flash('Rule updated successfully', 'success')
        return redirect(url_for('admin.rules_index'))
    return render_template('admin/rules/edit.html', rule=rule.to_dict(), tags=tags, moods=moods, go_withs=go_withs)



@admin_bp.route('/rules/<int:rule_id>/delete', methods=['GET', 'POST'])
@login_required
def rules_delete(rule_id):
    rule = RuleTable.query.get(rule_id)
    if not rule:
        abort(404)
    if request.method == 'POST':
        db.session.delete(rule)
        db.session.commit()
        flash('Rule deleted successfully', 'success')
        return redirect(url_for('admin.rules_index'))
    return render_template('admin/rules/delete.html', rule=rule.to_dict())


# ==================== FACTS ====================
@admin_bp.route('/facts')
@login_required
def facts_index():
    facts = [f.to_dict() for f in FactTable.query.all()]
    return render_template('admin/facts/index.html', facts=facts)


@admin_bp.route('/facts/create', methods=['GET', 'POST'])
@login_required
def facts_create():
    if request.method == 'POST':
        normalized, errors = validate_fact_payload({
            'location_name': request.form.get('location_name', ''),
            'description': request.form.get('fact_description', ''),
        })
        if errors:
            flash(errors[0], 'danger')
            return render_template('admin/facts/create.html', fact=normalized)
        fact = FactTable(location_name=normalized['location_name'], description=normalized['description'])
        db.session.add(fact)
        db.session.commit()
        flash('Fact created successfully', 'success')
        return redirect(url_for('admin.facts_index'))
    return render_template('admin/facts/create.html', fact=None)


@admin_bp.route('/facts/<int:fact_id>/edit', methods=['GET', 'POST'])
@login_required
def facts_edit(fact_id):
    fact = FactTable.query.get(fact_id)
    if not fact:
        abort(404)
    if request.method == 'POST':
        normalized, errors = validate_fact_payload({
            'location_name': request.form.get('location_name', ''),
            'description': request.form.get('fact_description', ''),
        })
        if errors:
            flash(errors[0], 'danger')
            return render_template('admin/facts/edit.html', fact={'id': fact_id, **normalized})
        fact.location_name = normalized['location_name']
        fact.description = normalized['description']
        db.session.commit()
        flash('Fact updated successfully', 'success')
        return redirect(url_for('admin.facts_index'))
    return render_template('admin/facts/edit.html', fact=fact.to_dict())


@admin_bp.route('/facts/<int:fact_id>/delete', methods=['GET', 'POST'])
@login_required
def facts_delete(fact_id):
    fact = FactTable.query.get(fact_id)
    if not fact:
        abort(404)
    if request.method == 'POST':
        db.session.delete(fact)
        db.session.commit()
        flash('Fact deleted successfully', 'success')
        return redirect(url_for('admin.facts_index'))
    return render_template('admin/facts/delete.html', fact=fact.to_dict())


# ==================== TAXONOMY ====================
@admin_bp.route('/taxonomy')
@login_required
def taxonomy_index():
    taxonomy = [t.to_dict() for t in TaxonomyTable.query.order_by(TaxonomyTable.id.asc()).all()]
    return render_template('admin/taxonomy/index.html', taxonomy=taxonomy)


@admin_bp.route('/taxonomy/create', methods=['GET', 'POST'])
@login_required
def taxonomy_create():
    if request.method == 'POST':
        normalized, errors = validate_taxonomy_payload({
            'name': request.form.get('name', ''),
            'type': request.form.get('type', ''),
            'description': request.form.get('description', ''),
        })
        if errors:
            flash(errors[0], 'danger')
            return render_template('admin/taxonomy/create.html', item=normalized)
        tax = TaxonomyTable(name=normalized['name'], type=normalized['type'], description=normalized['description'])
        db.session.add(tax)
        db.session.commit()
        flash('Taxonomy created successfully', 'success')
        return redirect(url_for('admin.taxonomy_index'))
    return render_template('admin/taxonomy/create.html', item=None)


@admin_bp.route('/taxonomy/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def taxonomy_edit(item_id):
    tax = TaxonomyTable.query.get(item_id)
    if not tax:
        abort(404)
    if request.method == 'POST':
        normalized, errors = validate_taxonomy_payload({
            'name': request.form.get('name', ''),
            'type': request.form.get('type', ''),
            'description': request.form.get('description', ''),
        })
        if errors:
            flash(errors[0], 'danger')
            return render_template('admin/taxonomy/edit.html', item={'id': item_id, **normalized})
        tax.name = normalized['name']
        tax.type = normalized['type']
        tax.description = normalized['description']
        db.session.commit()
        flash('Taxonomy updated successfully', 'success')
        return redirect(url_for('admin.taxonomy_index'))
    return render_template('admin/taxonomy/edit.html', item=tax.to_dict())


@admin_bp.route('/taxonomy/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def taxonomy_delete(item_id):
    tax = TaxonomyTable.query.get(item_id)
    if not tax:
        abort(404)
    if request.method == 'POST':
        db.session.delete(tax)
        db.session.commit()
        flash('Taxonomy deleted successfully', 'success')
        return redirect(url_for('admin.taxonomy_index'))
    return render_template('admin/taxonomy/delete.html', item=tax.to_dict())


# ==================== TAGS ====================
@admin_bp.route('/tags')
@login_required
def tags_index():
    tags = [t.to_dict() for t in TagTable.query.order_by(TagTable.id.asc()).all()]
    return render_template('admin/options/tags.html', tags=tags)


@admin_bp.route('/tags/create', methods=['POST'])
@login_required
def tags_create():
    name = request.form.get('name', '').strip()
    if name and not TagTable.query.filter_by(name=name).first():
        db.session.add(TagTable(name=name))
        db.session.commit()
        flash('Tag created successfully', 'success')
    return redirect(url_for('admin.tags_index'))


@admin_bp.route('/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def tags_delete(tag_id):
    tag = TagTable.query.get(tag_id)
    if tag:
        db.session.delete(tag)
        db.session.commit()
        flash('Tag deleted successfully', 'success')
    return redirect(url_for('admin.tags_index'))


# ==================== MOODS ====================
@admin_bp.route('/moods')
@login_required
def moods_index():
    moods = [m.to_dict() for m in MoodTable.query.order_by(MoodTable.id.asc()).all()]
    return render_template('admin/options/moods.html', moods=moods)


@admin_bp.route('/moods/create', methods=['POST'])
@login_required
def moods_create():
    name = request.form.get('name', '').strip()
    if name and not MoodTable.query.filter_by(name=name).first():
        db.session.add(MoodTable(name=name))
        db.session.commit()
        flash('Mood created successfully', 'success')
    return redirect(url_for('admin.moods_index'))


@admin_bp.route('/moods/<int:mood_id>/delete', methods=['POST'])
@login_required
def moods_delete(mood_id):
    mood = MoodTable.query.get(mood_id)
    if mood:
        db.session.delete(mood)
        db.session.commit()
        flash('Mood deleted successfully', 'success')
    return redirect(url_for('admin.moods_index'))


# ==================== GO WITH ====================
@admin_bp.route('/go_with')
@login_required
def go_with_index():
    go_withs = [g.to_dict() for g in GoWithTable.query.order_by(GoWithTable.id.asc()).all()]
    return render_template('admin/options/go_with.html', go_withs=go_withs)


@admin_bp.route('/go_with/create', methods=['POST'])
@login_required
def go_with_create():
    name = request.form.get('name', '').strip()
    if name and not GoWithTable.query.filter_by(name=name).first():
        db.session.add(GoWithTable(name=name))
        db.session.commit()
        flash('Go With created successfully', 'success')
    return redirect(url_for('admin.go_with_index'))


@admin_bp.route('/go_with/<int:go_with_id>/delete', methods=['POST'])
@login_required
def go_with_delete(go_with_id):
    gw = GoWithTable.query.get(go_with_id)
    if gw:
        db.session.delete(gw)
        db.session.commit()
        flash('Go With deleted successfully', 'success')
    return redirect(url_for('admin.go_with_index'))
