Automatic Discounts — Developer Enforcement & Build Guide

Purpose

This document translates the Automatic Discounts Policy Implementation Specification into concrete developer responsibilities. It defines what must be enforced, where enforcement must occur, and how the feature integrates safely with existing infrastructure.

This is an implementation guide, not a policy document. Where ambiguity exists, the authoritative policy documents take precedence.

1. Enforcement Checklist (Non-Negotiable)

The following rules MUST be enforced in code, regardless of UI state, client behavior, or teacher configuration.

1.1 Item-Level Enforcement

Base rent items MUST NOT be discountable

Items flagged as covered under rent MUST NOT be discountable

Mandatory baseline fees MUST NOT be discountable

At most one discount behavior MAY be associated with any item

Discount tiers MUST be limited to: Minor, Normal, Major

Discount controls MUST NOT be rendered for ineligible items

1.2 Transaction-Level Enforcement

Discounts MUST be evaluated at the moment of purchase

Discounts MUST NOT be applied retroactively

Discounts MUST NOT be applied proactively

A system-wide maximum discount cap MUST be enforced per transaction

1.3 Teacher Configuration Enforcement

Teachers MUST NOT be allowed to define new discount behaviors

Teachers MUST NOT be allowed to modify discount percentages

Teachers MUST NOT be allowed to stack discount behaviors

Teachers MUST NOT be allowed to apply discounts to rent or rent-covered items

2. Discount Behavior Evaluation Logic

Each purchase MUST follow the evaluation sequence below, in order:

Verify item eligibility

Resolve the item’s configured discount behavior (or none)

Evaluate student eligibility for that behavior

Resolve the selected discount tier to its percentage value

Apply the discount, enforcing the system-wide cap

Record discount metadata for audit and explanation

If any step fails, the transaction MUST proceed without a discount.

3. Behavior-Specific Enforcement Rules

3.1 Pays on Time

Eligibility MUST be evaluated against the Current Rent Cycle

Student MUST:

Be current on required rent

Have no NSF events during the cycle

Payments made during a grace period MUST NOT count as on-time

Eligibility MUST reset automatically at the start of each new rent cycle

3.2 Insured

Insurance status MUST be evaluated at the moment of purchase

The policy MUST:

Be active (waiting period completed)

Be current (paid through the most recent billing cycle)

Policies pending cancellation MUST invalidate eligibility

3.3 Has Savings Buffer

Savings balance MUST be evaluated at the moment of purchase

The balance MUST:

Meet or exceed the configured CWI multiplier

Exclude pending deposits and pending withdrawals

Exclude future or expected earnings

4. Data Model Additions (Implementation-Authoritative)

This section defines the required and optional schema changes necessary to implement Automatic Discounts. These definitions are authoritative for implementation. Formal schema documentation will be added to database_schema.md after the feature is built and stabilized.

4.1 Store Items (Required)

The following fields MUST be added to the store items table:

discount_behavior (nullable enum)

null (No Discount)

pays_on_time

insured

savings_buffer

discount_tier (nullable enum)

minor

normal

major

Existing items MUST default to null for both fields.

4.2 Class / Economy Settings (Existing Integration)

Automatic Discounts rely on existing class-scoped economic configuration. No new tables are required.

The following setting MUST be referenced:

savings_buffer_multiplier (enum)

1.0

1.5 (default)

2.0

This setting MUST be configurable only at the class level and MUST NOT be overridden per item or per student.

4.3 Transactions (Optional, Strongly Recommended)

To support auditing, debugging, dispute resolution, and future analytics, the following fields SHOULD be added to the transaction table:

discount_applied (boolean)

discount_behavior

discount_tier

discount_percentage

discount_amount

discount_reason (human-readable string)

These fields MUST be written at the time of purchase and MUST NOT be recalculated later.

4.4 Explicit Non-Requirements

The following MUST NOT be implemented:

A standalone discounts table

Per-student discount persistence

Coupon or promotion-style systems

Persistent discount entitlements

Discounts are derived at transaction time, not stored as first-class economic entities.

5. Build Order (Recommended)

Step 1: Backend Enforcement

Implement discount eligibility checks server-side

Enforce item eligibility rules regardless of UI state

Implement the system-wide discount cap

Step 2: Data Migration

Add nullable discount fields to existing store items

Default all existing items to discount_behavior = null

Backfill safely without altering existing pricing

Step 3: Transaction Pipeline Integration

Insert discount evaluation into the purchase flow

Ensure atomic evaluation at purchase time

Persist discount metadata for audits and debugging

Step 4: Teacher UI

Add radio-button discount selection for eligible items

Hide discount UI for ineligible items

Display discount tier percentages as read-only

Step 5: Student Feedback

Display a concise discount explanation after purchase

MUST NOT expose formulas, thresholds, or eligibility calculations

6. Failure Modes & Safe Defaults

If discount evaluation fails → proceed with full price

If behavior eligibility cannot be resolved → apply no discount

If discount metadata is missing → apply no discount

If conflicting flags exist → apply no discount

The system MUST fail closed, not open.

7. Testing Scenarios (Minimum Coverage)

On-time payment vs grace-period payment

NSF event within vs outside the current rent cycle

Insurance active vs pending cancellation

Savings balance just below vs just above the threshold

Rent item vs rent-covered item

Existing store items with null discount fields

8. Guiding Principle for Developers

Discounts are a consequence of reduced financial risk, not a pricing feature.

If an implementation choice weakens economic gravity, introduces stacking, or obscures causality, it violates policy (even if technically correct.)

Status: Required for implementation

