class Subject:
    def __init__(self, code, name, credit_hours):
        self.code = code
        self.name = name
        self.credit_hours = int(credit_hours)

    def serialize(self):
        return f"{self.code} | {self.name} | {self.credit_hours}\n"

    @staticmethod
    def deserialize(line):
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            return None
        return Subject(parts[0], parts[1], parts[2])
