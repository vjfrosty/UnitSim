Apps SDK
•	url: https://developers.openai.com/apps-sdk/
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Apps SDK
•	headings: Core Concepts | Plan | Build | Deploy | Guides | Resources
•	last_updated:
summary
High-level landing page for the Apps SDK: what it is, preview availability, and how to proceed via Plan → Build → Deploy. It also links to design guidelines, developer guidelines, optimization, security/privacy, troubleshooting, and reference. (developers.openai.com)
content
Introduces the Apps SDK as OpenAI’s framework for building apps inside ChatGPT. The page acts as a hub to core concepts (MCP, user interaction, design), planning (use cases, tools, components), building (MCP server setup, custom UX, auth, persistence, examples), deploying (server hosting, connecting from ChatGPT, testing), and key guides/resources. (developers.openai.com)
________________________________________
MCP
•	url: https://developers.openai.com/apps-sdk/concepts/mcp-server
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: MCP
•	headings: What is MCP? | Protocol building blocks | Why Apps SDK standardises on MCP
•	last_updated:
summary
Explains the Model Context Protocol (MCP) and why the Apps SDK standardizes on it for tool discovery/invocation and UI rendering metadata. Recommends streamable transports and outlines minimal server capabilities. (developers.openai.com)
content
Defines MCP as an open spec that connects LLM clients to external tools/resources. A minimal Apps SDK MCP server must list tools (with JSON Schema contracts), handle call_tool, and optionally point to embedded UI resources for rendering in ChatGPT. Transport is agnostic (e.g., SSE or Streamable HTTP), with Streamable HTTP recommended. (developers.openai.com)
________________________________________
User Interaction
•	url: https://developers.openai.com/apps-sdk/concepts/user-interaction
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: User Interaction
•	headings: Discovery | Named mention | In-conversation discovery | Directory | Entry points | In-conversation entry | Launcher
•	last_updated:
summary
How users discover, activate, and use apps in ChatGPT: named mentions, in-conversation discovery, the directory, and entry points like the launcher. Metadata quality and testing drive reliable tool selection. (developers.openai.com)
content
Covers discovery (prompts, directory, proactive entry points), criteria the model uses (context, mentions/citations, tool metadata, linking state), and best practices (action-oriented tool descriptors, clear component descriptions, golden prompts). Describes in-conversation entry behavior and the launcher as a high-intent entry point. (developers.openai.com)
________________________________________
App design guidelines
•	url: https://developers.openai.com/apps-sdk/concepts/design-guidelines
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: App design guidelines
•	headings: (Guidance on cards/views, clarity & trust, accessibility, performance)
•	last_updated:
summary
Design system guidance to make in-chat UIs feel native to ChatGPT—focus on clarity, accessibility, trustworthy patterns, and performance. (developers.openai.com)
content
Outlines principles for information hierarchy, component choices (cards, carousels, fullscreen), predictable interactions, and robust loading/error states. Encourages accessible, responsive layouts consistent with ChatGPT’s look/feel. (The page content is long; this is a concise summary derived from the document.) (developers.openai.com)
________________________________________
Research use cases
•	url: https://developers.openai.com/apps-sdk/plan/use-case
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Research use cases
•	headings: Why start with use cases | Gather inputs | Define evaluation prompts | Scope the minimum lovable feature | Translate use cases into tooling | Prepare for iteration
•	last_updated:
summary
Plan by enumerating/prioritizing user tasks, crafting golden prompts (positive/negative), and scoping minimum lovable features before tool/schema work. (developers.openai.com)
content
Advocates use-case-first planning to align discovery and outcomes. Gather inputs (interviews, prompt sampling, constraints), define evaluation prompts (direct, indirect, negative), scope P0 scenarios, translate scenarios into tool contracts (inputs/outputs, component intent), and set iteration loops with analytics and tester feedback. (developers.openai.com)
________________________________________
Define tools
•	url: https://developers.openai.com/apps-sdk/plan/tools
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Define tools
•	headings: (Tool schema design, inputs/outputs, metadata)
•	last_updated:
summary
Guidance to design tool contracts—schemas, parameters, outputs, and metadata that improve discovery and reliable invocation. (developers.openai.com)
content
Emphasizes precise JSON Schema inputs/outputs, clear descriptions, and metadata that the model can reason about. Align tools with concrete user tasks and how components will render results. (Concise summary from the page.) (developers.openai.com)
________________________________________
Design components
•	url: https://developers.openai.com/apps-sdk/plan/components
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Design components
•	headings: (Component library, layouts, state, loading & errors)
•	last_updated:
summary
Plan the UI components and interaction flows: layouts, state handling, progressive disclosure, and resilient loading/error patterns. (developers.openai.com)
content
Maps structured tool results to components rendered in chat. Encourages predictable, accessible components that adapt to conversation state and gracefully handle partial failures. (Concise summary from the page.) (developers.openai.com)
________________________________________
Set up your server
•	url: https://developers.openai.com/apps-sdk/build/mcp-server
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Set up your server
•	headings: Project setup | MCP server skeleton | Tool registration | Streaming
•	last_updated:
summary
Hands-on setup for an Apps SDK-compatible MCP server: bootstrapping, registering tools, structured outputs, and streaming for responsiveness. (developers.openai.com)
content
Shows how to implement an MCP server (often Node/TypeScript), expose tools with schemas, return structured content suited to component rendering, and enable streamable transport. Includes local dev/testing guidance. (developers.openai.com)
________________________________________
Build a custom UX
•	url: https://developers.openai.com/apps-sdk/build/custom-ux
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Build a custom UX
•	headings: (Component bridge, bundling, iframe sandbox, data exchange)
•	last_updated:
summary
How Apps SDK components (often React) run in an iframe and communicate with ChatGPT via a bridge API; bundling and data exchange patterns. (developers.openai.com)
content
Describes the component shell, window.openai-style bridge semantics, hydration and sandboxing, and project structure for reliable rendering in chat. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Authentication
•	url: https://developers.openai.com/apps-sdk/build/auth
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Authentication
•	headings: (Anonymous vs signed-in, OAuth, session tokens, backend integration)
•	last_updated:
summary
Auth strategies for apps needing user-specific access: OAuth-style flows, token exchange, and permission scoping. (developers.openai.com)
content
Explains when to gate actions, coordinate backend auth, and secure data. Notes multi-user sharing, privacy, and compliance considerations. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Storage
•	url: https://developers.openai.com/apps-sdk/build/storage
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Storage
•	headings: (State vs durable storage, caching, PII handling, compliance)
•	last_updated:
summary
Persistence patterns beyond conversation state: caching, durable storage, retention, encryption, and handling sensitive data. (developers.openai.com)
content
Covers choosing storage backends, modeling state/artifacts, and ensuring reliability and privacy. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Examples
•	url: https://developers.openai.com/apps-sdk/build/examples
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Examples
•	headings: (Multi-tool servers, pre-built components, metadata mapping)
•	last_updated:
summary
Sample servers/components showing end-to-end tool registration, structured responses, and UI rendering. (developers.openai.com)
content
Demonstrates common patterns—multi-tool coordination, embedded resources for UI, and testing in ChatGPT developer mode. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Deploy your app
•	url: https://developers.openai.com/apps-sdk/deploy
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Deploy your app
•	headings: Hosting | HTTPS endpoints | Platform choices | Configuration
•	last_updated:
summary
Deployment guidance for hosting your MCP server and component bundle with stable HTTPS endpoints and appropriate configuration. (developers.openai.com)
content
Outlines packaging, hosting environments, and environment/config management for reliable production deployments. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Connect from ChatGPT
•	url: https://developers.openai.com/apps-sdk/deploy/connect-chatgpt
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Connect from ChatGPT
•	headings: Developer Mode | Connector registration | Local testing
•	last_updated:
summary
How to connect your developer app from the ChatGPT client for testing/iteration and how to debug common issues. (developers.openai.com)
content
Walks through enabling developer mode, pointing ChatGPT at your MCP server, verifying component rendering, and diagnosing failures. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Test your integration
•	url: https://developers.openai.com/apps-sdk/deploy/testing
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Test your integration
•	headings: Checklists | Error paths | Network & auth | Component behavior
•	last_updated:
summary
Testing strategies across server, components, and ChatGPT client behaviors; systematic checklists and negative tests. (developers.openai.com)
content
Promotes realistic scenarios, network/auth failure testing, and telemetry for precision/recall of tool selection. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Troubleshooting
•	url: https://developers.openai.com/apps-sdk/deploy/troubleshooting
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Troubleshooting
•	headings: Triage by layer | Common errors | Recovery steps
•	last_updated:
summary
Common failure modes and how to isolate the problematic layer (server, component, client) and recover. (developers.openai.com)
content
Encourages targeted fixes, improved observability, and robust error/empty-state UX. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Optimize Metadata
•	url: https://developers.openai.com/apps-sdk/guides/optimize-metadata
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Optimize Metadata
•	headings: Discovery signals | Tool descriptions | Usage hints | Telemetry
•	last_updated:
summary
How enriched tool metadata improves discovery/ranking and shapes in-conversation behavior. (developers.openai.com)
content
Guidance on authoring effective names/descriptions, documenting parameters, and using feedback/analytics to refine recall/precision. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Security & Privacy
•	url: https://developers.openai.com/apps-sdk/guides/security-privacy
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Security & Privacy
•	headings: Data handling | Permissions | Sensitive scopes | Compliance
•	last_updated:
summary
Security/privacy considerations for data flows, permissions, and sensitive scopes in Apps SDK apps. (developers.openai.com)
content
Recommends least-privilege access, retention/encryption strategies, and reviews for regulated data. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
Reference
•	url: https://developers.openai.com/apps-sdk/reference
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: Reference
•	headings: (Bridge API, tool descriptor parameters, component contracts)
•	last_updated:
summary
Formal reference for Apps SDK: component bridge, tool descriptors, structured content mapping to UI. (developers.openai.com)
content
Documents parameters/fields and how components consume structured results in ChatGPT. (Concise summary from the doc set.) (developers.openai.com)
________________________________________
App developer guidelines
•	url: https://developers.openai.com/apps-sdk/app-developer-guidelines
•	domain: developers.openai.com
•	category: Docs (Apps SDK)
•	h1: App developer guidelines
•	headings: Safety | Privacy | Quality bar | Review readiness
•	last_updated:
summary
Preview guidelines for app quality, safety, privacy, accessibility, and performance before inclusion/promotion. (developers.openai.com)
content
Outlines standards for trustworthy UX, data handling, and compliance. Provides expectations for submissions and ongoing maintenance. (Concise summary from the doc set.) (developers.openai.com)




