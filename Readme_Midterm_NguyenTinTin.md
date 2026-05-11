# Midterm Implementation: AI-Assisted Messaging Feature
**Document:** Readme_Midterm_NguyenTinTin.md  
**Date:** March 30, 2026  
**Story Point Value:** 4  
**Status:** ✅ Complete and Tested

---

## Overview

This document describes the **AI-Assisted Messaging System** implemented for the Opportunity App. This feature enables volunteers to send messages to organizations and receive AI-powered FAQ suggestions in real-time, allowing volunteers to quickly get answers to common questions without waiting for organization responses.

### Business Value
- **Faster Response Times**: Volunteers get instant FAQ suggestions while typing messages
- **Improved Experience**: Self-service answers reduce frustration and increase engagement
- **Scalability**: AI suggestions handle high-volume inquiries without organization overhead
- **Data Collection**: Message history provides insights into volunteer questions and concerns

---

## Architecture Overview

The implementation follows a **three-tier architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│              FRONTEND (React/Vite)                              │
│  - Messaging UI components                                      │
│  - Real-time chat interface                                    │
│  - FAQ suggestion display                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP Requests (with proxy)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND (Django REST API)                           │
│  - Conversation management                                      │
│  - Message CRUD operations                                      │
│  - AI-powered FAQ generation                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │ SQL Queries
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE (PostgreSQL)                               │
│  - Conversations, Messages, FAQ Suggestions tables              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Newly Created Code Files

### 1. Backend - Models (`pages/models.py`)

**Purpose:** Define the database structure for conversations, messages, and FAQ suggestions.

**New Classes Added:**

#### `Conversation` Model
- Tracks interactions between a volunteer and an organization
- Maintains unique one-to-one relationships per volunteer-organization pair
- Auto-updates `last_message_at` timestamp

```python
class Conversation(models.Model):
    volunteer = ForeignKey(User, related_name='volunteer_conversations')
    organization = ForeignKey(User, related_name='organization_conversations')
    created_at = DateTimeField(auto_now_add=True)
    last_message_at = DateTimeField(auto_now=True)
```

#### `Message` Model
- Stores individual messages within conversations
- Tracks sender, content, timestamp, and read status
- Used for chat history and audit trails

```python
class Message(models.Model):
    conversation = ForeignKey(Conversation, related_name='messages')
    sender = ForeignKey(User, related_name='sent_messages')
    content = TextField()
    timestamp = DateTimeField(auto_now_add=True)
    is_read = BooleanField(default=False)
```

#### `FAQSuggestion` Model
- Stores AI-generated FAQ suggestions paired with messages
- Tracks relevance scores and user acceptance feedback

```python
class FAQSuggestion(models.Model):
    message = ForeignKey(Message, related_name='faq_suggestions')
    faq_content = TextField()
    relevance_score = FloatField(default=0.0)
    was_accepted = BooleanField(default=False)
```

---

### 2. Backend - Serializers (`pages/serializers.py`)

**Purpose:** Convert Django models to JSON for API responses, handling data transformation and nesting.

**New Serializers:**

#### `UserBasicSerializer`
- Minimal user information: ID, email, display name, user type
- Used in nested serializers to prevent circular references

#### `FAQSuggestionSerializer`
- Serializes FAQ suggestions with relevance scores
- Tracks acceptance feedback for ML model improvement

#### `MessageSerializer`
- Includes nested sender information and FAQ suggestions
- Converts timestamps to human-readable format
- Marks certain fields as read-only for security

#### `ConversationListSerializer`
- Displays all conversations for a user
- Dynamically shows the "other user" (not current user)
- Shows preview of last message
- Orders by most recent message first

#### `ConversationDetailSerializer`
- Full conversation with complete message history
- Includes all participant details
- Used when opening a specific conversation

---

### 3. Backend - FAQ Service (`pages/faq_service.py`)

**Purpose:** AI-powered suggestion engine using rule-based matching (with OpenAI integration ready).

**Key Functions:**

