public class ReverseMessenger extends Messenger {
    @Override
    Cipher createCipher() {
        return new ReverseCipher();
    }
}
