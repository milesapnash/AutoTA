from expression import Expression


class ReverseExpression(Expression):
    def interpret(self, context):
        context.set_text(context.get_text()[::-1])
