import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection

try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1 AS test_query')
    result = cursor.fetchone()
    print('Test query result:', result)
    print('Database connection: SUCCESS')
except Exception as e:
    print('Database connection: FAILED')
    print('Error:', str(e))
finally:
    cursor.close()
