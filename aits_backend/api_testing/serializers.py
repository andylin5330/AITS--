from rest_framework import serializers
from .models import APISpecification, APIEndpoint, APITestCase, APITestSuite, APITestExecution

class APISpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = APISpecification
        fields = '__all__'

class APIEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIEndpoint
        fields = '__all__'

class APITestCaseSerializer(serializers.ModelSerializer):
    endpoint_detail = APIEndpointSerializer(source='endpoint', read_only=True)

    class Meta:
        model = APITestCase
        fields = '__all__'

class APITestSuiteSerializer(serializers.ModelSerializer):
    cases_detail = APITestCaseSerializer(source='cases', many=True, read_only=True)

    class Meta:
        model = APITestSuite
        fields = '__all__'

class APITestExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = APITestExecution
        fields = '__all__'
