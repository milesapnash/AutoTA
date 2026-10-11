public class CaesarMessenger extends Messenger {
    @Override
    Cipher createCipher() {
        return new CaesarCipher();
    }
}
