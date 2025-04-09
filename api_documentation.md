# Unified Event & User Management API Documentation

This document provides detailed information about the Unified Event & User Management API, which combines the functionalities of Event Management and User Management.

## Table of Contents

- [Event Management](#event-management)
  - [Create Event](#create-event)
  - [List Events](#list-events)
  - [Get Event by ID](#get-event-by-id)
  - [Join Event](#join-event)
  - [Delete Event](#delete-event)
  - [Update Event](#update-event)
  - [Remove Attendee from Event](#remove-attendee-from-event)
- [User Management](#user-management)
  - [Register User](#register-user)
  - [Login User](#login-user)
  - [Get Current User Info](#get-current-user-info)
  - [List All Attendees](#list-all-attendees)
  - [Delete User](#delete-user)
  - [Get All Users (Admin Only)](#get-all-users-admin-only)
  - [Update User](#update-user)

## Event Management

### Create Event

**Endpoint:** `POST {{base_url}}/events`

**Description:**  Allows an organizer or admin to create an event.

**Headers:**
- `Authorization: Bearer {{token}}`
- `Content-Type: application/json`

****Request Body:****
```json
{
  "title": "Sample Event",
  "description": "An event for demonstration.",
  "location": "Mumbai",
  "date": "2025-05-01",
  "max_attendees": 50
}```

### List Events

****Endpoint:****  `GET {{base_url}}/events?limit=10&offset=0`

**Description:**  Retrieve a list of events with optional pagination and filtering.

**Query Parameters:**
limit: Number of events to return (default: 10)
offset: Offset for pagination (default: 0)
Get Event by ID

**Endpoint:** GET {{base_url}}/events/1
**Description:**  Retrieve a specific event by its ID.
**Headers:**
Authorization: Bearer {{token}}


### Join Event
**Endpoint:** POST {{base_url}}/events/1/join
**Description:**  Join a specific event by its ID.
**Headers:**
Authorization: Bearer {{token}}

### Delete Event
**Endpoint:** DELETE {{base_url}}/events/1/delete
**Description:**  Delete a specific event by its ID (admin/organizer only).
**Headers:**
Authorization: Bearer {{token}}

### Update Event
**Endpoint:** PUT {{base_url}}/events/1/update
**Description:**  Update event details (admin/organizer only).
**Headers:**
Authorization: Bearer {{token}}
Content-Type: application/json
**Request Body:**
{
  "title": "Updated Event Title"
}

### Remove Attendee from Event
**Endpoint:** DELETE {{base_url}}/events/1/attendees/2
**Description:**  Remove a specific user from event attendees.
**Headers:**
Authorization: Bearer {{token}}

## User Management
### Register User
**Endpoint:** POST {{base_url}}/users/register
**Description:**  Register a new user.
**Headers:**
Content-Type: application/json
**Request Body:**
{
  "username": "john_doe",
  "password": "strongpassword",
  "role": "attendee"
}
### Login User
**Endpoint:** POST {{base_url}}/users/login
**Description:**  Login a user.
**Headers:**
Content-Type: application/json
**Request Body:**
{
  "username": "john_doe",
  "password": "strongpassword"
}
### Get Current User Info
**Endpoint:** GET {{base_url}}/users/me
**Description:**  Retrieve information about the currently authenticated user.
**Headers:**
Authorization: Bearer <YOUR_ACCESS_TOKEN>

### List All Attendees
**Endpoint:** GET {{base_url}}/users
**Description:**  Retrieve a list of all attendees.
**Headers:**
Authorization: Bearer <YOUR_ACCESS_TOKEN>

### Delete User
**Endpoint:** DELETE {{base_url}}/users/5/delete
**Description:**  Delete a user by their ID.
**Headers:**
Authorization: Bearer <YOUR_ACCESS_TOKEN>

### Get All Users (Admin Only)
**Endpoint:** GET {{base_url}}/users/all_users
**Description:**  Retrieve a list of all users (admin only).
**Headers:**
Authorization: Bearer <YOUR_ACCESS_TOKEN>

### Update User
**Endpoint:** PUT {{base_url}}/users/3/update
**Description:**  Update user details.
**Headers:**
Authorization: Bearer <YOUR_ACCESS_TOKEN>
Content-Type: application/json
**Request Body:**
{
  "username": "johnny_updated",
  "role": "organizer"
}

This documentation is generated based on the API collection provided. For more detailed information or updates, please refer to the openapi.json or Unified_Event_&_User_Management_API.json.
