# Release Notes - Version 1.5.0

**Release Date**: December 29, 2025  
**Focus**: Issue reporting lifecycle, security remediation, documentation and dependency updates

---

## Highlights

- Added issue reporting with escalation and resolution workflows for students and teachers
- Shipped security remediation tooling and documented a comprehensive attack surface audit
- Standardized UTC timestamp formatting for consistent reporting
- Refreshed documentation structure and updated key dependencies

---

## New and Notable

### Issue Reporting and Resolution
- Added attendance issue reporting to help students and teachers flag and track issues.
- Implemented issue resolution and escalation workflows.
- Refined issue management and refreshed related UI flows.

### Security Remediation and Audit
- Disabled a vulnerable AI inference workflow after identifying a PromptPwnd prompt injection risk.
- Added remediation guidance, fixed workflow templates, and an SSH security setup script.
- Published a comprehensive attack surface audit with findings and recommendations.

### Time Handling and Admin Quality
- Standardized UTC timestamp formatting for clearer audit trails.
- Fixed System Admin announcements form error by adding a custom `coerce` for `target_teacher`.

### Documentation and Dependencies
- Reorganized documentation for improved navigation.
- Updated dependencies: `requests` 2.32.4 to 2.32.5, `markdown` 3.7 to 3.10, and `webfactory/ssh-agent` 0.9.0 to 0.9.1.

---

## Upgrade Notes

1. Follow the standard deployment process (pull latest, install dependencies, run migrations if applicable).
2. Review the security remediation guidance in `docs/security/SECURITY_REMEDIATION_GUIDE.md`.
3. Validate any internal workflow references to AI inference jobs, as the vulnerable workflow is disabled.

---

## Testing and Validation

- No new release-specific test guidance provided; run the standard test suite for your environment.

