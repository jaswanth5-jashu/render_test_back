from django.urls import path
from .views import (
    CareerApplicationCreate,
    ContactMessageCreate,
    MOUListAPIView,
    GalleryImageListAPIView,
    ProjectListAPIView,
    CommunityItemListAPIView,
    create_inquiry,
)

urlpatterns = [
    path("apply/", CareerApplicationCreate.as_view()),
    path("contact/", ContactMessageCreate.as_view()),
    path("mous/", MOUListAPIView.as_view(), name="mous"),
    path("gallery/", GalleryImageListAPIView.as_view()),
    path("projects/", ProjectListAPIView.as_view()),
    path("giveback/", CommunityItemListAPIView.as_view()),
    path("inquiry/", create_inquiry),
]
