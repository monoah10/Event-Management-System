from django.urls import path
from . import views

urlpatterns = [
    path("", views.event_list, name="event_list"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/edit/<int:event_id>/", views.event_edit, name="event_edit"),
    path("events/delete/<int:event_id>/", views.event_delete, name="event_delete"),
    path("events/join/<int:event_id>/", views.event_join, name="event_join"),
    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("users/", views.all_users, name="admin_user_list"),
    path("attendees/", views.attendees, name="attendee_list"),
path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path("events/<int:event_id>/attendees/", views.event_attendees, name="event_attendees"),
path("events/<int:event_id>/attendees/<int:user_id>/remove/", views.remove_attendee, name="remove_attendee"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
