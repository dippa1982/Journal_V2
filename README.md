# 📔 My Journal

A personal journaling application built with Flask, designed to help record journal entries, understand emotional patterns, track relationships and topics, and support ongoing personal reflection.

---

# 🚀 Recent Development

The application has recently been expanded significantly around:

- Dashboard improvements
- Mood tracking
- Pattern detection
- Relationship analysis
- Emotional pattern detection
- Topic pattern detection
- Therapy question extraction
- Saved therapy questions
- Therapy question exploration
- Markdown journal exports
- Navigation improvements
- Bootstrap dropdown navigation
- General UI and layout improvements

---

# 📊 Dashboard

The dashboard has been redesigned to provide a quick overview rather than displaying full journal entries.

The dashboard now focuses on useful high-level information such as:

- Total journal entries
- Average mood
- Current journal streak
- Unanswered therapy questions
- Daily Compass / current direction
- Personal progress and patterns

The intention is for the dashboard to answer:

> "How am I doing?"

without requiring the user to read through their journal.

Journal entries themselves remain accessible through the Journal section.

---

# 📖 Journal

The Journal section has been reorganised to make navigation easier.

Journal-related functionality includes:

- New Entry
- Journal Entries
- Calendar
- Timeline

The journal remains the core source of data for the application's analysis features.

---

# 📈 Pattern Detection

A dedicated Pattern Detector has been added to analyse journal entries and identify recurring patterns.

The pattern detector currently analyses:

- Mood patterns
- Emotional patterns
- Relationship patterns
- Topic patterns
- Recurring tags
- Significant changes

The pattern detector is designed to work from existing journal data rather than requiring the user to manually enter additional information.

---

## 😊 Mood Patterns

Mood analysis uses the mood scores recorded against journal entries.

Currently calculated:

- Average mood
- Lowest mood
- Highest mood
- Recent average mood
- Previous average mood
- Change between recent and previous moods
- Overall mood trend

The application compares the most recent seven entries against the previous seven entries when enough data exists.

Possible trend results include:

- Mood is trending upwards
- Mood is trending downwards
- Mood is stable

---

## 🧠 Emotional Patterns

The application now attempts to identify broader emotional behaviour rather than simply displaying mood numbers.

Current detection includes:

### Overall emotional state

Based on the average mood:

- Positive
- Mixed / moderate
- Negative

### Emotional stability

The application looks at changes between consecutive mood scores to identify:

- Relatively stable moods
- Moderate changes
- Noticeable emotional swings

### Recent emotional direction

Recent mood data is compared against previous entries to identify whether emotional state appears to be:

- Improving
- Declining

### Repeated lower moods

The detector checks whether lower mood scores occur regularly rather than appearing as isolated events.

### Repeated higher moods

The detector also identifies when higher moods occur regularly across journal entries.

### Significant mood changes

Repeated large changes between entries are flagged as a possible emotional pattern.

The purpose is not to diagnose anything.

It is simply to identify recurring patterns that may be worth reflecting on.

---

# ❤️ Relationship Patterns

Relationship analysis looks at people mentioned in journal entries and examines how mood relates to those interactions over time.

For each person, the application can display:

- Person
- Number of mentions
- Average mood
- First mentioned date
- Last mentioned date
- Mood trend

Relationship trends can currently be:

- Improving
- Declining
- Stable

Relationships are sorted by number of mentions so the people appearing most frequently in the journal are shown first.

This provides a way of seeing whether particular relationships repeatedly appear alongside changes in mood.

---

# 🏷️ Recurring Tags

Journal tags are analysed using a counter to identify frequently occurring tags.

The application records:

- Tag name
- Number of mentions

The most frequently occurring tags are displayed first.

This provides a simple way of identifying recurring subjects in the journal.

---

# 📝 Topic Patterns

Topic analysis has been introduced as another layer of pattern detection.

The goal is to move beyond simply counting tags and identify recurring topics within journal entries.

Topic analysis can eventually be used to identify:

- Frequently discussed subjects
- Number of mentions
- Average mood associated with a topic
- Difference between topic mood and overall mood
- Potential positive topic associations
- Potential negative topic associations

The topic system is intended to become more sophisticated as more journal data becomes available.

---

# 🧠 Therapy Questions

A therapy-question system has been added to the application.

The purpose is to allow meaningful questions from conversations with ChatGPT to be extracted and saved into the journal application.

The workflow is:

1. Copy a ChatGPT conversation.
2. Paste the conversation into the Therapy Questions page.
3. Submit the conversation.
4. AI identifies useful reflection questions.
5. Questions are displayed for review.
6. Select the questions worth keeping.
7. Save them to the journal.

Each saved question can contain:

- Question
- Category
- Context
- Date added
- Answered / unanswered status

---

# 📚 Saved Therapy Questions

Saved therapy questions have their own dedicated page.

Questions can be viewed individually rather than making the entire question card clickable.

Each saved question includes an:

**Explore →**

button.

This makes the interface clearer and prevents accidental navigation when interacting with the question itself.

---

# ✍️ Exploring Therapy Questions

Saved questions can be opened using the Explore button.

This provides a dedicated space to work through a question rather than treating the question itself as a journal entry.

The original therapy question remains associated with the resulting reflection.

---

# 📤 Therapy Questions in Markdown Export

Answered therapy questions can also be included in the journal's Markdown export.

This allows important reflections from therapy-related questions to become part of the exported journal without requiring every answer to become a separate journal entry.

This preserves the distinction between:

- Normal journal entries
- Therapy questions
- Reflections answering those questions

while still keeping them together when the journal is exported.

---

# 🧭 Navigation

The navigation system has been reorganised to reduce the number of top-level menu items.

The current structure is:

```text
🏠 Dashboard

📖 Journal
    ✍️ New Entry
    📖 Entries
    📅 Calendar
    📍 Timeline

📊 Insights
    🗺️ Insights
    👥 People
    🔍 Patterns
    📈 Trends

🧠 Reflection
    🤖 AI Reflection

❤️ Therapy
    📅 Weekly Report
    ❓ Therapy Questions