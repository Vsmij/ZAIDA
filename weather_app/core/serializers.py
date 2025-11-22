# core/serializers.py
from rest_framework import serializers
from .models import Series, Measurement
from django.utils import timezone

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ['id', 'timestamp', 'value']
        read_only_fields = ['id']
'''
    def validate(self, data):
        #timestamp = data.get('timestamp')
        #if timestamp:
            #if timestamp.date() != timezone.now().date() and 
        if not self.context['request'].user.is_staff:
            raise serializers.ValidationError("Tylko admin moze edytowac pomiary.")
        return data
'''
class SeriesSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(many=True, read_only=True)
    min_temp = serializers.SerializerMethodField()
    max_temp = serializers.SerializerMethodField()

    class Meta:
        model = Series
        fields = ['date', 'color', 'min_temp', 'max_temp', 'measurements']
        read_only_fields = ['date', 'min_temp', 'max_temp', 'measurements']

    def get_min_temp(self, obj):
        return obj.get_min_temp()

    def get_max_temp(self, obj):
        return obj.get_max_temp()


'''
class SeriesListSerializer(serializers.ModelSerializer):
    min_temp = serializers.SerializerMethodField()
    max_temp = serializers.SerializerMethodField()
    measurements_count = serializers.IntegerField(source='measurements.count', read_only=True)

    class Meta:
        model = Series
        fields = ['date', 'color', 'min_temp', 'max_temp', 'measurements_count']

    def get_min_temp(self, obj):
        return obj.get_min_temp()

    def get_max_temp(self, obj):
        return obj.get_max_temp()


class SeriesDetailSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(many=True, read_only=True)
    min_temp = serializers.SerializerMethodField()
    max_temp = serializers.SerializerMethodField()

    class Meta:
        model = Series
        fields = ['date', 'color', 'min_temp', 'max_temp', 'measurements']

    def get_min_temp(self, obj):
        return obj.get_min_temp()

    def get_max_temp(self, obj):
        return obj.get_max_temp()

'''
#Bo kolor nie chciał działać
class SeriesColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ['color']

