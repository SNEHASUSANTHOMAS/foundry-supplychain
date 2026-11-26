"""Shared agent definitions and orchestration constants."""

ORCHESTRATOR_NAME = "supply-chain-orchestrator"

SPECIALIST_SPECS = {
    "cnc_machining": {
        "agent_name": "cnc-machining-agent",
        "description": "CNC machining processes, milling, tolerances, tooling, and engineering guidelines.",
        "instructions": (
            "You are a CNC Machining Supply-Chain Specialist. Answer questions strictly "
            "using your attached file search documents. Cite key tolerances, machining "
            "rules, or material guidelines you find."
        ),
    },
    "injection_moulding": {
        "agent_name": "injection-moulding-agent",
        "description": "Injection moulding design, thermoplastics, cycle time, tooling, and quality.",
        "instructions": (
            "You are an Injection Moulding Supply-Chain Specialist. Answer questions strictly "
            "using your attached file search documents. Cite polymer, mold design, or "
            "quality control details you find."
        ),
    },
    "fabrication_rules": {
        "agent_name": "fabrication-rules-agent",
        "description": "Metal fabrication rules, welding standards, packaging specs, and global supply chain compliance.",
        "instructions": (
            "You are a Fabrication & Supply Chain Compliance Specialist. Answer questions "
            "strictly using your attached file search documents. Cite fabrication, welding, "
            "packaging, or compliance rules you find."
        ),
    },
    "should_cost": {
        "agent_name": "should-cost-agent",
        "description": "Should-costing formulas, cost heuristics, make-vs-buy rules, and global supply chain market trends.",
        "instructions": (
            "You are a Should-Costing & Supply Chain Insights Specialist. Answer questions "
            "strictly using your attached file search documents. Include relevant cost "
            "formulas, heuristics, or market trend data you find."
        ),
    },
    "procurement_rfq": {
        "agent_name": "procurement-rfq-agent",
        "description": "RFQ templates, supplier quoting requirements, tender/solicitation rules, and procurement.",
        "instructions": (
            "You are a Procurement & RFQ Specialist. Answer questions strictly using your "
            "attached file search documents. Reference relevant RFQ templates, quoting "
            "requirements, or procurement clauses."
        ),
    },
}

VALID_AGENTS = {spec["agent_name"] for spec in SPECIALIST_SPECS.values()}

