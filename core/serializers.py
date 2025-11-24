from rest_framework import serializers
from .models import SiteSettings, Feature, Step

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = "__all__"

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = "__all__"

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = "__all__"
