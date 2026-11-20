# Related-work positioning

ScopeShift's contribution is the executable combination of temporal application
policy schedules, real MCP tools, an observed local commitment boundary,
independent reconstruction of effects, and benchmark-reliability checks. It does
not claim to invent continuous authorization, transactions, concurrency testing,
mutation testing, property-based testing or MCP.

Primary software artifacts actually used and inspected here are the installed
[official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
1.30.0 (stdio client/session and FastMCP server),
[Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) 0.3.291
(Task, solver, tool, scorer and controlled mock provider),
[Hypothesis](https://github.com/HypothesisWorks/hypothesis) 6.170.16
(RuleBasedStateMachine, seed and shrinking), and SQLite 3.53.1 through the pinned
Python interpreter. Source-level use is tested; these are not claims of novel
upstream vulnerabilities.

The original master supplied AgentDojo, AgentCap, AuthorizationBench,
GatewayBench, MCP Security Bench, UCON, CHESS, Coyote, formal MCP safety
verification and execution-finality authorization literature as research leads.
Those paper-specific references remain **unverified leads**, not citations with
invented authors, dates or findings. No priority or state-of-the-art claim is
based on them. A publication-grade literature comparison remains future research;
this implementation focuses on reproducible executable methodology and scoped
empirical observations.
