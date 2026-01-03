# Attendance & Payroll System v2.0 - Development Rules

**Status:** Planning Phase - Not Yet Implemented
**Version:** 2.0.0
**Feature Branch:** `feature/v2.0-attendance-payroll`
**Specification:** `docs/specifications/v2.0-flexible-attendance-payroll.md`

---

## Overview

This document provides critical rules and guidelines for developing the Attendance & Payroll System v2.0. This is a MAJOR feature that introduces attendance-based payroll and flexible tracking controls alongside the existing time-based system.

**READ THE FULL SPECIFICATION FIRST:** Before working on ANY aspect of this feature, read `docs/specifications/v2.0-flexible-attendance-payroll.md` in its entirety.

---

## Critical Rules

### 🚨 MUST FOLLOW FOR V2.0 DEVELOPMENT

1. **ALWAYS maintain backward compatibility**
   - Existing time-based payroll MUST continue working unchanged
   - Default values for new fields MUST preserve current behavior
   - Never break existing clock-in/out functionality

2. **ALWAYS scope queries by `join_code`**
   - Every `AttendanceLog` query MUST include `join_code` filter
   - Multi-tenancy is CRITICAL - data leakage is unacceptable
   - See `.claude/rules/multi-tenancy.md` for complete rules

3. **ALWAYS follow the implementation phases**
   - Work must proceed in the order defined in the specification
   - Each phase is a separate PR
   - Never merge incomplete phases

4. **ALWAYS create migrations for schema changes**
   - Every model change requires a migration
   - Test upgrade AND downgrade before committing
   - See `.claude/rules/database-migrations.md` for workflow

5. **ALWAYS write tests**
   - Every new route needs tests
   - Every new calculation method needs tests
   - Multi-tenancy scoping MUST be tested
   - See `.claude/rules/testing.md` for requirements

6. **ALWAYS update documentation**
   - Update CHANGELOG.md for every PR
   - Update technical docs for schema/architecture changes
   - Update user guides for UI changes

7. **NEVER break multi-tenancy scoping**
   - `AttendanceLog` queries MUST filter by `join_code`
   - Teacher can only see students in their class periods
   - Student can only see their own attendance

8. **NEVER skip conflict resolution logic**
   - Duplicate attendance entries MUST be handled according to `conflict_resolution` setting
   - Teacher priority MUST be respected when configured

---

## Key Concepts

### Payroll Types

**Time-Based (Existing)**
- Students clock in and out
- Pay = duration worked × hourly rate
- Uses `TapEvent` table
- Hall passes pause time

**Attendance-Based (New)**
- Students mark present/absent/late
- Pay = days present × flat rate
- Uses `AttendanceLog` table
- Hall passes don't affect pay

### Tracking Controls

**Student Tracking** (`student_tracking_enabled`)
- If True: Students can mark their own attendance
- If False: Only teacher can mark attendance

**Teacher Tracking** (`teacher_tracking_enabled`)
- If True: Teacher can mark attendance via Daily Attendance interface
- If False: Teacher cannot use Daily Attendance interface (view-only in log)

**Period-Level Control** (`attendance_enabled` per `TeacherBlock`)
- Per-period override for student tracking
- If False: Students cannot mark attendance for that specific period

### Conflict Resolution

When both student and teacher can mark attendance:

**Last Entry Wins** (`conflict_resolution = 'last_entry'`)
- Most recent entry is used
- Earlier entries are overwritten

**Teacher Priority** (`conflict_resolution = 'teacher_priority'`)
- Teacher entry always takes precedence
- Student cannot overwrite teacher entry

---

## Database Schema Rules

### New Table: `AttendanceLog`

**Required Fields:**
- `student_id` - FK to Student
- `join_code` - Multi-tenancy scoping (ALWAYS filter by this!)
- `timestamp` - When attendance occurred
- `status` - Attendance state (values depend on `payroll_type`)
- `period` - Which class period
- `created_by` - 'student' or 'teacher'
- `entry_type` - 'manual', 'hall_pass', 'clock'
- `is_system_generated` - True for hall pass entries

