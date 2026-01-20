from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.models import Requirement


def mark_as_confirmed(modeladmin, request, queryset):
    updated = queryset.update(status='Confirmed', reviewed_by=request.user.username)
    messages.success(request, _(f'成功将 {updated} 条需求标记为已确认。'))
mark_as_confirmed.short_description = _('标记为已确认')


def mark_as_expired(modeladmin, request, queryset):
    updated = queryset.update(status='Expired')
    messages.success(request, _(f'成功将 {updated} 条需求标记为已过期。'))
mark_as_expired.short_description = _('标记为已过期')


def mark_as_pending_review(modeladmin, request, queryset):
    updated = queryset.update(status='PendingReview')
    messages.success(request, _(f'成功将 {updated} 条需求标记为待审核。'))
mark_as_pending_review.short_description = _('标记为待审核')


def mark_as_template(modeladmin, request, queryset):
    updated = queryset.update(is_template=True)
    messages.success(request, _(f'成功将 {updated} 条需求标记为模板。'))
mark_as_template.short_description = _('标记为模板')


def unmark_as_template(modeladmin, request, queryset):
    updated = queryset.update(is_template=False)
    messages.success(request, _(f'成功取消 {updated} 条需求的模板标记。'))
unmark_as_template.short_description = _('取消模板标记')


def set_reviewer(modeladmin, request, queryset):
    reviewer = request.user.username
    updated = queryset.update(reviewed_by=reviewer)
    messages.success(request, _(f'成功将 {updated} 条需求的审核人设置为 {reviewer}。'))
set_reviewer.short_description = _('设置当前用户为审核人')


def clear_reviewer(modeladmin, request, queryset):
    updated = queryset.update(reviewed_by=None)
    messages.success(request, _(f'成功清除 {updated} 条需求的审核人。'))
clear_reviewer.short_description = _('清除审核人')


def copy_as_template(modeladmin, request, queryset):
    count = 0
    for obj in queryset:
        obj.pk = None
        obj.requirement_id = f"{obj.requirement_id}_copy_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        obj.is_template = True
        obj.status = 'PendingReview'
        obj.save()
        count += 1
    messages.success(request, _(f'成功复制 {count} 条需求作为模板。'))
copy_as_template.short_description = _('复制为模板')


def delete_selected_with_confirmation(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    messages.success(request, _(f'成功删除 {count} 条需求记录。'))
delete_selected_with_confirmation.short_description = _('删除选中的需求')
