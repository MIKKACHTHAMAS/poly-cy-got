from pathlib import Path


class MeTTaEngine:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.knowledge_dir = self.base_dir / "knowledge"
        self.rules_dir = self.base_dir / "rules"
        self.queries_dir = self.base_dir / "queries"

        self.metta = None
        self._initialize()

    def _initialize(self):
        try:
            from hyperon import MeTTa
            self.metta = MeTTa()
            self._load_files()
        except ImportError:
            print("WARNING: Hyperon is not installed. MeTTa engine unavailable.")

    def _load_files(self):
        if self.metta is None:
            return

        files = [
            self.knowledge_dir / "actions.metta",
            self.knowledge_dir / "threats.metta",
            self.knowledge_dir / "indicators.metta",
            self.knowledge_dir / "patterns.metta",
            self.rules_dir / "safety.metta",
            self.rules_dir / "phishing.metta",
            self.rules_dir / "verification.metta",
        ]

        for file in files:
            if not file.exists():
                continue

            source = file.read_text(encoding="utf-8")

            # Load each top-level atom into the AtomSpace.
            atoms = self.metta.parse_all(source)

            for atom in atoms:
                self.metta.space().add_atom(atom)

    def run(self, expression: str):
        if self.metta is None:
            return []

        return self.metta.run(expression)

    def query(self, pattern: str, result: str = "$result"):
        """
        Query the current MeTTa AtomSpace.

        Example:
            engine.query("(unsafe-action share-otp)", "$x")
        """
        if self.metta is None:
            return []

        expression = f"!(match &self {pattern} {result})"
        return self.metta.run(expression)

    def available(self):
        return self.metta is not None
