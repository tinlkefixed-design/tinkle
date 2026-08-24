from tinkle.metamind.schemas import TaskType

class TaskClassifier:
    def classify(self, prompt: str) -> TaskType:
        p = prompt.lower()
        if any(x in p for x in ("python", "code", "program", "debug")):
            return TaskType.coding
        if any(x in p for x in ("research", "paper", "sources", "study")):
            return TaskType.research
        if any(x in p for x in ("calculate", "equation", "proof", "solve")):
            return TaskType.reasoning
        if any(x in p for x in ("data", "csv", "dataset", "statistics")):
            return TaskType.data_analysis
        if any(x in p for x in ("experiment", "physics", "chemistry", "biology")):
            return TaskType.scientific
        if any(x in p for x in ("write", "story", "poem", "design")):
            return TaskType.creative
        if len(p.split()) <= 12:
            return TaskType.simple
        return TaskType.unknown
