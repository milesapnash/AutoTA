from expression import Expression


class UpperExpression(Expression):
    def interpret(self, context):
        context.set_text(context.get_text().upper())
