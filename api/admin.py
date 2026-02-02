from django.contrib import admin
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

@admin.register(CpuInquiry)
class CpuInquiryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'email',
        'cpu_model',
        'quantity',
        'ram',
        'storage',
        'created_at'
    )

    list_filter = ('cpu_model', 'created_at')
    search_fields = ('full_name', 'email', 'cpu_model')
    ordering = ('-created_at',)

    readonly_fields = ()   

@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'phone',
        'college',
        'year_of_passing',
        'applied_at'
    )
    search_fields = ('full_name', 'email', 'skills')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "phone",
        "subject",
        "message",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
        "message",
    )

@admin.register(MOU)
class MOUAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "start_date",
        "is_active",
    )
    list_filter = ("category", "is_active")
    search_fields = ("title",)

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "status",
        "progress",
        "start_date",
        "end_date",
    )
    list_filter = ("status",)
    search_fields = ("title", "client")
    list_editable = ("status", "progress")

@admin.register(CommunityItem)
class CommunityItemAdmin(admin.ModelAdmin):

    list_display = ("title", "section", "item_type", "created_at")
    list_filter = ("section", "item_type")
    search_fields = ("title",)

    fieldsets = (
        ("Basic", {
            "fields": ("section", "item_type", "title", "description")
        }),
        ("Workshop Details", {
            "fields": ("date", "status", "participants"),
            "classes": ("workshop-fields",),
        }),
        ("Gallery Image", {
            "fields": ("image",),
            "classes": ("gallery-fields",),
        }),
    )

    class Media:
        js = ("admin/js/community_toggle.js",)
   
class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0
    fields = (
        "full_name",
        "email",
        "phone",
        "branch",
        "section",
        "year",
        "is_leader",
    )
    readonly_fields = ("is_leader",)


# ==============================
# Team Admin
# ==============================
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "team_name",
        "leader_name",
        "participants_count",
        "participants_names",
        "created_at",
    )

    search_fields = (
        "team_name",
        "participants__full_name",
        "participants__email",
    )

    ordering = ("-created_at",)

    inlines = [ParticipantInline]

    # 🔹 Team Leader Name
    def leader_name(self, obj):
        leader = obj.participants.filter(is_leader=True).first()
        return leader.full_name if leader else "-"
    leader_name.short_description = "Team Leader"

    # 🔹 Participants Count
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = "Members"

    # 🔹 Participants Names (comma separated)
    def participants_names(self, obj):
        names = obj.participants.values_list("full_name", flat=True)
        return ", ".join(names)
    participants_names.short_description = "Participants"


# ==============================
# Participant Admin (optional standalone view)
# ==============================
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "team",
        "branch",
        "year",
        "section",
        "is_leader",
    )

    list_filter = (
        "branch",
        "year",
        "is_leader",
    )

    search_fields = (
        "full_name",
        "email",
        "team__team_name",
    )