#### `FAQService.generate_suggestions(message_content, num_suggestions=3)`
- Analyzes volunteer message content
- Returns top N most relevant FAQ suggestions
- Scores suggestions by relevance (0.0 to 1.0)

**How It Works:**
1. **Rule-Based Matching** (default):
   - Maintains database of common FAQs with keywords
   - Matches message against FAQ keywords
   - Scores based on keyword density
   - Returns top 3 by relevance

2. **OpenAI Integration** (optional):
   - If `OPENAI_API_KEY` is set, uses GPT-3.5-turbo
   - Sends message to OpenAI API
   - Returns semantically relevant FAQ suggestions
   - Falls back to rule-based if API fails

**Sample FAQs in Database:**
- Volunteer hours and schedule
- Location and parking information
- Volunteer requirements and training
- Contact information
- Volunteer benefits and recognition

---

### 4. Backend - REST API Views (`pages/views.py`)

**Purpose:** HTTP endpoints for frontend-to-backend communication.

#### `ConversationListView` (GET `/api/conversations/`)
**Returns:** List of all conversations with previews
```json
[
  {
    "id": 1,
    "other_user": {
      "id": 3,
      "email": "redcross@test.com",
      "display_name": "Red Cross",
      "user_type": "organization"
    },
    "created_at": "2026-03-30T10:00:00Z",
    "last_message_at": "2026-03-30T12:00:00Z",
    "last_message": "Welcome! What are your interests?"
  }
]
```

#### `ConversationDetailView` (GET `/api/conversations/<id>/`)
**Returns:** Complete conversation with all messages
```json
{
  "id": 1,
  "volunteer": {...},
  "organization": {...},
  "messages": [{...}, {...}],
  "created_at": "2026-03-30T10:00:00Z"
}
```

#### `CreateConversationView` (POST `/api/conversations/create/`)
**Request Body:**
```json
{
  "organization_id": 3
}
```
**Action:** Initiates new conversation with specified organization

#### `MessageListView` (GET `/api/messages/?conversation_id=1`)
**Returns:** All messages in a conversation
```json
[
  {
    "id": 101,
    "sender": {"id": 1, "display_name": "Tin Tin Do"},
    "content": "Hi! Can I volunteer?",
    "timestamp": "2026-03-30T11:00:00Z",
    "is_read": true,
    "faq_suggestions": [{...}]
  }
]
```

#### `SendMessageView` (POST `/api/messages/send/`)
**Request Body:**
```json
{
  "conversation_id": 1,
  "content": "What are your volunteer hours?"
}
```
**Action:** Sends message and triggers FAQ suggestion generation

#### `FAQSuggestionView` (POST `/api/faq-suggestions/`)
**Request Body:**
```json
{
  "message_content": "What are your volunteer hours?"
}
```
**Returns:** Array of 3 suggested FAQs with relevance scores
```json
[
  {
    "faq_content": "Our organization is open Monday-Friday, 9AM-5PM...",
    "relevance_score": 0.95
  },
  {
    "faq_content": "Extended hours available for special events...",
    "relevance_score": 0.87
  }
]
```

#### `GetOrganizationsView` (GET `/api/organizations/`)
**Returns:** List of all organizations for volunteer to contact
```json
[
  {
    "id": 3,
    "email": "redcross@test.com",
    "display_name": "Red Cross"
  }
]
```

---

### 5. Frontend - Main Component (`frontend/src/components/Messaging.jsx`)

**Purpose:** Container component managing all messaging state and API interactions.

**Key Features:**
- Fetches and displays list of conversations
- Handles message sending and receiving
- Manages FAQ suggestion generation
- Provides CSRF token for security
- Auto-scrolls to latest messages

**User Workflow:**
1. Component loads → fetches all conversations
2. User selects a conversation
3. Messages load automatically
4. User types and sends message
5. FAQ suggestions appear below
6. Conversation list updates with new timestamp

---

### 6. Frontend - Conversation List (`frontend/src/components/ConversationList.jsx`)