**Status Values:**
- Attendance-based: `'present'`, `'absent'`, `'late'`
- Time-based: `'inactive'`, `'start_work'`, `'done'`

**Indexes Required:**
```python
Index('ix_attendance_join_code_timestamp', 'join_code', 'timestamp')
Index('ix_attendance_student_join_code', 'student_id', 'join_code')
```

### Modified Table: `PayrollSettings`

**New Fields:**
- `payroll_type` - 'time_based' or 'attendance_based' (default: 'time_based')
- `attendance_flat_rate` - Decimal, pay per present day (default: 0.00)
- `student_tracking_enabled` - Boolean (default: True)
- `teacher_tracking_enabled` - Boolean (default: False)
- `conflict_resolution` - 'last_entry' or 'teacher_priority' (default: 'last_entry')

### Modified Table: `TeacherBlock`

**New Field:**
- `attendance_enabled` - Boolean, per-period control (default: True)

---

## Query Patterns

### ✅ CORRECT: Scoped by `join_code`

```python
# Get attendance for a student in a specific class
attendance = AttendanceLog.query.filter_by(
    student_id=student_id,
    join_code=current_join_code  # CRITICAL!
).all()

# Get all attendance for a period on a date
attendance = AttendanceLog.query.filter_by(
    join_code=current_join_code,  # CRITICAL!
    period=period_name
).filter(
    func.date(AttendanceLog.timestamp) == target_date
).all()

# Count present days for payroll
present_count = AttendanceLog.query.filter_by(
    student_id=student_id,
    join_code=current_join_code,  # CRITICAL!
    status='present'
).filter(
    AttendanceLog.timestamp >= start_date,
    AttendanceLog.timestamp <= end_date
).count()
```

### ❌ WRONG: Not scoped

```python
# NEVER DO THIS - Data leakage!
attendance = AttendanceLog.query.filter_by(
    student_id=student_id
).all()

# NEVER DO THIS - Cross-period leakage!
attendance = AttendanceLog.query.filter(
    AttendanceLog.timestamp >= start_date
).all()
```

---

## Business Logic Rules

### Attendance Entry Creation

**Function:** `create_attendance_entry()`

**MUST:**
1. Check for existing entry (same student, join_code, period, date)
2. Apply conflict resolution if entry exists
3. Validate status value matches payroll_type
4. Set `created_by` correctly ('student' or 'teacher')
5. Set `modified_by` and `modified_at` if updating existing entry

**MUST NOT:**
- Allow editing of system-generated entries (`is_system_generated=True`)
- Create entries without `join_code`
- Create entries with invalid status for payroll_type

### Payroll Calculation

**Function:** `calculate_payroll()`

**MUST:**
1. Check `payroll_type` from `PayrollSettings`
2. Route to appropriate calculation method
3. Scope all queries by `join_code`
4. Return consistent structure regardless of type

**Time-Based Calculation:**
- Use existing `TapEvent` data
- Calculate duration worked
- Multiply by hourly rate
- Apply bonuses/deductions

**Attendance-Based Calculation:**
- Query `AttendanceLog` for 'present' status
- Count entries in pay period
- Multiply by `attendance_flat_rate`
- Return result

### Hall Pass Integration

**Function:** `create_hall_pass()`

**MUST:**
1. Check `payroll_type` from `PayrollSettings`
2. If time-based: Pause time tracking (existing behavior)
3. If attendance-based: Do NOT pause time (new behavior)
4. Always create `AttendanceLog` entry with `entry_type='hall_pass'`, `is_system_generated=True`
5. Set `created_by='teacher'` if teacher-initiated

**Teacher-Initiated Hall Pass:**
- Only available if `student_tracking_enabled=False`
- Teacher selects student and destination
- System creates pass on behalf of student
- Student can still return themselves (or teacher can return)

---

## UI Component Rules

### Daily Attendance Tab

**Visibility:**
- Only shown if `teacher_tracking_enabled = True`
- If False, tab is hidden entirely

**Data Scope:**
- Only shows students for current `join_code`
- Period selector tabs MUST filter by `join_code`

