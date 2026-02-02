from rest_framework import serializers
from django.db import transaction
from .models import (
    CareerApplication,
    ContactMessage,
    MOU,
    GalleryImage,
    Project,
    CommunityItem,
    CpuInquiry,
    Team,
    Participant,
)


class CareerApplicationSerializer(serializers.ModelSerializer):
    def validate_resume(self, value):
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Resume must be a PDF file")
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Resume size must be below 5MB")
        return value

    class Meta:
        model = CareerApplication
        fields = "__all__"


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"


class MOUSerializer(serializers.ModelSerializer):
    class Meta:
        model = MOU
        fields = "__all__"


class GalleryImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ["id", "title", "category", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class CommunityItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityItem
        fields = "__all__"


class CpuInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = CpuInquiry
        fields = "__all__"



class ParticipantSerializer(serializers.ModelSerializer):
    # accept frontend camelCase
    fullName = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Participant
        exclude = ("team",)

    # map fullName -> full_name
    def to_internal_value(self, data):
        if "fullName" in data:
            data["full_name"] = data.pop("fullName")
        return super().to_internal_value(data)

    # phone validation
    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone must contain only digits"
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must be 10 digits"
            )

        return value


class TeamRegistrationSerializer(serializers.ModelSerializer):
    leader = ParticipantSerializer()
    members = ParticipantSerializer(many=True)

    class Meta:
        model = Team
        fields = ("team_name", "leader", "members")

    # allow frontend "teamName"
    def to_internal_value(self, data):
        if "teamName" in data:
            data["team_name"] = data.pop("teamName")
        return super().to_internal_value(data)

    # validation
    def validate(self, data):
        members = data.get("members", [])
        leader = data.get("leader")

        total_members = 1 + len(members)

        # team size rule
        if total_members < 2 or total_members > 6:
            raise serializers.ValidationError(
                "Team must have between 2 and 6 members"
            )

        # duplicate emails prevention
        emails = {leader["email"]}
        for m in members:
            if m["email"] in emails:
                raise serializers.ValidationError(
                    "Duplicate email in team members"
                )
            emails.add(m["email"])

        return data

    # atomic creation
    @transaction.atomic
    def create(self, validated_data):
        leader_data = validated_data.pop("leader")
        members_data = validated_data.pop("members")

        team = Team.objects.create(**validated_data)

        # create leader
        Participant.objects.create(
            team=team,
            is_leader=True,
            **leader_data
        )

        # create members
        for member in members_data:
            Participant.objects.create(
                team=team,
                is_leader=False,
                **member
            )

        return team
