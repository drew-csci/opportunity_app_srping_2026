# Messaging Feature Test Summary

## Test File Location
`pages/test_messaging.py` - 19,205 bytes, 24 comprehensive test cases

## Quick Test Reference

### ✓ Successful Reply Test
**Test**: `MessageReplyTestCase.test_successful_reply`
```python
# Organization sends reply to a message
self.client.post(
    reverse('message_detail', args=[self.message.id]),
    {'content': 'This is a test reply'}
)

# Assertions:
# - Reply is saved to database
# - Message.replies.count() == 1
# - Reply content matches input
# - Reply sender is the organization
```

### ✗ Empty Reply Validation Test
**Test**: `MessageReplyTestCase.test_empty_reply_validation`
```python
# Attempt to send empty reply
self.client.post(
    reverse('message_detail', args=[self.message.id]),
    {'content': ''}
)

# Assertions:
# - Form validation error is displayed
# - Error message: "Reply cannot be empty."
# - Reply is NOT saved (replies.count() == 0)
# - User stays on message_detail page with error
```

### ✗ Whitespace-Only Reply Test
**Test**: `MessageReplyTestCase.test_whitespace_only_reply_validation`
```python
# Attempt to send whitespace-only reply
self.client.post(
    reverse('message_detail', args=[self.message.id]),
    {'content': '   \n  \t  '}
)

# Same validation as empty reply
```

## Test Execution Examples

```bash
# Run all 24 messaging tests
python manage.py test pages.test_messaging -v 2

# Run only reply tests (success & failure)
python manage.py test pages.test_messaging.MessageReplyTestCase -v 2

# Run specific validation test
python manage.py test pages.test_messaging.MessageReplyTestCase.test_empty_reply_validation

# Run with coverage reporting
coverage run --source='pages' manage.py test pages.test_messaging
coverage report
```

## Feature Coverage

### Messages Features Tested ✓
- Organization can view inbox
- Messages sorted by newest first
- Unread message count displayed
- Viewing message marks as read
- Student can send messages to organization
- Student can view success confirmation

### Reply Features Tested ✓
- Organization can reply successfully
- Reply content is preserved
- Reply sender is recorded
- Multiple replies can be created
- Replies ordered chronologically

### Validation Features Tested ✗
- Empty reply shows error: "Reply cannot be empty."
- Whitespace-only reply shows error
- Empty message content shows error
- Form-level validation working

### Security & Permissions Tested
- Student cannot access organization inbox
- Organization cannot view others' messages
- Unauthenticated users redirected to login
- Message privacy enforced

## Test Data Structure

Each test uses:
- Test Student: `student@test.com` (user_type='student')
- Test Organization: `org@test.com` (user_type='organization')
- Test Messages: Created with various read/unread states
- Test Replies: Created to simulate conversation

## Form Validation Examples

From `pages/forms.py`:

```python
class MessageReplyForm(forms.ModelForm):
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError('Reply cannot be empty.')
        return content

class MessageForm(forms.ModelForm):
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError('Message content cannot be empty.')
        return content
```

## Assertion Methods Used

```python
# Status codes
self.assertEqual(response.status_code, 200)  # Success
self.assertEqual(response.status_code, 302)  # Redirect
self.assertEqual(response.status_code, 404)  # Not found

# Form errors (for validation testing)
self.assertFormError(response, 'form', 'content', 'Reply cannot be empty.')

# Database counts
self.assertEqual(self.message.replies.count(), 1)
self.assertEqual(Message.objects.count(), 2)

# Templates
self.assertTemplateUsed(response, 'pages/inbox.html')

# Context data
self.assertEqual(response.context['unread_count'], 2)

# URLs
self.assertIn('login', response.url)
```

## Key Test Assertions for Requirements

### Requirement: Empty reply should show helpful message
✓ **Implemented in test_empty_reply_validation**
```python
# Checks that form error is exactly:
self.assertFormError(response, 'form', 'content', 'Reply cannot be empty.')
```

### Requirement: Successful reply should work
✓ **Implemented in test_successful_reply**
```python
# Verifies reply is created and accessible
self.assertEqual(self.message.replies.count(), 1)
reply = self.message.replies.first()
self.assertEqual(reply.content, 'This is a test reply')
```

### Requirement: Messages sorted by order of receipt
✓ **Implemented in test_inbox_displays_messages_newest_first**
```python
# Creates two messages and verifies newest is first
messages_list = response.context['messages']
self.assertEqual(messages_list[0].id, msg2.id)  # Newer message
self.assertEqual(messages_list[1].id, msg1.id)  # Older message
```

## Implementation Quality

- **24 Test Cases**: Comprehensive coverage of all features
- **6 Test Classes**: Organized by feature area
- **Test Isolation**: Each test is independent with setUp/tearDown
- **Database Isolation**: Uses Django TestCase for transaction rollback
- **No Side Effects**: Tests don't interfere with each other
- **Clear Names**: Test method names describe what they test
- **Good Documentation**: Comments explain test intent

---

**Total Test Methods**: 24
**Lines of Test Code**: 600+
**Features Tested**: 15+
**Edge Cases**: 8+
**Error Scenarios**: 5+