**Features:**
- Bulk "Apply to Selected" for efficiency
- Per-period attendance control toggles
- Statistics panel (present/absent/late counts)
- Auto-save with warning on unsaved changes
- Only shows current day (not historical dates)

**Status Dropdown:**
- Show values based on `payroll_type`:
  - Time-based: Inactive, Start Work, Done
  - Attendance-based: Present, Absent, Late

### Attendance Log Tab

**Visibility:**
- Always shown (even if `teacher_tracking_enabled = False`)

**Data Scope:**
- MUST filter by `join_code` in all queries
- Period filter MUST only show periods for current teacher
- Student name filter MUST only show students in current `join_code`

**Features:**
- Filterable by date range, period, status, created_by
- Sortable columns
- Pagination (20 entries per page default)
- Details panel when entry selected
- Edit/Delete functionality with restrictions

**Edit Restrictions:**
- Cannot edit entries where `is_system_generated = True`
- Edit button disabled for hall pass entries
- Tooltip explains why: "System-generated entries cannot be edited"

**Delete Restrictions:**
- Cannot delete entries where `is_system_generated = True`
- Confirm dialog if entry affects unpaid payroll
- Warning: "This may impact student payroll calculations"

### Payroll Settings Page

**New Section:** "Attendance & Payroll Configuration"

**Validation:**
- If "Attendance-Based" selected, `attendance_flat_rate` is required
- At least one tracking method must be enabled
- Conflict resolution only shown if both tracking methods enabled

**Conditional Display:**
- `attendance_flat_rate` field only shown if `payroll_type = 'attendance_based'`
- Conflict resolution only shown if both `student_tracking_enabled` and `teacher_tracking_enabled` are True

### Student Clock-In Page

**Conditional Behavior:**

**If `student_tracking_enabled = False`:**
- Show message: "Your teacher is managing attendance for this class period."
- Display current status (if marked by teacher)
- No action buttons

**If `payroll_type = 'attendance_based'` and `student_tracking_enabled = True`:**
- Show "Check In" button (not "Clock In")
- After check-in: Show "You're marked present for today's class!"
- No "Check Out" button (not needed for attendance-based)

**If `payroll_type = 'time_based'` and `student_tracking_enabled = True`:**
- Existing clock-in/out behavior unchanged

**Period-Level Override:**
- If `attendance_enabled = False` for current period, hide all attendance UI
- Show message: "Attendance tracking is disabled for this period."

---

## Implementation Phases

### Phase Order (MUST FOLLOW)

1. **Database Schema** - Migration + models
2. **Settings UI** - Payroll Settings configuration
3. **Attendance Utilities** - Core helper functions
4. **Daily Attendance Interface** - Teacher entry UI
5. **Attendance Log Interface** - Historical view + edit
6. **Payroll Calculation Update** - Handle both types
7. **Hall Pass Integration** - Update behavior
8. **Student UI Updates** - Conditional UIs
9. **Reporting & Analytics** - New reports
10. **Documentation & Polish** - User docs + final QA

**Each phase is a separate PR.**
**Do NOT start next phase until previous is merged.**

---

## Testing Requirements

### Unit Tests (Required for Every Phase)

**Attendance Utilities:**
- `test_create_attendance_entry_new()`
- `test_create_attendance_entry_duplicate_last_entry_wins()`
- `test_create_attendance_entry_duplicate_teacher_priority()`
- `test_create_attendance_entry_backdating()`
- `test_can_edit_entry_manual()`
- `test_can_edit_entry_system_generated()`

**Payroll Calculation:**
- `test_calculate_payroll_time_based()`
- `test_calculate_payroll_attendance_based()`
- `test_calculate_payroll_mixed_periods()`

**Hall Pass Integration:**
- `test_hall_pass_time_based_pauses_time()`
- `test_hall_pass_attendance_based_no_pause()`
- `test_hall_pass_creates_attendance_log()`
- `test_teacher_initiated_hall_pass()`

### Integration Tests (Required for UI Phases)