**Purpose:** Sidebar component showing all conversations.

**Key Features:**
- Displays organization name and last message preview
- "New Conversation" button to start messaging with organizations
- Shows date of last message
- Highlights currently selected conversation
- Dropdown list of available organizations

**UI Pattern:**
```
┌─────────────────────────────────┐
│ Conversations        [+ New]    │
├─────────────────────────────────┤
│ 🏢 Red Cross                    │
│ "Thanks for volunteers..."      │
│ 03/30/2026                      │
├─────────────────────────────────┤
│ 🏢 Food Bank                    │
│ "Welcome! How can we help?"     │
│ 03/29/2026                      │
└─────────────────────────────────┘
```

---

### 7. Frontend - Chat Window (`frontend/src/components/ChatWindow.jsx`)

**Purpose:** Main message display area.

**Key Features:**
- Shows conversation partner name in header
- Displays messages with sender attribution
- Color-coded: Blue for volunteer, Gray for organization
- Timestamps on each message
- Auto-scroll to latest message
- "No messages yet" state for new conversations

**Visual Layout:**
```
┌───────────────────────────────────┐
│ Red Cross        [Organization]   │
├───────────────────────────────────┤
│                                   │
│ ┌─────────────────────────────┐  │
│ │ Hi! Can I volunteer?   11:00│  │  (Volunteer message - right)
│ └─────────────────────────────┘  │
│                                   │
│ ┌─────────────────────────────┐  │
│ │ Yes! Here are our hours... │12:00  (Org message - left)
│ └─────────────────────────────┘  │
│                                   │
└───────────────────────────────────┘
```

---

### 8. Frontend - Message Input (`frontend/src/components/MessageInput.jsx`)

**Purpose:** Text input and send button area.

**Key Features:**
- Textarea input (allows multi-line with Shift+Enter)
- Send button (disabled until text entered)
- Loading state during message transmission
- CSRF token automatically included in requests
- Character counter (optional enhancement)

**Keyboard Shortcuts:**
- `Enter` = Send message
- `Shift+Enter` = New line in message

---

### 9. Frontend - FAQ Suggestions (`frontend/src/components/FAQSuggestions.jsx`)

**Purpose:** Display AI-generated FAQ suggestions after sending a message.

**Features:**
- Shows up to 3 suggestions with relevance percentages
- Hover effects for interactivity
- Clickable suggestions (expandable for future use)
- Hidden when no suggestions available
- Light blue background to distinguish from chat

**Visual Example:**
```
💡 AI-Assisted FAQ Suggestions:

┌─────────────────────────────────────┐
│ Suggestion 1 (Relevance: 95%)      │
│ Our volunteer hours are Monday...   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Suggestion 2 (Relevance: 87%)      │
│ Extended hours available on...      │
└─────────────────────────────────────┘
```

---

### 10. Frontend - Vite Configuration (`frontend/vite.config.js`)

**Purpose:** Configure frontend build tool with API proxy.

**Key Addition:**
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    }
  }
}
```
**Benefit:** Frontend can call `/api/conversations/` and it's automatically forwarded to Django backend at port 8000.

---

### 11. Backend - Settings Configuration (`opportunity_app/settings.py`)

**Purpose:** Configure Django for REST API and CORS.

**Updates Made:**
1. Added `rest_framework` to `INSTALLED_APPS`
2. Added `corsheaders` to `INSTALLED_APPS` and `MIDDLEWARE`
3. Configured CORS for localhost:5173 (frontend)
4. Set default REST permissions to `IsAuthenticated`

---

### 12. Backend - URL Routing (`pages/urls.py`)

**Purpose:** Map HTTP request paths to API view functions.

**New Routes:**
```
GET    /api/conversations/              → List conversations
GET    /api/conversations/<id>/         → Conversation detail
POST   /api/conversations/create/       → Create conversation
GET    /api/messages/                   → List messages
POST   /api/messages/send/              → Send message
PUT    /api/messages/<id>/read/         → Mark as read
GET    /api/organizations/              → List organizations
POST   /api/faq-suggestions/            → Generate FAQ suggestions
```

---

### 13. Database Migrations (`pages/migrations/0002_conversation_message_faqsuggestion.py`)

**Purpose:** Define database schema changes.

**Tables Created:**
1. `pages_conversation` - Stores conversation metadata
2. `pages_message` - Stores individual messages
3. `pages_faqsuggestion` - Stores AI-generated suggestions

---

### 14. Management Command (`pages/management/commands/create_test_data.py`)

**Purpose:** Populate database with sample data for testing.

**Data Created:**
- 1 Volunteer user (email: volunteer@test.com)
- 2 Organization users (Red Cross, Food Bank)
- 2 Conversations with sample messages

**Usage:**
```bash
python manage.py create_test_data
```

---

## How Everything Works Together

### User Flow: Sending a Message

```
1. USER OPENS BROWSER
   ↓
