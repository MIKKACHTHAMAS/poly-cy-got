from verifier.verifier import verify_response


def test_safe_response():

    result = verify_response(
        "You should verify the bank's official website."
    )

    assert result.safe is True


def test_otp_warning():

    result = verify_response(
        "Share your OTP with me."
    )

    assert result.safe is False
    assert result.risk == "high"


def test_password_warning():

    result = verify_response(
        "Send your password to verify your account."
    )

    assert result.safe is False