"""
API views for Carriers.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth.models import User
from .models import CarrierInfo
from .serializers import CarrierInfoListSerializer, CarrierInfoDetailSerializer, CarrierInfoCreateSerializer


@extend_schema_view(
    list=extend_schema(summary="List Carriers", tags=["Carriers"]),
    create=extend_schema(summary="Create Carrier", tags=["Carriers"]),
    retrieve=extend_schema(summary="Get Carrier", tags=["Carriers"]),
    update=extend_schema(summary="Update Carrier", tags=["Carriers"]),
    partial_update=extend_schema(summary="Partially Update Carrier", tags=["Carriers"]),
    destroy=extend_schema(summary="Delete Carrier", tags=["Carriers"])
)
class CarrierInfoViewSet(viewsets.ModelViewSet):
    queryset = CarrierInfo.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'address', 'phone']
    ordering_fields = ['name', 'created_on', 'modified_on']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CarrierInfoListSerializer
        elif self.action == 'create':
            return CarrierInfoCreateSerializer
        else:
            return CarrierInfoDetailSerializer
    
    def perform_create(self, serializer):
        default_user = User.objects.first()
        if default_user:
            serializer.save(created_by=default_user, modified_by=default_user, owner=default_user)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        default_user = User.objects.first()
        if default_user:
            serializer.save(modified_by=default_user)
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        instance.status = 'inactive'
        instance.save()
    
    @extend_schema(summary="Get Migration Information", tags=["Carriers"])
    @action(detail=False, methods=['get'])
    def migration_info(self, request):
        queryset = self.get_queryset()
        total_count = queryset.count()
        active_count = queryset.filter(status='active').count()
        
        return Response({
            "powerapps_entity_name": "cr7c4_carrierinfo",
            "django_model_name": "CarrierInfo",
            "django_app_name": "carriers",
            "total_records": total_count,
            "active_records": active_count,
            "field_mappings": {
                "cr7c4_name": "name",
                "cr7c4_address": "address", 
                "cr7c4_phone": "phone",
                "statecode/statuscode": "status",
                "CreatedOn": "created_on",
                "ModifiedOn": "modified_on",
                "CreatedBy": "created_by",
                "ModifiedBy": "modified_by",
                "OwnerId": "owner"
            },
            "api_endpoints": {
                "list": "/api/v1/carriers/",
                "detail": "/api/v1/carriers/{id}/",
                "migration_info": "/api/v1/carriers/migration_info/"
            }
        }, status=status.HTTP_200_OK)
