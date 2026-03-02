import re

with open('tests/test_itinerary_webhook.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r"apps\.admin\.views\.settings", 'django.conf.settings', content)

with open('tests/test_itinerary_webhook.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement completed")
