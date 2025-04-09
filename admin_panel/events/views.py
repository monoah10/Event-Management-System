from django.shortcuts import render, redirect
import requests
from .forms import EventForm, UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


API_BASE = "http://localhost:8000"

def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                response = requests.post(f"{API_BASE}/users/login", json=data)
                if response.status_code == 200:
                    res_json = response.json()

                    token = res_json.get("access_token")
                    if not token:
                        messages.error(request, "Token not received.")
                        return redirect("login")
                    bearer_token = f"Bearer {token}"
                    request.session["access_token"] = bearer_token
                    headers = {"Authorization": bearer_token}
                    user_info_resp = requests.get(f"{API_BASE}/users/me", headers=headers)
                    if user_info_resp.status_code == 200:
                        user_info = user_info_resp.json()
                        request.session["user_role"] = user_info.get("role", "attendee")
                        request.session["user_id"] = user_info.get("id")
                        request.session["username"] = user_info.get("username")
                        messages.success(request, f"Welcome, {user_info.get('username')}!")
                        return redirect("dashboard")
                    else:
                        messages.warning(request, "Logged in but failed to fetch user info.")
                        return redirect("dashboard")
                else:
                    detail = response.json().get("detail", "Login failed.")
                    messages.error(request, detail)

            except Exception as e:
                messages.error(request, f"Something went wrong: {str(e)}")

    else:
        form = UserLoginForm()

    return render(request, "auth/login.html", {"form": form})

