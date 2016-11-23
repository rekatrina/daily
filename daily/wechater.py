import hashlib
import local_settings

def check_signature(signature, timestamp, nonce):
    if not signature or not timestamp or not nonce:
        return False

    L = [timestamp, nonce, local_settings.token_recall]
    L.sort()
    s = L[0] + L[1] + L[2]
    return hashlib.sha1(s).hexdigest() == signature


def VerifyURL(signature, timestamp, nonce, echoStr):
    if check_signature(signature, timestamp, nonce):
        return 1;