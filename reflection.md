# PawPal+ Project Reflection

## 1. System Design

Based on the PawPal+ project, here are three core user actions the app should support:

1. **Add a pet care task**
The user enters a task name (e.g., "Morning walk"), duration in minutes, and priority (low/medium/high). This is already stubbed in the starter UI and is the primary data-entry action that feeds everything else.

2. **Generate a daily schedule**
The user clicks "Generate schedule" to produce an ordered, time-blocked plan for the day. The scheduler should pick and sequence tasks based on priority and available time, then explain why each task was chosen and when it happens.

3. **Set owner + pet context**
The user provides basic owner info (name, time available) and pet info (name, species, any preferences like medication timing). This context constrains the schedule, e.g., a cat owner gets different default tasks than a dog owner, and a busy owner with only 90 minutes gets a tighter plan.

These three map directly to the three layers the README asks you to build: input (owner/pet info) → data (tasks) → output (schedule). Everything else like editing tasks, viewing history, explaining reasoning is a refinement on top of these.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
