from .formalizer import ProblemFormalizer
from .schemas import ScientificProblem, ScientificProblemGraph

class ScientificCore:
    def __init__(self): self.formalizer=ProblemFormalizer()
    def formalize(self, prompt: str, context=None) -> tuple[ScientificProblem, ScientificProblemGraph]:
        return self.formalizer.formalize(prompt, context=context)
