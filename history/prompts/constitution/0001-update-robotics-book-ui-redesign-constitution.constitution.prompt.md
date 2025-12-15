---
id: 0001
title: Update Robotics Book UI Redesign Constitution
stage: constitution
date: 2025-12-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: unknown
command: /sp.phr --title "Update Robotics Book Website UI Redesign Constitution" --stage constitution
labels: ["constitution", "ui-redesign", "robotics-book", "principles", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

# Objective
Improve and redesign the homepage UI of my Robotics Book website.
The goal is to create a **fast-loading, clean, modern, and robotics-themed** interface.

# Task
You must update my homepage (`index.tsx`) and apply styling using my existing custom CSS file.
The new UI must look highly professional, futuristic, and fully aligned with a Robotics / Humanoid AI theme.

# Requirements

## 1. Hero Section (Top of the Homepage)
- Left side:
  - Big **Book Title**
  - Short **Subheading**
  - **Get Started** button → must navigate to **Chapter 1**
- Right side:
  - A high-quality **Robotics/Humanoid AI related image**
  (Use an online image link or placeholder; I will replace later)
- Hero section must feel premium and futuristic.

## 2. Core Concepts Section
Create a visually attractive “Core Concepts” section that includes:
- 3–6 concept cards
- Each card must have:
  - Robo-tech icon/image
  - Title
  - Short description
- Layout should be clean, grid-based, and appealing.

## 3. Table of Contents Section
Create TOC cards for **all 8 chapters**:
- Each card must include:
  - Chapter image (placeholder ok)
  - Chapter name
  - Subtitle
  - “Read More” button linking to the correct chapter file
- Design should match robotics theme
- Cards must look modern, with hover effects.

## 4. Design & Performance Expectations
- Robotics-themed color palette (blues, blacks, neons, gradients)
- Smooth spacing, shadows, animations
- Fully responsive
- Fast-loading structure
- Clean and well-organized JSX + CSS

# Output Format
Return:
- Updated `index.tsx` code
- Updated CSS code (using my existing custom CSS file — do not create a new one)
- Only clean, production-ready code—no explanation text.

## Response snapshot

The project constitution for the Robotics Book Website UI Redesign was updated to version 1.0.0, incorporating core principles for fast loading, modern aesthetics, robotics-themed interface, responsive design, and component-based structure. Several templates and the `README.md` file require manual updates to align with the new constitution.

## Outcome

- ✅ Impact: The project's core principles and governance for the UI redesign were formally established in the constitution file.
- 🧪 Tests: none
- 📁 Files: 1 file modified: .specify/memory/constitution.md
- 🔁 Next prompts: Update remaining templates and README.md; Address TODO(RATIFICATION_DATE) in constitution.
- 🧠 Reflection: The `create-phr.sh` script was not found, requiring a manual PHR creation based on the template.

## Evaluation notes (flywheel)

- Failure modes observed: The `create-phr.sh` script was not found in the expected path, leading to a fallback to manual PHR creation.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Investigate why `create-phr.sh` was not found and ensure the script path is correct or regenerate if missing.