**Daily Attendance:**
- `test_daily_attendance_visibility()`
- `test_daily_attendance_bulk_apply()`
- `test_daily_attendance_period_switching()`
- `test_daily_attendance_auto_save()`

**Attendance Log:**
- `test_attendance_log_filtering()`
- `test_attendance_log_edit()`
- `test_attendance_log_edit_system_generated_blocked()`
- `test_attendance_log_delete()`
- `test_attendance_log_bulk_add()`

**Settings:**
- `test_save_payroll_type()`
- `test_save_tracking_controls()`
- `test_validation_attendance_rate_required()`

### Multi-Tenancy Tests (CRITICAL - MUST PASS)

- `test_attendance_log_scoped_by_join_code()`
- `test_daily_attendance_only_shows_own_students()`
- `test_payroll_calculation_scoped_by_join_code()`
- `test_bulk_operations_scoped_by_join_code()`
- `test_attendance_log_filtering_scoped_by_join_code()`

**Multi-tenancy tests MUST be included in EVERY phase.**

### Regression Tests (Required Before Merge to Main)

- `test_existing_time_based_payroll_unchanged()`
- `test_existing_clock_in_out_unchanged()`
- `test_existing_hall_pass_unchanged()`
- `test_existing_reports_unchanged()`
- `test_existing_tap_event_data_preserved()`

---

## Code Organization

### New Files to Create

```
app/
├── routes/
│   └── attendance.py           # New blueprint for attendance management
├── utils/
│   └── attendance_utils.py     # Helper functions for attendance logic
└── forms_attendance.py         # Forms for attendance entry/editing

templates/
└── attendance/
    ├── management.html         # Main attendance management page
    ├── daily_tab.html          # Daily attendance entry interface
    ├── log_tab.html            # Historical log view
    ├── edit_modal.html         # Edit entry dialog
    └── bulk_add_modal.html     # Bulk add dialog

tests/
└── test_attendance.py          # Comprehensive attendance tests
```

### Files to Modify

```
app/
├── models.py                   # Add AttendanceLog, modify PayrollSettings, TeacherBlock
├── payroll.py                  # Update payroll calculation
├── routes/
│   ├── admin.py               # Add attendance menu item
│   └── student.py             # Update clock-in behavior
└── __init__.py                # Register attendance blueprint

templates/
├── admin_dashboard.html        # Add "Attendance" menu item
├── productivity/
│   └── clock_in.html          # Conditional UI based on settings
└── settings/
    └── payroll_settings.html  # Add new payroll options
```

---

## Common Pitfalls

### ❌ Forgetting Multi-Tenancy Scoping

**Problem:** Queries don't filter by `join_code`, causing data leakage.

**Solution:**
- Every `AttendanceLog` query MUST include `.filter_by(join_code=current_join_code)`
- Review `.claude/rules/multi-tenancy.md` before writing any query
- Add multi-tenancy tests for every new feature

### ❌ Breaking Backward Compatibility

**Problem:** Changes to existing time-based system break current functionality.

**Solution:**
- Never modify existing `TapEvent` logic
- Always check `payroll_type` before branching logic
- Test existing features after every change
- Run full regression test suite before merging

### ❌ Inconsistent Status Values

**Problem:** Using time-based status in attendance-based context (or vice versa).

**Solution:**
- Always check `payroll_type` before setting/validating status
- Use helper functions to get valid status values for current type
- Validate status in forms based on `payroll_type`

### ❌ Allowing Edits to System-Generated Entries

**Problem:** Teachers editing hall pass entries, breaking audit trail.

**Solution:**
- Always check `is_system_generated` before allowing edit/delete
- Disable edit/delete buttons in UI for system-generated entries
- Server-side validation to reject edits to system-generated entries

### ❌ Skipping Conflict Resolution

**Problem:** Duplicate entries created without applying conflict resolution logic.

**Solution:**
- Always check for existing entry before creating new one
- Apply `conflict_resolution` setting from `PayrollSettings`
- Test both conflict resolution modes

### ❌ Not Warning About Payroll Impact

**Problem:** Teachers edit entries affecting unpaid payroll without realizing it.

