public class UpperExpression implements Expression {
    @Override
    public void interpret(Context context) {
        context.setText(context.getText().toUpperCase());
    }
}
