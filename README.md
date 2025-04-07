# Email Triage Assistant

## Overview

The **Email Triage Assistant** is an AI-powered tool that automates email management by classifying incoming emails into actionable categories ("ignore," "notify," or "respond") and generating responses when needed. Built with Python, LangChain, and Google’s Gemini 1.5 Flash model, it leverages a free-tier API to keep costs at zero while delivering robust functionality. The assistant learns from user feedback, dynamically updates its classification rules, and maintains session memory to enhance accuracy and context over time.


## What It Does

The Email Triage Assistant processes emails by:
1. **Classifying Emails**: Analyzes email content (sender, subject, body) and assigns one of three labels:
   - **Ignore**: Spam, newsletters, or irrelevant messages
   - **Notify**: Important updates (e.g., team member sick, build status)
   - **Respond**: Direct questions, meeting requests, or urgent issues requiring a reply
2. **Generating Responses**: For "respond" emails, uses a ReAct agent with tools to draft emails, schedule meetings, or check availability
3. **Learning and Adapting**: Incorporates user feedback to refine classification rules and memory, improving over time

## How It Works

The assistant operates as a stateful workflow using LangGraph, powered by Gemini 1.5 Flash for natural language processing. Here’s the flow:

1. **Input**: Takes an email from `email_inputs.py` (a dict with `author`, `to`, `subject`, `email_thread`)
2. **Triage**:
   - Parses the email and retrieves similar past examples from an in-memory store (using `sentence-transformers` embeddings)
   - Classifies it with Gemini, guided by static rules and dynamic examples
   - Stores the result and asks for user feedback to correct errors
3. **Response**:
   - If "respond," a ReAct agent uses tools (e.g., `write_email`) to draft a reply, informed by session history
4. **Learning**:
   - Updates stored examples with corrected labels
   - Refines triage rules (e.g., adds "urgent issue" to "notify") via Gemini based on feedback

The code runs locally with no external costs, relying on Gemini’s free tier (1500 requests/day) and `sentence-transformers` for embeddings

## Features

- **Email Classification**:
  - Three categories: "ignore," "notify," "respond."
  - Uses Gemini 1.5 Flash (1M token context) for accurate NLP
- **Response Generation**:
  - Tools: `write_email`, `schedule_meeting`, `check_calendar_availability` (mocked for demo, extensible to real APIs)
  - ReAct agent for intelligent, tool-driven replies
- **Dynamic Memory**:
  - `InMemoryStore` with local embeddings (`all-MiniLM-L6-v2`) stores and retrieves past triage examples
  - Updates examples based on user feedback for better accuracy
- **Session Context**:
  - Tracks email history in `State` (e.g., "Alice’s last email was ‘respond’") for coherent responses
- **Adaptive Rules**:
  - Gemini refines `PROMPT_INSTRUCTIONS` from feedback (e.g., adds new patterns to rules)
- **Free and Lightweight**:
  - No OpenAI or Vertex AI costs—uses Gemini’s free tier and local embeddings

## Installation

### Prerequisites
- Python 3.8+
- Git

### Steps
1. Clone the Repository
2. Install dependencies with: pip install -r requirements.txt
3. Set Up Environment:
   - Get a Gemini API key from [ai.google.dev](https://ai.google.dev).
   - Create a `.env` file in the root directory with: GOOGLE_API_KEY=AIzaSy-your-key-here
4. Run the Assistant:
   Start the assistant with: python main.py
   - Uses the first sample email from `email_inputs.py` by default

**Customize Email Inputs**:
   - Open `email_inputs.py` and modify `EMAIL_SAMPLES` to add your own emails, such as:
     `EMAIL_SAMPLES = [{"author": "Your Name <you@example.com>", "to": "Recipient <recipient@example.com>", "subject": "Your Subject", "email_thread": "Your email body here"}]`
   - Change the index in `main.py` to test different samples, e.g., `email_input = get_email_input(1)` for the second email

## Next Steps

### Current Limitations
- **In-Memory Only**: `InMemoryStore` and `State` history reset on restart
- **Basic Feedback**: Relies on manual `input()`; no UI or automated feedback loop
- **Embedding Quality**: `sentence-transformers` is less powerful than OpenAI/Gemini embeddings

### Planned Features
1. **Real Tool Integration**:
   - Connect `write_email` and `schedule_meeting` to actual email/calendar APIs (e.g., Gmail, Google Calendar)
2. **Persistent Storage**:
   - Replace `InMemoryStore` with `shelve` or SQLite for memory across sessions
3. **UI Integration**:
   - Add a simple CLI or web interface (e.g., Flask) for email input and feedback
4. **Enhanced Embeddings**:
   - If Gemini offers free embeddings via `langchain_google_genai`, swap `sentence-transformers` for better similarity search