**Solution:**
- Check if edited entry's timestamp falls within unpaid period
- Show warning dialog if it does
- Clearly explain: "This may affect student payroll calculations"

### ❌ Forgetting to Update Documentation

**Problem:** Features implemented without updating user guides or technical docs.

**Solution:**
- Update CHANGELOG.md in EVERY PR
- Update user guides for user-facing changes
- Update technical docs for architecture/schema changes
- See `.claude/rules/documentation.md` for standards

---

## Checklist for Each PR

### Before Starting Work

- [ ] Read full specification: `docs/specifications/v2.0-flexible-attendance-payroll.md`
- [ ] Understand which phase you're working on
- [ ] Review related rule files (multi-tenancy, migrations, testing, etc.)
- [ ] Check that previous phase is merged to main

### During Development

- [ ] All queries scoped by `join_code`
- [ ] Backward compatibility maintained
- [ ] Status values match `payroll_type`
- [ ] Conflict resolution applied correctly
- [ ] System-generated entries cannot be edited
- [ ] Validation rules enforced
- [ ] CSRF protection included
- [ ] Helpful error messages

### Before Committing

- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Multi-tenancy tests written and passing
- [ ] Regression tests passing
- [ ] Code follows project style
- [ ] No console.log or debug statements
- [ ] No hardcoded values

### Before Creating PR

- [ ] CHANGELOG.md updated
- [ ] Relevant documentation updated
- [ ] Migration tested (upgrade + downgrade)
- [ ] All tests passing
- [ ] No breaking changes to existing features
- [ ] PR description explains changes clearly
- [ ] Screenshots included for UI changes

---

## Migration Strategy

### Safe Migration Process

1. **Create migration script:**
   ```bash
   flask db migrate -m "Add AttendanceLog model for v2.0"
   ```

2. **Review generated migration:**
   - Check all new columns have appropriate defaults
   - Verify indexes are created
   - Ensure foreign keys are correct

3. **Test upgrade:**
   ```bash
   flask db upgrade
   ```

4. **Verify schema:**
   - Check tables exist
   - Check columns have correct types
   - Check indexes are created

5. **Test downgrade:**
   ```bash
   flask db downgrade
   ```

6. **Verify rollback:**
   - Check tables/columns removed
   - Check no orphaned data

7. **Re-upgrade:**
   ```bash
   flask db upgrade
   ```

8. **Run tests:**
   ```bash
   pytest tests/
   ```

9. **Commit:**
   - Commit migration file with model changes
   - Never commit migration separately from model

### Default Values for Backward Compatibility

**PayrollSettings:**
- `payroll_type = 'time_based'` (keeps existing behavior)
- `student_tracking_enabled = True` (keeps existing behavior)
- `teacher_tracking_enabled = False` (no change to existing)
- `attendance_flat_rate = 0.00` (safe default)
- `conflict_resolution = 'last_entry'` (safe default)

**TeacherBlock:**
- `attendance_enabled = True` (keeps existing behavior)

**AttendanceLog:**
- No migration of existing data needed
- New table starts empty
- Existing `TapEvent` data remains intact

---

## Support & Resources

### Documentation

- **Full Specification:** `docs/specifications/v2.0-flexible-attendance-payroll.md`
- **Multi-Tenancy Rules:** `.claude/rules/multi-tenancy.md`
- **Migration Workflow:** `.claude/rules/database-migrations.md`
- **Testing Standards:** `.claude/rules/testing.md`
- **Documentation Standards:** `.claude/rules/documentation.md`
- **Security Principles:** `.claude/rules/security.md`

### When Uncertain

1. Read the full specification
2. Check related rule files
3. Review existing code patterns
4. Ask for clarification (don't assume)

### Red Flags (Stop and Ask)

- You're about to modify `TapEvent` table
- You're writing a query without `join_code` filter
- You're skipping tests "for now"
- You're not sure which phase you're working on
- You're about to break backward compatibility
- You're allowing edits to system-generated entries

---

**Version:** 1.0
**Last Updated:** 2026-01-03
**Status:** Active - Planning Phase
