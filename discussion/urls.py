from django.urls import path
from . import views

app_name = 'discussion'

urlpatterns = [
    path('discussion-page/', views.discussion_home, name='discussion-page'),
    path('create-topic/', views.create_topic, name='create-topic'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('ajax/reply/<int:topic_pk>/', views.ajax_add_reply, name='ajax_add_reply'),
    path('ajax/reply/<int:topic_pk>/<int:parent_pk>/', views.ajax_add_reply, name='ajax_add_nested_reply'),
]
