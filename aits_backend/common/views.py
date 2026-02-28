from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import test_websocket_log_task

@api_view(['POST'])
def trigger_celery_ws_task(request):
    task_id = request.data.get('task_id', 'general')
    iterations = int(request.data.get('iterations', 5))
    
    # Trigger celery task asynchronously
    test_websocket_log_task.delay(task_id, iterations)
    
    return Response({"status": "success", "message": f"Task deployed for {task_id}"})
