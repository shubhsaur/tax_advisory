# Phase 1 Requirements: Tax Advisor Application

## Overview
Phase 1 focuses on the initial project setup, database schema creation, and the implementation of a modern landing page. This phase lays the foundation for all subsequent development.

## Deliverables
- **Project Setup:**
  - Initialize the project repository and structure for both frontend and backend.
  - Set up the unified tech stack as described in the PRD (Vanilla HTML/CSS/JS frontend, FastAPI backend, Supabase database connection).

- **Database Schema:**
  - Create the `UserFinancials` table in Supabase with the following columns:
    | Column Name         | Data Type         | Description                        |
    |--------------------|------------------|------------------------------------|
    | session_id         | UUID             | Primary Key, unique session ID      |
    | gross_salary       | NUMERIC(15, 2)   | Total gross salary                  |
    | basic_salary       | NUMERIC(15, 2)   | Basic salary component              |
    | hra_received       | NUMERIC(15, 2)   | HRA received                        |
    | rent_paid          | NUMERIC(15, 2)   | Annual rent paid                    |
    | deduction_80c      | NUMERIC(15, 2)   | 80C investments                     |
    | deduction_80d      | NUMERIC(15, 2)   | 80D medical insurance               |
    | standard_deduction | NUMERIC(15, 2)   | Standard deduction                  |
    | professional_tax   | NUMERIC(15, 2)   | Professional tax paid               |
    | tds                | NUMERIC(15, 2)   | Tax Deducted at Source              |
    | created_at         | TIMESTAMPTZ      | Record creation timestamp           |

- **Landing Page:**
  - Design and implement a modern, branded landing page.
  - Use the "Aptos Display" font and a light theme with blue highlights.
  - Include a prominent "Start" button to begin the user flow.

## Acceptance Criteria
- User can access and view the landing page in the browser.
- The `UserFinancials` table exists in Supabase with the specified schema.

## References
- See [PRD.md](./PRD.md) for the full product requirements and future phases. 