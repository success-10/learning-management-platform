from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache


def health_check(request):
    """
    Health check endpoint for load balancers, container orchestrators,
    and monitoring systems. Verifies DB and Redis connectivity.
    """
    health = {'status': 'healthy'}

    # Check database connectivity
    try:
        connection.ensure_connection()
        health['database'] = 'ok'
    except Exception:
        health['database'] = 'error'
        health['status'] = 'unhealthy'

    # Check Redis/cache connectivity
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health['cache'] = 'ok'
        else:
            health['cache'] = 'error'
            health['status'] = 'unhealthy'
    except Exception:
        health['cache'] = 'error'
        health['status'] = 'unhealthy'

    status_code = 200 if health['status'] == 'healthy' else 503
    return JsonResponse(health, status=status_code)
