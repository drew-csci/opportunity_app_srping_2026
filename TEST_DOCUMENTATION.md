# Messaging Feature Test Suite

## Overview
The test suite in `pages/test_messaging.py` contains comprehensive tests for the organization messaging feature. It covers 5 main test classes with 24 test cases total.

## Test Classes & Cases

### 1. MessagingInboxTestCase (6 tests)
Tests for the organization inbox listing view.

- **test_organization_can_access_inbox**
  - Verifies organizations can view their inbox
  - Checks for correct template and HTTP 200 response

- **test_student_cannot_access_inbox**
  - Ensures students are redirected (HTTP 302) when accessing inbox
  - Prevents unauthorized access to organization features

- **test_unauthenticated_user_redirected_to_login**
  - Verifies unauthenticated users are redirected to login
  - Ensures proper authentication enforcement

- **test_inbox_displays_messages_newest_first**
  - Creates two messages at different times
  - Verifies newest message appears first in the list
  - Tests sorting order (descending by created_at)

- **test_unread_count_displayed_correctly**
  - Creates mix of read and unread messages
  - Verifies accurate unread count in context
  - Ensures read/unread status is tracked

- **test_inbox_shows_only_recipient_messages**
  - Creates messages to multiple organizations
  - Verifies each org only sees their own messages
  - Tests message filtering by recipient

### 2. MessageDetailTestCase (6 tests)
Tests for viewing individual messages and marking as read.

- **test_can_view_message_detail**
  - Verifies organization can access message detail view
  - Checks correct template usage
  - Confirms message appears in response context

- **test_viewing_message_marks_as_read**
  - Creates unread message
  - Views the message
  - Verifies is_read flag changes to True
  - Tests automatic read status update

- **test_cannot_view_others_messages**
  - Attempts to access message not addressed to user
  - Expects HTTP 404 Not Found response
  - Ensures message privacy

- **test_reply_form_displayed**
  - Verifies reply form is present on detail page
  - Confirms content field exists in form
  - Tests form context passing

### 3. MessageReplyTestCase (7 tests)
Tests for replying to messages (both success and error cases).

- **test_successful_reply** ✓
  - Organization sends reply to message
  - Verifies reply is saved to database
  - Confirms reply contains correct content and sender
  - Tests full reply workflow

- **test_empty_reply_validation** ✗
  - Attempts to send empty reply
  - Verifies form validation error is shown
  - Confirms "Reply cannot be empty." error message
  - Ensures reply is NOT saved
  - **Tests unsuccessful scenario as requested**

- **test_whitespace_only_reply_validation** ✗
  - Attempts to send whitespace-only reply
  - Verifies same validation error as empty reply
  - Tests edge case with spaces/tabs/newlines
  - Ensures invalid replies are rejected

- **test_multiple_replies**
  - Sends two replies to same message
  - Verifies both are saved
  - Tests ability to have conversation thread

- **test_replies_ordered_chronologically**
  - Creates multiple replies
  - Verifies they appear in creation order
  - Tests reply ordering (ascending by created_at)

- **test_reply_contains_sender_info**
  - Sends reply and verifies sender information
  - Checks timestamp is recorded
  - Tests metadata preservation

### 4. SendMessageTestCase (3 tests)
Tests for students sending messages to organizations.

- **test_student_can_send_message**
  - Student sends message with subject and content
  - Redirects to success page
  - Verifies message saved with correct sender/recipient
  - Tests full send workflow

- **test_empty_message_content_validation**
  - Attempts to send message with empty content
  - Verifies form validation error shown
  - Confirms "Message content cannot be empty." error
  - Ensures invalid message not saved

- **test_message_with_optional_subject**
  - Sends message without subject (optional field)
  - Verifies message sends successfully
  - Tests optional field handling

### 5. UnreadCountAPITestCase (3 tests)
Tests for unread message count API endpoint.

- **test_get_unread_count_for_organization**
  - Organization queries unread count endpoint
  - Creates 2 unread, 1 read message
  - Verifies API returns correct count (2)
  - Tests JSON response format

- **test_get_unread_count_for_student**
  - Student queries unread count endpoint
  - Expects count to be 0 (students don't receive org messages)
  - Tests permission-aware response

- **test_unread_count_updates_after_reading**
  - Gets initial unread count
  - Marks message as read
  - Re-queries API
  - Verifies count decrements
  - Tests real-time updates

## Test Scenarios Covered

### Success Cases ✓
1. Organization accesses inbox
2. Inbox displays messages sorted newest first
3. Unread count is accurate
4. Only recipient sees their messages
5. Message detail view works
6. Viewing message marks as read
7. Successful reply is saved and displayed
8. Multiple replies can be created
9. Replies ordered chronologically
10. Students can send messages
11. Optional subject field works
12. API returns correct unread count

### Failure Cases ✗
1. Student cannot access organization inbox (redirected)
2. Empty reply validation with error message
3. Whitespace-only reply validation
4. Empty message content validation
5. Users cannot view others' messages (404)
6. Unauthenticated users redirected to login

## Running the Tests

### Option 1: Django Management Command
```bash
python manage.py test pages.test_messaging -v 2
```

### Option 2: Specific Test Class
```bash
python manage.py test pages.test_messaging.MessagingInboxTestCase
```

### Option 3: Specific Test Method
```bash
python manage.py test pages.test_messaging.MessageReplyTestCase.test_empty_reply_validation
```

### Option 4: Using the provided script
```bash
python run_tests.py
```

## Test Coverage

The test suite covers:
- **Models**: Message, MessageReply creation and relationships
- **Views**: All 6 messaging views with different user types
- **Forms**: MessageForm, MessageReplyForm validation
- **Templates**: inbox.html, message_detail.html, send_message.html
- **Permissions**: Access control for organizations vs students
- **API**: Unread count endpoint
- **Edge Cases**: Empty fields, whitespace, sorting, multiple operations

## Key Assertions

### Form Validation Tests
```python
self.assertFormError(response, 'form', 'content', 'Reply cannot be empty.')
self.assertFormError(response, 'form', 'content', 'Message content cannot be empty.')
```

### Database Tests
```python
self.assertEqual(self.message.replies.count(), 1)
self.assertEqual(Message.objects.count(), 1)
```

### Template & Context Tests
```python
self.assertTemplateUsed(response, 'pages/inbox.html')
self.assertEqual(response.context['unread_count'], 2)
```

### Permission & Access Tests
```python
self.assertEqual(response.status_code, 404)  # Cannot view others' messages
self.assertIn('screen1', response.url)  # Student redirected
```

## Notes

- All tests use Django's TestCase for database isolation
- Each test creates fresh test data via setUp()
- Tests use Client() to simulate HTTP requests
- Email-based login used (matches custom authentication)
- Tests verify both HTTP status codes and template rendering
- Form validation errors are tested explicitly
- **Empty reply validation is tested with descriptive error message**
