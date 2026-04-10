# Readme_Integration_Test_Nakiwe

## Purpose
This document explains the integration test scenarios added to `pages/tests.py` for the application draft/resubmit lifecycle and overall request flow in the Django app.

## Test file location
- `pages/tests.py`

## Integration Test: `test_draft_resubmit_lifecycle`

### Setup
- `setUp` in test class creates:
  - student user (`user_type='student'`)
  - organization user (`user_type='organization'`)
  - active opportunity owned by organization

### Steps
1. Log in as the student using `self.client.force_login(self.student)`.
2. POST a draft application to `apply_to_opportunity`:
   - URL: `reverse('apply_to_opportunity', args=[opportunity.id])`
   - data: `{'message': 'Draft entry', 'action': 'save_draft'}`
   - `follow=True` to follow redirects
3. Verify draft state:
   - database `Application` record exists and status is `draft`
   - response contains success phrase `Application draft saved`
4. Verify `my_applications` includes draft entry:
   - GET `reverse('my_applications')`
   - status 200
   - context includes one application with status `draft`
5. Resubmit same opportunity as a final submit:
   - POST to same `apply_to_opportunity` URL
   - data: `{'message': 'Final submission', 'action': 'submit'}`
   - follow redirects
6. Verify pending state transition:
   - refresh `Application` from DB
   - status becomes `pending`
   - message updates to `'Final submission'`
   - response contains `Application submitted`

## Key behaviors verified
- draft saving through the application form route (student workflow)
- student can view draft applications in their application list
- the same application instance is reused for the same opportunity
- transition from `draft` to `pending` occurs correctly on submit
- user feedback is present in rendered response messages

## Running integration tests
From project root:

```bash
source venv/bin/activate
python manage.py test pages
```

(Optional to run only one test)
```bash
python manage.py test pages.tests.ApplicationTrackingTests.test_draft_resubmit_lifecycle
```
