from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString

get_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]

def read_card_id():
    card = CardRequest(timeout=None, newcardonly=True).waitforcard()
    card.connection.connect()
    data, sw1, sw2 = card.connection.transmit(get_uid)
    if (sw1, sw2) != (0x90, 0x00):
        raise RuntimeError('Could not read the card UID.')
    return toHexString(data).replace(' ', '')


if __name__ == '__main__':
    print('Tap a card')
    print(read_card_id())