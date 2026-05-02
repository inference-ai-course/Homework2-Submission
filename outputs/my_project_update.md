# Project Update — Week 2

**Generated:** 2026-05-02 15:15:11
**Student Name:** Chris

---

## Original Project Definition (Week 1)

# My Research Agent Project
**Created:** 2026-04-07 17:24:31


# MY RESEARCH AGENT PROJECT

## 1. PROJECT TITLE
GitHub Insight Agent – README-Based Repository Summarizer

## 2. THE PROBLEM
Developers and researchers often encounter GitHub repositories with long or unclear documentation. 
Understanding what a repository does, its key features, and whether it is relevant can take significant time.

## 3. YOUR SOLUTION
Build an AI agent that takes a GitHub repository URL and:
- Extracts the README file using the GitHub API
- Analyzes the content using an LLM
- Produces a structured summary including:
  - Project description
  - Key features
  - Tech stack
  - Use cases
  - Complexity level

Future extensions may include deeper code analysis and repository comparison.

## 4. USER WORKFLOW
1. User inputs a GitHub repository URL
2. Agent parses the URL to identify owner and repository
3. Agent fetches the README file via GitHub API
4. Agent generates a structured summary using an LLM
5. User receives a clean JSON summary

## 5. COMPONENTS
☑ CO-STAR prompting – for consistent and high-quality summaries  
☑ Structured outputs – JSON format for reliable downstream use  
☐ Chain-of-thought – optional (future improvement)  
☐ Model selection – optional (future optimization)  
☑ MCP/Tool use – GitHub API for data retrieval  
☑ Multi-step workflow – URL → README → summary  

## 6. SUCCESS CRITERIA
- Produces valid JSON output ≥95% of the time  
- Accurately captures repository purpose (ma

---

## Week 2 Updates
Consiering the simplicity of the project definition of Week 1, I focused on designing a data strategy that would be practical 
and aligned with the tools we've covered. I identified radio news transcripts and YouTube lecture transcripts as promising sources of domain-relevant text for a personalized language learning companion. I estimated an initial volume of around 50 documents totaling approximately 50K tokens, which is manageable for experimentation while still providing enough content to work with. 

### Data Strategy

| Aspect | Plan |
|---|---|
| Scraping targets | ['Radio news transcripts for current events vocabulary', 'YouTube lecture transcripts'] |
| Expected volume | [50 documents, 50K tokens] |
| Cleaning concerns | ['Duplicate abstracts from cross-posted papers', 'Non-English, Non-French, Non-Chinese content to filter'] |
| Tokenizer | [tiktoken cl100k_base / HF gpt2 / sentencepiece] |
| Est. cost per call | [0.1$ per API call] |
| Approach | [fine-tuning /  prompt engineering / hybrid] |

### Architecture Constraints

As a systems architect, I will evaluate your Language Learning/Education (EdTech) project through the lens of computational efficiency, linguistic nuance, and scaling costs.

### 1. Typical Input Lengths in EdTech
In the education domain, you will encounter three distinct "tiers" of input lengths:

*   **Micro-Interactions (50 – 500 tokens):** Chat-based tutoring, flashcard generation, and grammar corrections. This is 80% of your traffic.
*   **Assessment & Content (2,000 – 8,000 tokens):** Grading a student’s 1,500-word essay alongside a rubric, or processing a single textbook chapter for reading comprehension questions.
*   **The "Course-Level" Context (20,000 – 60,000 tokens):** This is unique to EdTech. It involves the student’s entire semester history, past mistakes, and the full curr

### Key Learnings from Week 2

- Transformer attention is O(n²) — must plan for context window limits
- Tokenizer choice affects cost: tiktoken (cl100k) is most efficient for English
- Data cleaning pipeline: language filter → dedup → PII removal
- Extended thinking improves reasoning at ~2× token cost
- Fine-tuning covered conceptually; full implementation in later class

### Updated Technical Approach

[TODO: Based on what you learned in Week 2, update your approach here.
Consider: model choice, data pipeline, tokenization, context window strategy,
and whether fine-tuning or RAG makes more sense for your use case.]

---

*Updated after completing Week 2 notebooks 00–08.*
