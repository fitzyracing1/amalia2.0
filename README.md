# Amalia 2.0

> **Modern Python SDK, CLI, and Boilerplate for Amália — Portugal's National LLM**

**Status:** In Active Development (v2.0 Alpha)  
**License:** MIT  
**Website:** https://fitzyracing1.github.io/amalia2.0  
**PyPI (planned):** `pip install amalia2`  
**Original SDK:** [alfmatos/amalia](https://github.com/alfmatos/amalia)

---

## Vision

**Amalia 2.0** is the next-generation developer experience for **Amália**, the fully open-source Portuguese (pt-PT) large language model from the AMALIA-LLM initiative.

While the original SDK provided a solid foundation, Amalia 2.0 delivers a **batteries-included, visually-documented, ecosystem-aware boilerplate** that makes it dramatically easier and more enjoyable to build production-grade applications with Amália.

Key pillars:
- **Exceptional Developer Experience** — Rich CLI, beautiful docs, instant project templates
- **Agent-Native Architecture** — First-class support for multi-agent systems, tools, and skills
- **Portuguese Excellence** — Deep optimization for European Portuguese language, culture, and evaluation benchmarks
- **Ecosystem Integration** — Seamless connection with 3XB Entity Intelligence, Pie Face Mobile OS, quantum sensing prototypes, and more
- **Open & Community-Driven** — Designed for rapid contribution and real-world deployment

This project draws inspiration from the pioneering work of the AMALIA-LLM organization and the original community SDK, while pushing the boundaries of what a national LLM platform can offer developers.

---

## Key Features

- **Modern Async Client** — High-performance async/await support with streaming, retries, and structured outputs
- **Powerful Typer + Rich CLI** — Beautiful terminal interface with progress bars, syntax highlighting, and interactive chat
- **Agent & Skill Framework** — Define tools, skills, and multi-agent orchestrators with minimal boilerplate
- **Project Templates** — `amalia2 new my-app` instantly scaffolds a full project (RAG, chatbot, evaluation harness, mobile companion, etc.)
- **First-Class Documentation** — Living website with interactive examples, architecture diagrams, and Portuguese-specific guidance
- **Evaluation & Benchmarking** — Built-in support for ALBA, PHEB, and AMALIA-LM-Eval style benchmarks
- **Ecosystem Ready** — Native integrations with 3XB for entity extraction on Portuguese text, Loopa safety, Fire Fire Coin payments, etc.

---

## Quick Start

```bash
# From source (not yet on PyPI)
git clone https://github.com/fitzyracing1/amalia2.0
cd amalia2.0
pip install -e ".[dev]"

# Credentials — env vars, or a creds.txt in cwd / ~/.amalia/
export AMALIA_API_KEY=sk-usr-...
export AMALIA_AGENT_ID=<your-agent-id>
export AMALIA_CHANNEL_ID=<your-channel-id>
# optional: export AMALIA_BASE_URL=https://api.iaedu.pt/agent-chat

# Interactive streaming chat
amalia2 chat

# Scaffolding is not implemented yet (phase 03)
amalia2 new my-portuguese-app --template rag-chatbot
```

See [docs/getting-started.md](docs/getting-started.md) or the [project website](https://fitzyracing1.github.io/amalia2.0).

---

## Project Structure

```
amalia2.0/
├── src/amalia2/           # Core package
│   ├── client.py          # Async IAEdu streaming client
│   ├── config.py          # AMALIA_* env + creds.txt loading
│   ├── errors.py          # Typed API errors
│   └── cli.py             # Typer CLI (`chat`, `version`, `new`)
├── examples/              # Ready-to-run examples
├── templates/             # Cookiecutter / copier templates for new projects
├── docs/                  # Beautiful GitHub Pages website
├── skills/                # Community + official skills
└── pyproject.toml
```

---

## Roadmap

| Phase | Focus                              | Status      |
|-------|------------------------------------|-------------|
| 01    | Core async client + beautiful CLI  | In Progress |
| 02    | Agent framework + skill system     | Planned     |
| 03    | Project templates & scaffolding    | Planned     |
| 04    | Deep ecosystem integrations (3XB, Pie Face, etc.) | Planned |
| 05    | Production examples + benchmarks   | Future      |
| 06    | PyPI release + community growth    | Future      |

Full interactive roadmap and technical architecture available on the [project website](#).

---

## Ecosystem & Integrations

Amalia 2.0 is designed to be a first-class citizen in ambitious Portuguese and European AI stacks:

- **3XB AI** — Entity intelligence, weighted tagging, and alt-credit modeling on Portuguese text
- **Pie Face Mobile OS** — Lightweight on-device inference and mobile agents
- **Organic Spin Processor** — Future quantum-enhanced Portuguese language understanding
- **BMD AI Agents** — Defensive multi-agent coordination (conceptual)
- **Community Plan, Inc. legacy** — Real-world fintech and community applications

We believe national LLMs like Amália deserve world-class tooling.

---

## Contributing

We welcome contributions from Portuguese speakers, LLM enthusiasts, agent builders, and anyone passionate about sovereign AI tooling.

Please read [docs/contributing.md](docs/contributing.md). Visual contributions (diagrams, UI mocks for the chat client, example screenshots) are especially valued.

---

## License & Acknowledgments

MIT License.

Built with deep respect for the **AMALIA-LLM** organization, the original community SDK by @alfmatos, and everyone advancing open Portuguese language technology.

Special thanks to the Grok & xAI ecosystem for accelerating ambitious builder workflows.

---

**Amalia 2.0** • Modern tooling for Portugal's LLM • fitzyracing1 • 2026

*Part of the Earthenware Computer ecosystem — Tagging for everyone and everything.*
## Documentation

- In-repo docs: [docs/](docs/index.md)
- Wiki: [https://github.com/fitzyracing1/amalia2.0/wiki](https://github.com/fitzyracing1/amalia2.0/wiki)

## Plans

This project is free, and its license stays as is. Support it through [GitHub Sponsors](https://github.com/sponsors/fitzyracing1):

- **Free**: use the code, community support.
- **Free (followers)**: follow me on X or GitHub and get free consulting on my products.
- **Pro ($49/month)**: priority issues and support.
- **Team ($199/month)**: priority support for your team plus early access.
