# UPick Project Architecture

UPick is a subscription management system with a focus on academic paper tracking, particularly from sources like arXiv. The system crawls content, analyzes changes, and presents updates through a Gradio-based web interface.

## System Components

```mermaid
graph TD
    User[User] --> WebUI[Gradio Web Interface]
    WebUI --> Services[Services]
    Services --> Crawler[Crawlers]
    Services --> DB[Database]
    Services --> Agent[AI Agent]
    Crawler --> arXiv[arXiv API]
    Crawler --> Web[Web Sources]
    Crawler --> IEEE[IEEE Sources]
    Agent --> LLM[LLM Services]
    WebUI --> Updates[Content Updates]
    DB <--> Updates
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Scheduler
    participant Crawler
    participant AI Agent
    participant Database
    participant Web UI

    User->>Web UI: Add subscription
    Web UI->>Database: Store subscription
    Web UI->>Scheduler: Register refresh job
    
    loop Scheduled Jobs
        Scheduler->>Crawler: Fetch content
        Crawler->>Database: Store raw content
        Crawler->>AI Agent: Request content analysis
        AI Agent->>Database: Store content summary
    end
    
    User->>Web UI: View updates
    Web UI->>Database: Request updates
    Database->>Web UI: Return processed updates
    Web UI->>User: Display updates
```

## Directory Structure

```mermaid
graph LR
    Root[UPick] --> SRC[src]
    Root --> Resources[resources]
    Root --> Docs[Documentation]
    SRC --> Pages[pages]
    SRC --> DB[db]
    SRC --> Crawler[crawler]
    SRC --> Services[services]
    SRC --> Log[log]
    SRC --> Agent[agent]
    Pages --> GradioPage[gradio_page.py]
    Pages --> ArxivPage[Upick_for_arxiv.py]
    Crawler --> ArxivCrawler[arxiv.py]
    Crawler --> WebCrawler[web.py]
    Crawler --> IEEECrawler[ieee.py]
    Agent --> LLM[llm.py]
    Agent --> Summary[summary.py]
    Services --> Scheduler[scheduler.py]
    Services --> ContentDiff[contentdiff.py]
```

## Key Components Description

### Crawlers
- **ArxivCrawler**: Specialized crawler for extracting papers from arXiv
- **WebCrawler**: General-purpose web crawler for subscription content
- **IEEECrawler**: Specialized crawler for IEEE publications

### AI Agent
- **Summary**: Uses LLM to analyze content changes and generate summaries
- **LLM**: Interface to language model services

### Services
- **Scheduler**: Manages periodic content refreshing using APScheduler
- **ContentDiff**: Detects changes between content versions

### Web UI
- **Gradio Interface**: User-friendly interface for managing subscriptions and viewing updates
- **Upick_for_arxiv**: Specialized UI for arXiv paper tracking

## Technology Stack

- **Backend**: Python
- **Web Framework**: Gradio
- **Database**: SQLite
- **Scheduler**: APScheduler
- **AI**: LangChain, OpenAI (or alternative LLM providers)
- **Web Crawling**: BeautifulSoup, Requests
- **Data Processing**: JSON, Pydantic

## Development Roadmap

```mermaid
gantt
    title UPick Development Roadmap
    dateFormat  YYYY-MM-DD
    
    section Crawler
    Enhance arXiv crawler functionality :done, a1, 2025-03-20, 30d
    Support more categories :active, a2, after a1, 30d
    Add scheduled crawling :active, a3, after a1, 30d
    
    section User Features
    Create subscription interface :active, b1, 2025-04-01, 30d
    Add email notifications :b2, after b1, 30d
    
    section Data Management
    Bulk import/export :c1, 2025-05-01, 30d
    Data cleaning tools :c2, after c1, 30d
    
    section UI Improvements
    Mini-program adaptation :d1, 2025-06-01, 30d
    
    section AI Enhancements
    Abstract summarization :e1, 2025-05-15, 45d
    Paper quality scoring :e2, after e1, 30d
``` 