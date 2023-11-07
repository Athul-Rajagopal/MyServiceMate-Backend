from django.contrib import admin

# Register your models here.
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message_content', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__email', 'receiver__email', 'message_content')

admin.site.register(Message, MessageAdmin)