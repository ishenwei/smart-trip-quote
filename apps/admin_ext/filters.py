from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from apps.models import Requirement


class StatusFilter(SimpleListFilter):
    title = _('需求状态')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Requirement.Status.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class SourceTypeFilter(SimpleListFilter):
    title = _('需求来源')
    parameter_name = 'source_type'

    def lookups(self, request, model_admin):
        return Requirement.SourceType.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source_type=self.value())
        return queryset


class TransportationTypeFilter(SimpleListFilter):
    title = _('交通方式')
    parameter_name = 'transportation_type'

    def lookups(self, request, model_admin):
        return Requirement.TransportationType.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(transportation_type=self.value())
        return queryset


class HotelLevelFilter(SimpleListFilter):
    title = _('酒店等级')
    parameter_name = 'hotel_level'

    def lookups(self, request, model_admin):
        return Requirement.HotelLevel.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(hotel_level=self.value())
        return queryset


class TripRhythmFilter(SimpleListFilter):
    title = _('行程节奏')
    parameter_name = 'trip_rhythm'

    def lookups(self, request, model_admin):
        return Requirement.TripRhythm.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(trip_rhythm=self.value())
        return queryset


class BudgetLevelFilter(SimpleListFilter):
    title = _('预算等级')
    parameter_name = 'budget_level'

    def lookups(self, request, model_admin):
        return Requirement.BudgetLevel.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(budget_level=self.value())
        return queryset


class TemplateFilter(SimpleListFilter):
    title = _('模板类型')
    parameter_name = 'is_template'

    def lookups(self, request, model_admin):
        return (
            ('1', _('是模板')),
            ('0', _('非模板')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_template=True)
        elif self.value() == '0':
            return queryset.filter(is_template=False)
        return queryset


class DateFlexibilityFilter(SimpleListFilter):
    title = _('日期灵活性')
    parameter_name = 'travel_date_flexible'

    def lookups(self, request, model_admin):
        return (
            ('1', _('日期灵活')),
            ('0', _('日期固定')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(travel_date_flexible=True)
        elif self.value() == '0':
            return queryset.filter(travel_date_flexible=False)
        return queryset


class GroupSizeFilter(SimpleListFilter):
    title = _('团队规模')
    parameter_name = 'group_size'

    def lookups(self, request, model_admin):
        return (
            ('small', _('小团队 (1-5人)')),
            ('medium', _('中团队 (6-15人)')),
            ('large', _('大团队 (16人以上)')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'small':
            return queryset.filter(group_total__lte=5)
        elif self.value() == 'medium':
            return queryset.filter(group_total__gte=6, group_total__lte=15)
        elif self.value() == 'large':
            return queryset.filter(group_total__gte=16)
        return queryset


class TripDurationFilter(SimpleListFilter):
    title = _('行程时长')
    parameter_name = 'trip_duration'

    def lookups(self, request, model_admin):
        return (
            ('short', _('短期 (1-3天)')),
            ('medium', _('中期 (4-7天)')),
            ('long', _('长期 (8天以上)')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'short':
            return queryset.filter(trip_days__lte=3)
        elif self.value() == 'medium':
            return queryset.filter(trip_days__gte=4, trip_days__lte=7)
        elif self.value() == 'long':
            return queryset.filter(trip_days__gte=8)
        return queryset
