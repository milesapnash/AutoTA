public class SequenceExpression implements Expression {
    private Expression first;
    private Expression second;

    public SequenceExpression(Expression first, Expression second) {
        this.first = first;
        this.second = second;
    }

    @Override
    public void interpret(Context context) {
        first.interpret(context);
        second.interpret(context);
    }
}
