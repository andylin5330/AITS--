from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .tasks import simulate_agent_generation

@api_view(['POST'])
@permission_classes([AllowAny]) # For easy local testing, bypassing auth temporary
def generate_agent_cases(request):
    prompt = request.data.get('prompt', '')
    task_id = request.data.get('task_id', 'agent_session')
    
    if not prompt:
        return Response({"error": "Prompt is empty"}, status=400)

    # Dispatch Celery simulated task
    simulate_agent_generation.delay(task_id, prompt)

    return Response({
        "status": "success",
        "message": "Generating...",
        "task_id": task_id
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def save_agent_cases(request):
    from api_testing.models import APITestCase
    from projects.models import Project

    project_id = request.data.get('project_id')
    content = request.data.get('content', '')
    name = request.data.get('name', 'AI生成的接口场景测试用例')
    
    if not project_id or not content:
        return Response({"error": "Missing project_id or content"}, status=400)
    
    try:
        project = Project.objects.get(id=project_id)
        # Store the generated markdown in request_data or assertions placeholder for now
        # You could implement deeper LLM structured JSON parsing here later
        case = APITestCase.objects.create(
            project=project,
            name=name,
            case_type='scenario',
            request_data={"ai_raw_content": content},
            is_ai_generated=True
        )
        return Response({"status": "success", "case_id": case.id})
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
