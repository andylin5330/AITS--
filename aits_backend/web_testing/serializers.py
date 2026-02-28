from rest_framework import serializers
from .models import WebUITestCase, MidSceneScript, WebUITestSuite, WebUITestExecution

class WebUITestCaseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = WebUITestCase
        fields = '__all__'

class MidSceneScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MidSceneScript
        fields = '__all__'

class WebUITestSuiteSerializer(serializers.ModelSerializer):
    cases_detail = WebUITestCaseSerializer(source='cases', many=True, read_only=True)

    class Meta:
        model = WebUITestSuite
        fields = '__all__'

class WebUITestExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebUITestExecution
        fields = '__all__'
