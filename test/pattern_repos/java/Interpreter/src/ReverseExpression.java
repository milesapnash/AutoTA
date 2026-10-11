public class ReverseExpression implements Expression {
    @Override
    public void interpret(Context context) {
        String reversed = new StringBuilder(context.getText()).reverse().toString();
        context.setText(reversed);
    }
}
