class MarkdownChecker:
    def __init__(self):
        self.rules = []

    def define_rule(self, func):
        self.rules.append(func)
        return func

checker = MarkdownChecker()
