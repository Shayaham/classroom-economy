# **Automatic Discounts Policy Implementation Specification**

  

## Priority Level

  

**Authoritative policy document**


  

This document defines the philosophy, rules, and constraints governing **automatic discounts** and their relationship to the **Classroom Wage Index (CWI)**. It is intended to function at the same level as the CWI specification: as economic infrastructure, not a feature description. 

**Conflict Resolution**

When interpreting and implementing the content and intent of this document, you MUST NOT contradict the philosophy, rules, and contraints set forth by ECONOMY_SPECIFICATION.md. In all other instances, if interpreting and implementing the content and intent of this document would contradict with other rules and constraints, this document SHALL take precendent.



## **1. Purpose**

  

The Automatic Discount System exists to reinforce financially responsible behavior **without weakening economic gravity**. Discounts SHALL NOT  be implemented as rewards for compliance, effort, or moral behavior. They SHALL be interpreted as systemic responses to **reduced financial risk**, measured relative to the Classroom Wage Index (CWI).

CWI defines the scale of income, cost, and risk in the system. Discounts exist only as a secondary effect of stability within that scale.



## **2. Foundational Principle**

  

> **CWI defines the unit of financial risk.**

> **Discounts reflect reductions in that risk, not arbitrary rewards.**

  

All discount logic MUST be defensible in terms of how much instability, volatility, or downside exposure a behavior removes relative to one pay cycle (CWI).



## **3. Non-Negotiable Constraints**

  

The following rules are enforced at the system level and MUST NOT be configurable:

-   Base rent MUST NOT be discountable
    
-   Items covered under rent MUST NOT be discountable
    
-   Mandatory baseline fees MUST NOT be discountable
    
-   Discount behavior applied to any item MUST NOT be more than one.
    
-   Discount tiers defined in this document MUST NOT be editable.
    
-   A system-wide maximum discount cap MUST be enforced per transaction.
    
-   Discounts MUST NOT be applied retroactively or proactively.
-   Discount controls for base rent, items covered under rent, mandatory baseline fees MUST NOT be displayed.

----------

## **4. Discount Behaviors **

 
Each store item MAY optionally incentivize **one** of the following behaviors:

  

### **4.1 No Discount (Default)**

  

The item does not participate in the automatic discount system.


### **4.2 Pays on Time Discount**

  

**Definition:**

Student MUST be **current** on required rent and MUST NOT have any NSF events during the **Current Rent Cycle**.

> [!IMPORTANT]
> The **Current Rent Cycle** is the active rent period configured for the class by the teacher in Rent Settings (e.g., weekly, monthly, or fixed-day cycle).  Once configured, the cycle functions as the authoritative economic period for evaluating rent status, NSF events, and discount eligibility.  Eligibility is evaluated **only within the active cycle** and resets automatically when a new rent cycle begins.

> [!IMPORTANT]
>  **Current** on rent is defined as payment that **occurred on or before the end of the configured due date, evaluated in the system’s authoritative time zone (Pacific Time)**. Payments made during the grace period SHALL NOT count as current.

  

**CWI Rationale:**

Late payments and NSF events disrupt future income streams measured in CWI units. Paying on time protects cash flow across an entire pay cycle.

  

**Economic Meaning:**

The student demonstrates income predictability and low administrative risk.




### **4.3 Insured**

**Definition:**

Student MUST hold an active and current insurance policy **at the moment of purchase**.

>[!IMPORTANT]
> **Active** insurance is defined as a policy that has completed any waiting period and is not pending cancellation.  
> **Current** insurance is defined as a policy that is fully paid through the most recent billing cycle.  
> Insurance status is evaluated **only at the time of purchase** and is not retroactively applied.

**CWI Rationale:**

Insurance caps potential losses that could otherwise exceed a full CWI cycle. The student prepays to limit downside exposure.

**Economic Meaning:**

The student has transferred risk away from the system and reduced volatility.


### **4.4 Has Savings Buffer**

**Definition:**

Student MUST have a savings balance that meets or exceeds a system-defined multiple of CWI **at the moment of purchase**.

**Default Threshold:**

**1.5 × CWI**

**Preset Thresholds (configurable in Banking Settings):**

- 1.0 × CWI  
- 1.5 × CWI (default)  
- 2.0 × CWI  

>[!IMPORTANT]
> Savings balance is evaluated using the student’s available savings at the time of purchase.  
> Pending deposits, pending withdrawals, or future earnings MUST NOT be counted.  
> Eligibility is not persistent and MUST be re-evaluated for each transaction.

**CWI Rationale:**

Savings replace future income. A buffer of 1.5 × CWI allows the student to absorb a missed pay cycle without destabilization.

**Economic Meaning:**

The student has achieved short-term financial independence from the next paycheck.

## **5. Discount Tiers**

  

Discount strength is selected from fixed tiers that are displayed as radio buttons.

-   **Minor** — 5%
    
-   **Normal** — 10%
    
-   **Major** — 15%
    

  

Percentages are fixed system constants and MUST NOT be modified.

----------

## **6. Discount Tier Rationale (CWI-Anchored)**

  

Discount tiers represent the **degree of financial risk removed**, measured relative to one CWI cycle:

-   **Minor**
    
    Reduces small, short-term friction. Reflects marginal stabilization below one full pay cycle.
    
-   **Normal**
    
    Reduces meaningful friction. Reflects stabilization at approximately one pay cycle.
    
-   **Major**
    
    Reduces significant future volatility. Reflects protection against multi-cycle disruption.
    

  

Because all prices scale with CWI, fixed percentages remain proportional and non-arbitrary across classrooms.


## **7. Teacher Configuration Boundaries**

  

Teachers may:

-   Enable or disable the automatic discount system
    
-   Select one discount behavior per eligible item
    
-   Select a discount tier (Minor / Normal / Major)
    
-   Choose a class-level Savings Buffer threshold from preset options in banking setting (to be added)
    

  

System MUST NOT allow Teachers to:

-   Define new behaviors
    
-   Modify percentages
    
-   Stack discount behaviors
    
-   Apply discounts to rent or rent-covered items
    


## **8. Student Experience**

  

When a discount is applied, the system provides a concise explanation, for example:

  

> “You received a 10% discount because you have a savings buffer.”

  

Students are not shown formulas, thresholds, or internal calculations. The causal relationship between behavior and outcome remains visible and legible.


## **9. Educational Intent**

  

This system is designed to teach that:

-   Obligations are fixed
    
-   Responsibility does not eliminate costs
    
-   Responsibility reduces friction and volatility
    
-   Stability creates optionality
    

  

The economy rewards planning, reliability, and risk management. It is not meant for optimization or compliance.


## **10. Versioning & Expansion Policy**

  

v1 intentionally limits discount behaviors to preserve clarity and trust. Any expansion MUST:

-   Be defensible in CWI terms
    
-   Represent a distinct dimension of risk reduction
    
-   Avoid overlap with existing behaviors
    

  

Expansion is a curriculum decision, not a convenience feature.

----------