def user_logout(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

def make_authenticated_request(method, url, headers=None, json=None, params=None):
    method = method.upper()
    headers = headers or {}
    try:
        response = requests.request(method, url, headers=headers, json=json, params=params)
        print(f"status for endpoint {url} is  {response.status_code}")
        if response.status_code == 401 or "token expired" in response.text.lower():
            return redirect("logout")
        return response

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")

def dashboard(request):
    user_role = request.session.get("user_role")

    return render(request, "auth/dashboard.html", {
        "user_role": user_role,
        "username": request.session.get("username")
    })

def event_list(request):
    location = request.GET.get("location")
    page = int(request.GET.get("page", 1))
    limit = 5
    offset = (page - 1) * limit

    params = {"limit": limit, "offset": offset}
    if location:
        params["location"] = location

    try:
        # response = requests.get(f'{API_BASE}/events', params=params)
        response = make_authenticated_request(method="get", url=f'{API_BASE}/events', params=params)
        if isinstance(response, HttpResponseRedirect):
            return response
        response.raise_for_status()
        events = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Failed to fetch events: {e}")
        events = []

    return render(request, "events/event_list.html", {
        "events": events,
        "page": page,
        "location": location
    })

def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            token = request.session.get("access_token")
            if not token:
                messages.error(request, "Authentication required to create events.")
                return redirect("event_list")
            headers = {"Authorization": token}
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()

            try:
                # response = requests.post(f'{API_BASE}/events', json=data, headers=headers)
                response = make_authenticated_request(method="post", url=f'{API_BASE}/events', json=data, headers=headers)
                if isinstance(response, HttpResponseRedirect):
                    return response
                if response.status_code in [200, 201]:
                    messages.success(request, "Event created successfully!")
                    return redirect("event_list")
                else:
                    detail = response.json().get("detail", "Failed to create event.")
                    messages.error(request, detail)
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error connecting to API: {e}")
    else:
        form = EventForm()

    return render(request, "events/event_form.html", {"form": form})

def event_join(request, event_id):
    token = request.session.get("access_token")
    if not token:
        messages.error(request, "Login required to join events.")
        return redirect("event_list")

    headers = {"Authorization": token}
    url = f"{API_BASE}/events/{event_id}/join"
    try:
        # response = requests.post(url, headers=headers)
        response = make_authenticated_request(method="post", url=url, headers=headers)
        if isinstance(response, HttpResponseRedirect):
            return response
        if response.status_code == 200:
            messages.success(request, "Successfully joined the event.")
        else:
            messages.error(request, response.json().get("detail", "Failed to join the event."))
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Failed to join event: {e}")

    return redirect("event_list")

def event_delete(request, event_id):
    token = request.session.get("access_token")
    if not token:
        messages.error(request, "Login required to delete events.")
        return redirect("event_list")
    if request.session.get("user_role") not in ["admin", "organizer"]:
        messages.error(request, f"Not authorized to edit events")
        return redirect("event_list")

    headers = {"Authorization": token}
    url = f"{API_BASE}/events/{event_id}/delete"

    try:
        requests.delete(url, headers=headers)
        messages.success(request, "Event deleted successfully.")
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Failed to delete event: {e}")
    return redirect("event_list")

def event_edit(request, event_id):
    if request.session.get("user_role") not in ["admin", "organizer"]:
        messages.error(request, f"Not authorized to edit events")
        return redirect("event_list")
    headers = {
        "Authorization": request.session.get("access_token")
    }

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
            try:
                # response = requests.put(
                #     f"{API_BASE}/events/{event_id}/update",
                #     json=data,
                #     headers=headers
                # )
                response = make_authenticated_request(method="put", url=f"{API_BASE}/events/{event_id}/update", json=data,
                                                      headers=headers)
                if isinstance(response, HttpResponseRedirect):
                    return response
                if response.status_code == 200:
                    messages.success(request, "Event updated successfully!")
                    return redirect("event_list")
                else:
                    detail = response.json().get("detail", "Failed to update event.")
                    messages.error(request, detail)
            except Exception as e:
                messages.error(request, f"Error updating event: {str(e)}")
            return redirect("event_list")
    else:
        form = EventForm()
    return render(request, "events/event_edit.html", {"form": form, "event_id": event_id, "edit": True})

def event_attendees(request, event_id):
    if request.session.get("user_role") not in ["admin", "organizer"]:
        return HttpResponseForbidden("Not authorized")

    access_token = request.session.get("access_token")
    if not access_token:
        messages.error(request, "Unauthorized: No access token.")
        return redirect("login")

    headers = {"Authorization": access_token}
    try:
        # response = requests.get(f"{API_BASE}/events/{event_id}", headers=headers)
        response = make_authenticated_request(method="get", url=f"{API_BASE}/events/{event_id}", headers=headers)
        if isinstance(response, HttpResponseRedirect):
            return response
        if response.status_code == 200:
            event = response.json()
            attendees = event.get("attendees", [])
            return render(request, "auth/attendee_list.html", {
                "users": attendees,
                "event_title": event.get("title"),
                "event_id": event_id,
            })
        else:
            messages.error(request, "Failed to fetch event details.")
            return redirect("event_list")
    except requests.RequestException as e:
        messages.error(request, f"Request error: {str(e)}")
        return redirect("event_list")

def remove_attendee(request, event_id, user_id):
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect("login")

    headers = {"Authorization": access_token}
    try:
        # response = requests.delete(f"{API_BASE}/events/{event_id}/attendees/{user_id}", headers=headers)
        response = make_authenticated_request(method="delete", url=f"{API_BASE}/events/{event_id}/attendees/{user_id}", headers=headers)
        if isinstance(response, HttpResponseRedirect):
            return response
        if response.status_code == 200:
            messages.success(request, "Attendee removed successfully.")
        else:
            messages.error(request, "Failed to remove attendee.")
    except requests.RequestException as e:
        messages.error(request, f"Error: {str(e)}")

    return redirect("event_attendees", event_id=event_id)

def user_register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                response = requests.post(f"{API_BASE}/users/register", json=data)
                if response.status_code in [200, 201]:
                    messages.success(request, "Registration successful! Please log in.")
                    print(response, "response===========")
                    return redirect("login")
                else:
                    messages.error(request, response.json().get("detail", "Registration failed."))
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = UserRegisterForm()

    return render(request, "auth/register.html", {"form": form})

def all_users(request):
    if request.session.get("user_role") != "admin":
        return HttpResponseForbidden("Not authorized")

    access_token = request.session.get("access_token")
    if not access_token:
        messages.error(request, "Unauthorized: No access token found.")
        return redirect("login")

    headers = {"Authorization": access_token}
    try:
        # response = requests.get(f"{API_BASE}/users/all_users", headers=headers)
        response = make_authenticated_request(method="get", url=f"{API_BASE}/users/all_users", headers=headers)
        if isinstance(response, HttpResponseRedirect):
            return response
        if response.status_code == 200:
            users = response.json()
            return render(request, "auth/user_list.html", {"users": users})
        else:
            detail = response.json().get("detail", "Failed to fetch users.")
            messages.error(request, f"Error: {detail}")
            return redirect("event_list")
    except requests.RequestException as e:
        messages.error(request, f"Request error: {str(e)}")
        return redirect("event_list")

def delete_user(request, user_id):
    access_token = request.session.get("access_token")
    if not access_token:
        messages.error(request, "Unauthorized: No access token found.")
        return redirect("login")

    headers = {"Authorization": access_token}
    try:
        # response = requests.delete(f"{API_BASE}/users/{user_id}/delete", headers=headers)
        response = make_authenticated_request(method="delete", url=f"{API_BASE}/users/{user_id}/delete", headers=headers)
        if isinstance(response, HttpResponseRedirect):
            return response

        if response.status_code == 200:
            messages.success(request, "User deleted successfully!")
        else:
            detail = response.json().get("detail", "Failed to delete user.")
            messages.error(request, f"Error: {detail}")
    except requests.RequestException as e:
        messages.error(request, f"Request error: {str(e)}")
        print((str(e)))
    return redirect("admin_user_list")

@csrf_exempt
def update_user(request, user_id):
    if request.method == "POST":
        username = request.POST.get("username")
        role = request.POST.get("role")
        access_token = request.session.get("access_token")

        if not access_token:
            messages.error(request, "Unauthorized: No access token found.")
            return redirect("login")

        headers = {"Authorization": access_token}
        data = {
            "username": username,
            "role": role
        }
        try:
            response = make_authenticated_request(
                method="put",
                url=f"{API_BASE}/users/{user_id}/update",
                headers=headers,
                json=data
            )
            if isinstance(response, HttpResponseRedirect):
                return response
            if response.status_code == 200:
                messages.success(request, "User updated successfully!")
            else:
                detail = response.json().get("detail", "Failed to update user.")
                messages.error(request, f"Error: {detail}")

        except requests.RequestException as e:
            messages.error(request, f"Request error: {str(e)}")
            print((str(e)))

    return redirect("admin_user_list")

def attendees(request):
    if request.session.get("user_role") != "organizer":
        return HttpResponseForbidden("Not authorized")

    access_token = request.session.get("access_token")
    if not access_token:
        messages.error(request, "Unauthorized: No access token found.")
        return redirect("login")

    headers = {"Authorization": access_token}
    try:
        # response = requests.get(f"{API_BASE}/users", headers=headers)
        response = make_authenticated_request(method="get", url=f"{API_BASE}/users", headers=headers)
        if isinstance(response, HttpResponseRedirect):
            return response
        if response.status_code == 200:
            attendees = response.json()
            return render(request, "auth/attendee_list.html", {"users": attendees})
        else:
            detail = response.json().get("detail", "Failed to fetch attendees.")
            messages.error(request, f"Error: {detail}")
            return redirect("event_list")
    except requests.RequestException as e:
        messages.error(request, f"Request error: {str(e)}")
        return redirect("event_list")