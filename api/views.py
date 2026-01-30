from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from django.conf import settings
import requests

from .models import (
    CareerApplication,
    ContactMessage,
    MOU,
    GalleryImage,
    Project,
    CommunityItem,
)
from .serializers import (
    CareerApplicationSerializer,
    ContactMessageSerializer,
    MOUSerializer,
    GalleryImageSerializer,
    ProjectSerializer,
    CommunityItemSerializer,
    CpuInquirySerializer,
)


def send_telegram(bot_token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(
            url,
            data={"chat_id": chat_id, "text": text},
            timeout=5,
        )
    except:
        pass


class CareerApplicationCreate(APIView):
    def post(self, request):
        serializer = CareerApplicationSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()

            resume_url = ""
            if obj.resume:
                resume_url = request.build_absolute_uri(
                    settings.MEDIA_URL + obj.resume.name
                )

            send_telegram(
                settings.TELEGRAM_CAREER_BOT_TOKEN,
                settings.TELEGRAM_CAREER_CHAT_ID,
                f"📄 Career Application\n\n"
                f"Name: {obj.full_name}\n"
                f"Email: {obj.email}\n"
                f"Phone: {obj.phone}\n"
                f"College: {obj.college}\n"
                f"CGPA: {obj.cgpa}\n"
                f"Year: {obj.year_of_passing}\n"
                f"Experience: {obj.experience}\n"
                f"Skills: {obj.skills}\n\n"
                f"📎 Resume PDF:\n{resume_url}"
            )

            return Response(
                {"message": "Application submitted successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactMessageCreate(APIView):
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()

            send_telegram(
                settings.TELEGRAM_CONTACT_BOT_TOKEN,
                settings.TELEGRAM_CONTACT_CHAT_ID,
                f"📩 Contact Message\n\n"
                f"Name: {obj.name}\n"
                f"Email: {obj.email}\n"
                f"Phone: {obj.phone}\n"
                f"Subject: {obj.subject}\n"
                f"Message: {obj.message}"
            )

            return Response(
                {"message": "Contact saved"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MOUListAPIView(ListAPIView):
    serializer_class = MOUSerializer

    def get_queryset(self):
        return MOU.objects.filter(is_active=True)


class GalleryImageListAPIView(ListAPIView):
    serializer_class = GalleryImageSerializer
    queryset = GalleryImage.objects.all().order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ProjectListAPIView(APIView):
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


class CommunityItemListAPIView(ListAPIView):
    serializer_class = CommunityItemSerializer

    def get_queryset(self):
        return CommunityItem.objects.filter(section="giveback").order_by("-created_at")


@api_view(["POST"])
def create_inquiry(request):
    serializer = CpuInquirySerializer(data=request.data)
    if serializer.is_valid():
        obj = serializer.save()

        send_telegram(
            settings.TELEGRAM_CPU_BOT_TOKEN,
            settings.TELEGRAM_CPU_CHAT_ID,
            f"🖥 CPU Inquiry\n\n"
            f"Name: {obj.full_name}\n"
            f"Email: {obj.email}\n"
            f"CPU: {obj.cpu_model}\n"
            f"Quantity: {obj.quantity}\n"
            f"RAM: {obj.ram}\n"
            f"Storage: {obj.storage}\n"
            f"Message: {obj.message}"
        )

        return Response(
            {"message": "Inquiry submitted successfully"},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
