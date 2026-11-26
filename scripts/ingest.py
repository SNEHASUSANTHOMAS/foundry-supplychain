"""Ingest supply-chain PDFs from data/ into Azure AI Foundry Vector Stores."""

import json
import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = PROJECT_ROOT / "config" / "vector_stores.json"

DOMAIN_PREFIXES = {
    "cnc_machining": ("cnc_machining_",),
    "injection_moulding": ("injection_moulding_",),
    "fabrication_rules": ("fabrication_rules_",),
    "should_cost": ("heuristics_", "insights_"),
    "procurement_rfq": ("rfq_",),
}


def get_domain_files(prefixes: tuple[str, ...]) -> list[Path]:
    """Return sorted PDF paths matching any of the given filename prefixes."""
    return sorted(
        p for p in DATA_DIR.glob("*.pdf")
        if p.name.startswith(prefixes)
    )


def main() -> None:
    """Create one Foundry Vector Store per domain and upload its PDFs."""
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    openai_client = project.get_openai_client()

    store_ids: dict[str, str] = {}
    if OUTPUT_FILE.exists():
        store_ids = json.loads(OUTPUT_FILE.read_text())

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    for domain, prefixes in DOMAIN_PREFIXES.items():
        if domain in store_ids:
            print(f"[skip] {domain} already indexed -> {store_ids[domain]}")
            continue

        files = get_domain_files(prefixes)
        if not files:
            print(f"[warn] no files found for {domain}")
            continue

        vs = openai_client.vector_stores.create(name=f"supply_chain_{domain}")
        print(f"Created vector store '{domain}': {vs.id} ({len(files)} files)")

        for pdf_path in files:
            print(f"  Uploading {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)...")
            with pdf_path.open("rb") as fh:
                openai_client.vector_stores.files.upload_and_poll(
                    vector_store_id=vs.id,
                    file=fh,
                )

        store_ids[domain] = vs.id
        OUTPUT_FILE.write_text(json.dumps(store_ids, indent=2) + "\n")
        print(f"Saved {domain} -> {vs.id}")

    print("\nAll vector stores ready:", json.dumps(store_ids, indent=2))


if __name__ == "__main__":
    main()

