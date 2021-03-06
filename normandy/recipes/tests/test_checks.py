from datetime import timedelta

import pytest

from normandy.recipes import checks, signing
from normandy.recipes.tests import RecipeFactory, SignatureFactory


@pytest.mark.django_db
class TestSignaturesUseGoodCertificates(object):
    def test_it_works(self):
        assert checks.signatures_use_good_certificates(None) == []

    def test_it_fails_if_a_signature_does_not_verify(self, mocker, settings):
        settings.CERTIFICATES_EXPIRE_EARLY_DAYS = None
        recipe = RecipeFactory(signed=True)
        mock_verify_x5u = mocker.patch("normandy.recipes.checks.signing.verify_x5u")
        mock_verify_x5u.side_effect = signing.BadCertificate("testing exception")

        errors = checks.signatures_use_good_certificates(None)
        mock_verify_x5u.assert_called_once_with(recipe.signature.x5u, None)
        assert len(errors) == 1
        assert errors[0].id == checks.WARNING_BAD_SIGNING_CERTIFICATE

    def test_it_ignores_signatures_not_in_use(self, mocker, settings):
        settings.CERTIFICATES_EXPIRE_EARLY_DAYS = None
        recipe = RecipeFactory(signed=True)
        SignatureFactory(x5u="https://example.com/bad_x5u")  # unused signature
        mock_verify_x5u = mocker.patch("normandy.recipes.checks.signing.verify_x5u")

        def side_effect(x5u, *args):
            if "bad" in x5u:
                raise signing.BadCertificate("testing exception")
            return True

        mock_verify_x5u.side_effect = side_effect

        errors = checks.signatures_use_good_certificates(None)
        mock_verify_x5u.assert_called_once_with(recipe.signature.x5u, None)
        assert errors == []

    def test_it_passes_expire_early_setting(self, mocker, settings):
        settings.CERTIFICATES_EXPIRE_EARLY_DAYS = 7
        recipe = RecipeFactory(signed=True)
        mock_verify_x5u = mocker.patch("normandy.recipes.checks.signing.verify_x5u")

        errors = checks.signatures_use_good_certificates(None)
        mock_verify_x5u.assert_called_once_with(recipe.signature.x5u, timedelta(7))
        assert errors == []
