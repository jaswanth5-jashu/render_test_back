from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from django.conf import settings
from django.shortcuts import get_object_or_404
import requests

from .models import (
    CareerApplication,
    ContactMessage,
    MOU,
    GalleryImage,
    Project,
    CommunityItem,
    CpuInquiry,Team,Participant,
)
from .serializers import (
    CareerApplicationSerializer,
    ContactMessageSerializer,
    MOUSerializer,
    GalleryImageSerializer,
    ProjectSerializer,
    CommunityItemSerializer,
    CpuInquirySerializer,TeamRegistrationSerializer
)

#send messages to telegram 

def send_telegram(bot_token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=5)
    except:
        pass


class CareerApplicationCreate(APIView):

    def get(self, request):
        qs = CareerApplication.objects.all().order_by("-applied_at")
        serializer = CareerApplicationSerializer(qs, many=True)
        return Response(serializer.data)

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
                f"Career Application\n\n"
                f"Name: {obj.full_name}\n"
                f"Email: {obj.email}\n"
                f"Phone: {obj.phone}\n"
                f"College: {obj.college}\n"
                f"CGPA: {obj.cgpa}\n"
                f"Year: {obj.year_of_passing}\n"
                f"Experience: {obj.experience}\n"
                f"Skills: {obj.skills}\n\n"
                f"Resume:\n{resume_url}"
            )

            return Response(
                {"message": "Application submitted successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = get_object_or_404(CareerApplication, pk=pk)
        obj.delete()
        return Response(
            {"message": "Career application deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


class ContactMessageCreate(APIView):

    def get(self, request):
        qs = ContactMessage.objects.all().order_by("-created_at")
        serializer = ContactMessageSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()

            send_telegram(
                settings.TELEGRAM_CONTACT_BOT_TOKEN,
                settings.TELEGRAM_CONTACT_CHAT_ID,
                f"Contact Message\n\n"
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

    def delete(self, request, pk):
        obj = get_object_or_404(ContactMessage, pk=pk)
        obj.delete()
        return Response(
            {"message": "Contact message deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET", "POST", "DELETE"])
def create_inquiry(request, pk=None):

    if request.method == "GET":
        qs = CpuInquiry.objects.all().order_by("-created_at")
        serializer = CpuInquirySerializer(qs, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = CpuInquirySerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()

            send_telegram(
                settings.TELEGRAM_CPU_BOT_TOKEN,
                settings.TELEGRAM_CPU_CHAT_ID,
                f"CPU Inquiry\n\n"
                f"Name: {obj.full_name}\n"
                f"Email: {obj.email}\n"
                f"Phone: {obj.phone}\n"
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

    if request.method == "DELETE":
        obj = get_object_or_404(CpuInquiry, pk=pk)
        obj.delete()
        return Response(
            {"message": "CPU inquiry deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


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
        qs = Project.objects.all()
        serializer = ProjectSerializer(qs, many=True)
        return Response(serializer.data)


class CommunityItemListAPIView(ListAPIView):
    serializer_class = CommunityItemSerializer

    def get_queryset(self):
        return CommunityItem.objects.filter(section="giveback").order_by("-created_at")
    

class HackathonRegistrationView(APIView):

    # 🔹 GET: list all registrations
    def get(self, request):
        teams = Team.objects.all().order_by("-created_at")
        data = []

        for team in teams:
            participants = Participant.objects.filter(team=team)

            team_data = {
                "id": team.id,
                "team_name": team.team_name,
                "total_members": participants.count(),
                "participants": [
                    {
                        "full_name": p.full_name,
                        "email": p.email,
                        "phone": p.phone,
                        "branch": p.branch,
                        "section": p.section,
                        "year": p.year,
                        "is_leader": p.is_leader,
                    }
                    for p in participants
                ],
            }

            data.append(team_data)

        return Response(data, status=status.HTTP_200_OK)

    # 🔹 POST: create registration + telegram
    def post(self, request):
        serializer = TeamRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            team = serializer.save()
            participants = Participant.objects.filter(team=team)

            message = (
                "🚀 Hackathon Registration\n\n"
                f"Team: {team.team_name}\n"
                f"Total Members: {participants.count()}\n\n"
            )

            for p in participants:
                role = "Leader" if p.is_leader else "Member"
                message += (
                    f"{role}\n"
                    f"Name: {p.full_name}\n"
                    f"Email: {p.email}\n"
                    f"Phone: {p.phone}\n"
                    f"Branch: {p.branch}\n"
                    f"Section: {p.section}\n"
                    f"Year: {p.year}\n\n"
                )

            send_telegram(
                settings.TELEGRAM_HACKATHON_TOKEN,
                settings.TELEGRAM_HACKATHON_ID,
                message
            )

            return Response(
                {"message": "Hackathon registration successful"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔹 DELETE: delete team by ID
    def delete(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        team.delete()

        return Response(
            {"message": "Hackathon registration deleted"},
            status=status.HTTP_204_NO_CONTENT
        )
