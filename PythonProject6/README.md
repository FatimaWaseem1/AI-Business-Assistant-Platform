# AI Business Assistant Platform

A multi-module AI platform built during my internship at Axorvian, bringing together several business-facing AI tools into a single Streamlit application.

## Overview

The platform is organized as a multi-page Streamlit app, with each page dedicated to a different business use case. All modules share a common backend for authentication, LLM access, and retrieval, so new features can be added without duplicating core logic.

## Modules

- **AI Chat** – conversational assistant for general queries
- **Document AI** – document upload, parsing, and Q&A
- **Resume AI** – resume analysis and feedback
- **Email AI** – AI-assisted email drafting
- **Content AI** – content generation support
- **Coding AI** – coding help and code-related queries

## Architecture

- **Frontend:** Streamlit multi-page app
- **Core package (`core/`):** shared logic used across all modules, including:
  - SQLite-based authentication
  - Streaming LLM integration (Gemini and OpenAI)
  - Retrieval-Augmented Generation (RAG) via FAISS

## Notes

Building this surfaced a few real-world debugging challenges along the way, including handling a retired Gemini model name and recovering from a missing `.env` file — both fixed as part of getting the platform running reliably.

## Tech Stack

Python, Streamlit, FAISS, SQLite, Gemini API, OpenAI API
