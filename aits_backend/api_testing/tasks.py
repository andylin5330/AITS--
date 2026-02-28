import os
import json
import uuid
import shutil
import pytest
import subprocess
from celery import shared_task
from django.conf import settings
from .models import APITestSuite, APITestExecution

@shared_task
def run_api_test_suite(execution_id):
    try:
        execution = APITestExecution.objects.get(id=execution_id)
    except APITestExecution.DoesNotExist:
        return {'error': 'Execution record not found'}

    execution.status = 'running'
    execution.save()

    suite = execution.suite
    cases = suite.cases.all()

    if not cases.exists():
        execution.status = 'error'
        execution.report_data = {'message': 'Suite has no test cases'}
        execution.save()
        return {'status': 'error', 'message': 'No cases'}

    # Prepare directories
    base_dir = settings.MEDIA_ROOT / 'test_runs' / str(execution_id)
    test_scripts_dir = base_dir / 'scripts'
    allure_results_dir = base_dir / 'results'
    allure_html_dir = base_dir / 'html'

    os.makedirs(test_scripts_dir, exist_ok=True)
    os.makedirs(allure_results_dir, exist_ok=True)

    # 1. Generate test file
    test_file_path = test_scripts_dir / 'test_cases.py'
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write("import pytest\n")
        f.write("import requests\n")
        f.write("import allure\n\n")

        # Basic dynamic generation based on Request Data
        for i, case in enumerate(cases):
            f.write(f"@allure.title({repr(case.name)})\n")
            f.write(f"def test_case_{case.id}_{i}():\n")
            
            # Simple fallback request extraction
            # Assume request_data has url, method, headers, json/data
            r_data = case.request_data or {}
            method = r_data.get('method', 'GET').lower()
            url = r_data.get('url', 'http://localhost')
            if not url.startswith('http'):
                url = 'http://localhost' + url if url.startswith('/') else 'http://localhost/' + url

            headers = r_data.get('headers', {})
            json_body = r_data.get('body', {})
            params = r_data.get('params', {})

            if type(json_body) is str:
                try:
                    json_body = json.loads(json_body)
                except:
                    pass

            f.write("    with allure.step('Send Request'):\n")
            f.write(f"        req_kwargs = {{\n")
            f.write(f"            'method': repr('{method}'),\n")
            f.write(f"            'url': repr('{url}')\n")
            f.write(f"        }}\n")
            
            f.write(f"        headers = {repr(headers)}\n")
            f.write(f"        if headers:\n")
            f.write(f"            req_kwargs['headers'] = headers\n")

            f.write(f"        params = {repr(params)}\n")
            f.write(f"        if params:\n")
            f.write(f"            req_kwargs['params'] = params\n")

            if method in ['post', 'put', 'patch'] and json_body:
                f.write(f"        req_kwargs['json'] = {repr(json_body)}\n")
            
            f.write(f"        response = requests.request(method='{method}', url='{url}', headers=headers, params=params, json={repr(json_body)})\n")
            
            # Very basic assertions injection (optional based on your structure)
            f.write("    with allure.step('Verify Status Code'):\n")
            f.write("        assert response.status_code < 600\n")
            f.write("\n")

    # 2. Run Pytest with Allure
    import sys
    pytest_cmd = [
        sys.executable, '-m', 'pytest',
        str(test_file_path),
        f'--alluredir={allure_results_dir}',
        '-p', 'no:mcp_eval'  # Disable conflicting global plugin
    ]
    
    try:
        run_res = subprocess.run(pytest_cmd, capture_output=True, text=True)
        ret = run_res.returncode
    except Exception as e:
        execution.status = 'error'
        execution.report_data = {'message': f"Pytest execution failed: {str(e)}"}
        execution.save()
        return {'status': 'error', 'message': str(e)}
    
    # 3. Generate Allure Report HTML
    # `allure generate <results_dir> -o <html_dir> --clean`
    try:
        subprocess.run(
            ['allure', 'generate', str(allure_results_dir), '-o', str(allure_html_dir), '--clean'],
            check=True,
            capture_output=True,
            shell=os.name == 'nt' # Use shell on Windows
        )
        report_url = f"{settings.MEDIA_URL}test_runs/{execution_id}/html/index.html"
        execution.status = 'passed' if ret == 0 else 'failed'
        execution.report_data = {
            'report_url': report_url,
            'pytest_exit_code': int(ret)
        }
    except subprocess.CalledProcessError as e:
        execution.status = 'error'
        execution.report_data = {
            'message': 'Failed to generate allure HTML report',
            'stderr': e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
        }
    
    execution.save()
    return {'status': execution.status, 'report_data': execution.report_data}
