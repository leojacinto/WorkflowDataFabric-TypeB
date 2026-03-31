# Outcome: Agent Flow — Document Intelligence Highlight

Greyed-out variant with Expense → Doc Intel or Lens → Documents highlighted. First column replaces Integration Hub/REST API with Doc Intel or Lens/Documents.
Used in `extended-exercises/lab-exercise-servicenow-lens-and-document-intelligence.md`.

```mermaid
graph TD

    EC[Employee Center or<br/>Workspace with Now Assist]
  
    subgraph TOOLS["Agent Tools & Data Sources"]
        T1["Expense"]
        T2["Cost<br/>Center<br/>Details"]
        T3["Cost<br/>Center<br/>Summary"]        
        T4["Cost<br/>Center<br/>History"]
        T5["Expense<br/>History"]
        T6["External<br/>DB"]
        T7["Executive<br/>Memos"]
        S_DI["Doc<br/>Intel<br/>or Lens"]
        S2["Zero<br/>Copy<br/>ERP"]
        S3["Zero<br/>Copy<br/>SQL"]        
        S6["MCP"]
        S7["External<br/>Content<br/>Connector"]
    end

    subgraph EXT["External Systems"]
        DOCS["Documents"]
        CDW["Cloud<br/>Data<br/>Warehouse"]
        ERP["ERP<br>System"]
        MCP_EXT["External<br/>MCP<br/>Server"]
        SharePoint["SharePoint"]
    end
    
    EC --> TOOLS
    T1 --> S_DI --> DOCS
    T2 --> S2 --> ERP
    T3 --> S3 --> CDW
    T4 --> S3 
    T5 --> S3 
    T6 --> S6 --> MCP_EXT
    T7 --> S7 --> SharePoint

    %% Styling
    classDef external fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    classDef wdf fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
    classDef data fill:#8D6E63,stroke:#5D4037,stroke-width:2px,color:#fff
    classDef docintel fill:#FFB300,stroke:#F57F17,stroke-width:2px,color:#1a1a1a
    classDef greyed fill:#D5D5D5,stroke:#BDBDBD,stroke-width:1px,color:#9E9E9E

    %% Highlight Expense → Doc Intel or Lens → Documents
    class T1 data
    class S_DI docintel
    class DOCS external

    %% Grey out everything else
    class EC,T2,T3,T4,T5,T6,T7 greyed
    class S2,S3,S6,S7 greyed
    class CDW,ERP,MCP_EXT,SharePoint greyed

    %% Grey out non-highlighted edges (keep 1:T1→S_DI, 2:S_DI→DOCS)
    linkStyle 0 stroke:#D5D5D5,stroke-width:1px
    linkStyle 3 stroke:#D5D5D5,stroke-width:1px
    linkStyle 4 stroke:#D5D5D5,stroke-width:1px
    linkStyle 5 stroke:#D5D5D5,stroke-width:1px
    linkStyle 6 stroke:#D5D5D5,stroke-width:1px
    linkStyle 7 stroke:#D5D5D5,stroke-width:1px
    linkStyle 8 stroke:#D5D5D5,stroke-width:1px
    linkStyle 9 stroke:#D5D5D5,stroke-width:1px
    linkStyle 10 stroke:#D5D5D5,stroke-width:1px
    linkStyle 11 stroke:#D5D5D5,stroke-width:1px
    linkStyle 12 stroke:#D5D5D5,stroke-width:1px
```
