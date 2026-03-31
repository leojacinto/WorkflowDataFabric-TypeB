# Outcome: Agent Flow — Zero Copy Connectors Highlight

Greyed-out variant with Cost Center Details → Zero Copy ERP → ERP, and Cost Center Summary/History + Expense History → Zero Copy SQL → CDW highlighted.
Used in `main-exercises/lab-exercise-zero-copy-connectors.md`.

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
        S1["Integration<br>Hub"]
        S2["Zero<br/>Copy<br/>ERP"]
        S3["Zero<br/>Copy<br/>SQL"]        
        S6["MCP"]
        S7["External<br/>Content<br/>Connector"]
    end

    subgraph EXT["External Systems"]
        API["REST<br/>API"]
        CDW["Cloud<br/>Data<br/>Warehouse"]
        ERP["ERP<br>System"]
        MCP_EXT["External<br/>MCP<br/>Server"]
        SharePoint["SharePoint"]
    end
    
    EC --> TOOLS
    T1 --> S1 --> API
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
    classDef greyed fill:#D5D5D5,stroke:#BDBDBD,stroke-width:1px,color:#9E9E9E

    %% Highlight Zero Copy paths
    class T2,T3,T4,T5 data
    class S2,S3 wdf
    class CDW,ERP external

    %% Grey out everything else
    class EC,T1,T6,T7 greyed
    class S1,S6,S7 greyed
    class API,MCP_EXT,SharePoint greyed

    %% Grey out non-highlighted edges (keep 3:T2→S2, 4:S2→ERP, 5:T3→S3, 6:S3→CDW, 7:T4→S3, 8:T5→S3)
    linkStyle 0 stroke:#D5D5D5,stroke-width:1px
    linkStyle 1 stroke:#D5D5D5,stroke-width:1px
    linkStyle 2 stroke:#D5D5D5,stroke-width:1px
    linkStyle 9 stroke:#D5D5D5,stroke-width:1px
    linkStyle 10 stroke:#D5D5D5,stroke-width:1px
    linkStyle 11 stroke:#D5D5D5,stroke-width:1px
    linkStyle 12 stroke:#D5D5D5,stroke-width:1px
```
