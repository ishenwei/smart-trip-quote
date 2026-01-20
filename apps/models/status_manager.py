from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


class RequirementStatusManager:
    
    @staticmethod
    def confirm_requirement(requirement_id, reviewer=None):
        from .requirement import Requirement
        try:
            requirement = Requirement.objects.get(requirement_id=requirement_id)
            if requirement.status != Requirement.Status.PENDING_REVIEW:
                raise ValueError(f'需求状态必须为待审核才能确认，当前状态: {requirement.get_status_display()}')
            
            requirement.confirm(reviewer)
            return requirement
        except Requirement.DoesNotExist:
            raise ValueError(f'需求不存在: {requirement_id}')
    
    @staticmethod
    def expire_requirement(requirement_id):
        from .requirement import Requirement
        try:
            requirement = Requirement.objects.get(requirement_id=requirement_id)
            if requirement.status == Requirement.Status.EXPIRED:
                return requirement
            
            if requirement.status not in [Requirement.Status.PENDING_REVIEW, Requirement.Status.CONFIRMED]:
                raise ValueError(f'需求状态必须为待审核或已确认才能过期，当前状态: {requirement.get_status_display()}')
            
            requirement.expire()
            return requirement
        except Requirement.DoesNotExist:
            raise ValueError(f'需求不存在: {requirement_id}')
    
    @staticmethod
    def check_and_expire_pending_requirements(pending_hours=72):
        from .requirement import Requirement
        expiry_time = timezone.now() - timedelta(hours=pending_hours)
        expired_requirements = Requirement.objects.filter(
            status=Requirement.Status.PENDING_REVIEW,
            created_at__lt=expiry_time
        )
        
        count = expired_requirements.count()
        expired_requirements.update(status=Requirement.Status.EXPIRED)
        
        return count
    
    @staticmethod
    def check_and_expire_confirmed_requirements(validity_hours=168):
        from .requirement import Requirement
        expiry_time = timezone.now() - timedelta(hours=validity_hours)
        expired_requirements = Requirement.objects.filter(
            status=Requirement.Status.CONFIRMED,
            created_at__lt=expiry_time
        )
        
        count = expired_requirements.count()
        expired_requirements.update(status=Requirement.Status.EXPIRED)
        
        return count
    
    @staticmethod
    def check_all_expired_requirements(pending_hours=72, confirmed_hours=168):
        pending_count = RequirementStatusManager.check_and_expire_pending_requirements(pending_hours)
        confirmed_count = RequirementStatusManager.check_and_expire_confirmed_requirements(confirmed_hours)
        
        return {
            'pending_expired': pending_count,
            'confirmed_expired': confirmed_count,
            'total_expired': pending_count + confirmed_count
        }
    
    @staticmethod
    def get_requirements_by_status(status):
        from .requirement import Requirement
        return Requirement.objects.filter(status=status)
    
    @staticmethod
    def get_pending_requirements():
        from .requirement import Requirement
        return Requirement.objects.filter(status=Requirement.Status.PENDING_REVIEW)
    
    @staticmethod
    def get_confirmed_requirements():
        from .requirement import Requirement
        return Requirement.objects.filter(status=Requirement.Status.CONFIRMED)
    
    @staticmethod
    def get_expired_requirements():
        from .requirement import Requirement
        return Requirement.objects.filter(status=Requirement.Status.EXPIRED)
    
    @staticmethod
    def get_requirements_near_expiry(hours_threshold=24):
        from .requirement import Requirement
        threshold_time = timezone.now() + timedelta(hours=hours_threshold)
        return Requirement.objects.filter(
            status__in=[Requirement.Status.PENDING_REVIEW, Requirement.Status.CONFIRMED],
            expires_at__lte=threshold_time
        )
    
    @staticmethod
    def set_expiry_time(requirement_id, hours):
        from .requirement import Requirement
        try:
            requirement = Requirement.objects.get(requirement_id=requirement_id)
            requirement.expires_at = timezone.now() + timedelta(hours=hours)
            requirement.save()
            return requirement
        except Requirement.DoesNotExist:
            raise ValueError(f'需求不存在: {requirement_id}')
    
    @staticmethod
    def get_status_statistics():
        from .requirement import Requirement
        from django.db.models import Count
        
        stats = Requirement.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        result = {}
        for stat in stats:
            result[stat['status']] = stat['count']
        
        return result
    
    @staticmethod
    def validate_status_transition(current_status, new_status):
        from .requirement import Requirement
        valid_transitions = {
            Requirement.Status.PENDING_REVIEW: [
                Requirement.Status.CONFIRMED,
                Requirement.Status.EXPIRED
            ],
            Requirement.Status.CONFIRMED: [
                Requirement.Status.EXPIRED
            ],
            Requirement.Status.EXPIRED: []
        }
        
        if current_status not in valid_transitions:
            return False
        
        if new_status not in valid_transitions[current_status]:
            return False
        
        return True
