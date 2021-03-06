from urllib.parse import urlparse, quote as url_quote

import pytest
from pathlib import Path

from django.conf import settings

from normandy.base.tests import Whatever
from normandy.studies.models import Extension
from normandy.studies.tests import ExtensionFactory
from normandy.studies.api.v3.fields import ExtensionFileField


@pytest.mark.django_db
class TestExtensionAPI(object):
    @classmethod
    def data_path(cls, file_name):
        return Path(settings.BASE_DIR) / "normandy/studies/tests/data" / file_name

    def test_it_works(self, api_client):
        res = api_client.get("/api/v3/extension/")
        assert res.status_code == 200
        assert res.data["results"] == []

    def test_it_serves_extensions(self, api_client, storage):
        extension = ExtensionFactory(name="foo")

        res = api_client.get("/api/v3/extension/")
        assert res.status_code == 200
        assert res.data["results"] == [{"id": extension.id, "name": "foo", "xpi": Whatever()}]

    def test_list_view_includes_cache_headers(self, api_client):
        res = api_client.get("/api/v3/extension/")
        assert res.status_code == 200
        # It isn't important to assert a particular value for max-age
        assert "max-age=" in res["Cache-Control"]
        assert "public" in res["Cache-Control"]

    def test_detail_view_includes_cache_headers(self, api_client, storage):
        extension = ExtensionFactory()
        res = api_client.get("/api/v3/extension/{id}/".format(id=extension.id))
        assert res.status_code == 200
        # It isn't important to assert a particular value for max-age
        assert "max-age=" in res["Cache-Control"]
        assert "public" in res["Cache-Control"]

    def test_list_sets_no_cookies(self, api_client):
        res = api_client.get("/api/v3/extension/")
        assert res.status_code == 200
        assert "Cookies" not in res

    def test_detail_sets_no_cookies(self, api_client, storage):
        extension = ExtensionFactory()
        res = api_client.get("/api/v3/extension/{id}/".format(id=extension.id))
        assert res.status_code == 200
        assert res.client.cookies == {}

    def test_filtering_by_name(self, api_client, storage):
        matching_extension = ExtensionFactory()
        ExtensionFactory()  # Generate another extension that will not match

        res = api_client.get(f"/api/v3/extension/?text={matching_extension.name}")
        assert res.status_code == 200
        assert [ext["name"] for ext in res.data["results"]] == [matching_extension.name]

    def test_filtering_by_xpi(self, api_client, storage):
        matching_extension = ExtensionFactory()
        ExtensionFactory()  # Generate another extension that will not match

        res = api_client.get(f"/api/v3/extension/?text={matching_extension.xpi}")
        assert res.status_code == 200
        expected_path = matching_extension.xpi.url
        assert [urlparse(ext["xpi"]).path for ext in res.data["results"]] == [expected_path]

    def _upload_extension(self, api_client, path):
        with open(path, "rb") as f:
            res = api_client.post(
                "/api/v3/extension/", {"name": "test extension", "xpi": f}, format="multipart"
            )
        return res

    def test_upload_works_webext(self, api_client, storage):
        path = self.data_path("webext-signed.xpi")
        res = self._upload_extension(api_client, path)
        assert res.status_code == 201  # created
        Extension.objects.filter(id=res.data["id"]).exists()

    def test_upload_works_legacy(self, api_client, storage):
        path = self.data_path("legacy-signed.xpi")
        res = self._upload_extension(api_client, path)
        assert res.status_code == 201  # created
        Extension.objects.filter(id=res.data["id"]).exists()

    def test_uploads_must_be_zips(self, api_client, storage):
        path = self.data_path("not-an-addon.txt")
        res = self._upload_extension(api_client, path)
        assert res.status_code == 400  # Client error
        assert res.data == {"xpi": [ExtensionFileField.default_error_messages["not_a_zip"]]}

    def test_uploads_must_be_signed_webext(self, api_client, storage):
        path = self.data_path("webext-unsigned.xpi")
        res = self._upload_extension(api_client, path)
        assert res.status_code == 400  # Client error
        assert res.data == {"xpi": [ExtensionFileField.default_error_messages["not_signed"]]}

    def test_uploads_must_be_signed_legacy(self, api_client, storage):
        path = self.data_path("legacy-unsigned.xpi")
        res = self._upload_extension(api_client, path)
        assert res.status_code == 400  # Client error
        assert res.data == {"xpi": [ExtensionFileField.default_error_messages["not_signed"]]}

    def test_uploaded_webexts_must_have_id(self, api_client, storage):
        # NB: This is a fragile test. It uses a unsigned webext, and
        # so it relies on the ID check happening before the signing
        # check, so that the error comes from the former.
        path = self.data_path("webext-no-id-unsigned.xpi")
        res = self._upload_extension(api_client, path)
        assert res.status_code == 400  # Client error
        assert res.data == {"xpi": [ExtensionFileField.default_error_messages["no_id"]]}

    def test_keeps_extension_filename(self, api_client, storage):
        filename = "bootstrap-addon-example@mozilla.org-0.1.0.xpi"
        path = self.data_path(filename)
        res = self._upload_extension(api_client, path)
        assert res.status_code == 201, f"body of unexpected response: {res.data}"  # created
        assert res.data["xpi"].split("/")[-1] == url_quote(filename)

        # Download the XPI to make sure the url is actually good
        res = api_client.get(res.data["xpi"], follow=True)
        assert res.status_code == 200

    def test_order_name(self, api_client, storage):
        e1 = ExtensionFactory(name="a")
        e2 = ExtensionFactory(name="b")

        res = api_client.get(f"/api/v3/extension/?ordering=name")
        assert res.status_code == 200
        assert [r["id"] for r in res.data["results"]] == [e1.id, e2.id]

        res = api_client.get(f"/api/v3/extension/?ordering=-name")
        assert res.status_code == 200
        assert [r["id"] for r in res.data["results"]] == [e2.id, e1.id]

    def test_order_id(self, api_client, storage):
        e1 = ExtensionFactory()
        e2 = ExtensionFactory()
        assert e1.id < e2.id

        res = api_client.get(f"/api/v3/extension/?ordering=id")
        assert res.status_code == 200
        assert [r["id"] for r in res.data["results"]] == [e1.id, e2.id]

        res = api_client.get(f"/api/v3/extension/?ordering=-id")
        assert res.status_code == 200
        assert [r["id"] for r in res.data["results"]] == [e2.id, e1.id]

    def test_order_bogus(self, api_client, storage):
        """Test that filtering by an unknown key doesn't change the sort order"""
        ExtensionFactory()
        ExtensionFactory()

        res = api_client.get(f"/api/v3/extension/?ordering=bogus")
        assert res.status_code == 200
        first_ordering = [r["id"] for r in res.data["results"]]

        res = api_client.get(f"/api/v3/extension/?ordering=-bogus")
        assert res.status_code == 200
        assert [r["id"] for r in res.data["results"]] == first_ordering
