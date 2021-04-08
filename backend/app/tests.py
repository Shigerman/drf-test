from rest_framework.test import APITestCase
from rest_framework import status
from icecream import ic
from backend.app.serializers import UserSerializer, ItemSerializer
from backend.app.models import Item

class RestTests(APITestCase):

    def _create_user(self, username="foo", password="foo"):
        data = {'username': username, 'password': password}
        return self.client.post('/register/', data)


    def _login_user(self, username="foo", password="foo"):
        data = {'username': username, 'password': password}
        return self.client.post('/login/', data)


    def _create_item(self, user_token, item_name):
        auth = {'HTTP_AUTHORIZATION': f'Token {user_token}'}
        self.client.credentials(**auth) # type: ignore
        data = {'name': item_name}
        return self.client.post('/items/new/', data)


    def _send_item(self, item_id, username):
        data = {'item_id': item_id, 'username': username}
        return self.client.post('/send/', data)


    def test_user_can_be_created(self):
        # Act
        response = self._create_user()

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_user_can_be_logged_in(self):
        # Arrange
        self._create_user()

        # Act
        response = self._login_user()

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["token"]) # type: ignore


    def test_user_can_create_item(self):
        # Arrange
        self._create_user()
        token = self._login_user().data.get("token") # type: ignore

        # Act
        response = self._create_item(user_token=token, item_name="something")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    

    def test_user_can_delete_an_item(self):
        # Arrange
        self._create_user()
        token = self._login_user().data.get("token") # type: ignore
        item_name = "coffee"
        self._create_item(user_token=token, item_name=item_name)
        item = Item.objects.get(name=item_name)
        self.assertEqual(item.name, item_name)

        # Act
        response = self.client.delete(f'/items/{item.id}/')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Item.objects.filter(name=item_name).first(), None)


    def test_user_can_send_item_to_another_user(self):
        # Arrange
        # create sender
        self._create_user()
        token = self._login_user().data.get("token") # type: ignore
        response = self._create_item(user_token=token, item_name="something")
        item_id = response.data.get("item_id") # type: ignore
        # create receiver
        receiver_name = "bar"
        self._create_user(username=receiver_name)

        # Act
        response = self._send_item(item_id=item_id, username=receiver_name)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_user_can_get_their_item_list(self):
        # Arrange
        self._create_user()
        token = self._login_user().data.get("token") # type: ignore
        item_count = 2
        self._create_item(user_token=token, item_name="book")
        self._create_item(user_token=token, item_name="pc")

        # Act
        data = {'token': token}
        response = self.client.get('/items/', data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), item_count)
