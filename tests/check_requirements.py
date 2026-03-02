import os
import django

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.models import Requirement

print("Checking requirements in database...")
requirements = Requirement.objects.all()
print(f"Found {requirements.count()} requirements")
for req in requirements:
    print(f"- {req.requirement_id}")
