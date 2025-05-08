from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin  # Make sure this is correctly imported
from .models import Admin, Election, Candidate, Ballot, Vote, Result

# Custom UserAdmin for better handling of the User model
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']

# Register the custom UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register other models to the admin site
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'election', 'nomination_date', 'approval_status', 'image']
    list_filter = ['election', 'approval_status']
    search_fields = ['user__username', 'position']

    # Override save_model to automatically create a User for the Candidate
    def save_model(self, request, obj, form, change):
        if not obj.user:
            # Create a new User for the Candidate
            user = User.objects.create_user(username=obj.position + str(obj.id), password='defaultpassword123')
            obj.user = user  # Associate this User with the Candidate
        super().save_model(request, obj, form, change)

admin.site.register(Admin)
admin.site.register(Election)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Ballot)
admin.site.register(Vote)
admin.site.register(Result)
