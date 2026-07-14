from app.security import make_signature, verify_signature


def test_hmac_signature_round_trip():
    body=b'{"method":"mechanics.kinetic_energy"}'
    signature=make_signature('secret','1700000000','POST','/v1/compute/run',body)
    assert len(signature)==64
    assert verify_signature('secret','1700000000','POST','/v1/compute/run',body,signature)
    assert not verify_signature('wrong','1700000000','POST','/v1/compute/run',body,signature)
