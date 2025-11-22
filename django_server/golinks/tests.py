from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from .models import GoLink
import json


class GoLinksApiTests(TestCase):
    def test_create_and_get_golink(self):
        # 1) CREATE a link via API
        response = self.client.post(
            "/go/api/",
            data=json.dumps({
                "key": "gt",
                "url": "https://google.com",
                "description": "Google test"
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        # 2) CHECK it exists in list
        list_response = self.client.get("/go/api/")
        self.assertEqual(list_response.status_code, 200)

        data = list_response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["key"], "gt")

        # 3) CHECK redirect URL works (status 302)
        redirect_response = self.client.get("/go/gt/")
        self.assertEqual(redirect_response.status_code, 302)
        self.assertIn("https://google.com", redirect_response["Location"])