2. Frontend loads conversations from GET /api/conversations/
   ↓
3. User selects a conversation
   ↓
4. Messages load from GET /api/messages/?conversation_id=1
   ↓
5. User types message and clicks Send
   ↓
6. POST /api/messages/send/
   ├─ Message saved to database
   └─ FAQ suggestions generated
   ↓
7. POST /api/faq-suggestions/
   ├─ Message analyzed by FAQService
   ├─ Top 3 suggestions returned with relevance scores
   └─ Displayed in suggestion panel
   ↓
8. UI updates in real-time with new message and suggestions
```

### FAQ Suggestion Process

```
Volunteer Message: "What are your hours?"
        ↓
FAQService.generate_suggestions()
        ↓
Keyword Matching:
├─ "hours" matches FAQ about schedule
├─ "availability" matches FAQ about hours  
├─ Score: 0.95, 0.87
        ↓
Return to Frontend:
└─ Display "Our organization is open Mon-Fri..."
   Display "Extended hours available..."
```

---

## Testing the Feature

### Using the API Directly

**List all conversations:**
```bash
curl http://127.0.0.1:8000/api/conversations/
```

**Get a specific conversation:**
```bash
curl http://127.0.0.1:8000/api/conversations/1/
```

**Send a message:**
```bash
curl -X POST http://127.0.0.1:8000/api/messages/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "content": "What are your volunteer hours?"
  }'
```

**Get FAQ suggestions:**
```bash
curl -X POST http://127.0.0.1:8000/api/faq-suggestions/ \
  -H "Content-Type: application/json" \
  -d '{
    "message_content": "What are your volunteer hours?"
  }'
```

### Using the Frontend Interface

1. Open http://localhost:5173
2. Click "Conversations" section
3. Click conversation to open chat
4. Type message: "What are volunteer hours?"
5. Click Send
6. See FAQ suggestions appear below input

---

## Technology Stack

### Backend
- **Framework:** Django 5.2.12
- **API:** Django REST Framework 3.17.1
- **Database:** PostgreSQL
- **CORS:** django-cors-headers 4.9.0

### Frontend
- **Framework:** React 18.3.1
- **Build Tool:** Vite 5.4.21
- **Testing:** Vitest 3.2.4

### AI Integration
- **Default:** Rule-based keyword matching
- **Optional:** OpenAI GPT-3.5-turbo (when `OPENAI_API_KEY` set)

---

## Summary

The **AI-Assisted Messaging System** provides a complete end-to-end solution for volunteer-organization communication with intelligent FAQ suggestions. The implementation includes:

✅ **14 new files/components** created  
✅ **8 REST API endpoints** for message operations  
✅ **5 React components** for beautiful UI  
✅ **AI-powered FAQ service** with keyword matching and OpenAI support  
✅ **Database schema** supporting conversations, messages, and suggestions  
✅ **Complete CORS & proxy configuration** for development  
✅ **Test data** pre-populated for immediate testing  

**Total Story Points:** 4  
**Status:** Complete and tested ✅
