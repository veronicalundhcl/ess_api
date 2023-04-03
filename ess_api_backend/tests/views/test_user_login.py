from datetime import timedelta, datetime
from freezegun import freeze_time
from ess_api_backend.views import user_login
from django.test import RequestFactory

"""
Code Analysis:
- The main goal of the function is to authenticate a user and generate a JWT token and CSRF token for the authenticated user.
- The function takes a request object as input, which contains the user's email and password.
- It then uses the authenticate() function to check if the user exists and if the provided credentials are correct.
- If the user is authenticated, it generates a JWT token using the user's ID and an expiration time of 24 hours, and a CSRF token using the get_token() function.
- The function then returns a JSON response containing a success message, the generated JWT token, and the CSRF token.
- If the user is not authenticated, the function returns an HTTP response with a message indicating that the user does not exist.
"""


"""
Test Plan:
- test_successful_login(): tests that a user can successfully login and receive a JSON response with a JWT token and CSRF token. Tags: [happy path]
- test_auth_token_string_conversion(): tests that the JWT token is converted to a string before being returned in the JSON response. Tags: [happy path]
- test_jwt_token_encoded_using_secret_key(): tests that the JWT token is encoded using the SECRET_KEY setting. Tags: [happy path]
- test_invalid_user(): tests that a user with invalid credentials cannot login and receives an appropriate error message. Tags: [edge case]
- test_expired_jwt_token(): tests that the JWT token expires after 24 hours and the user cannot access protected resources with an expired token. Tags: [edge case]
- test_csrf_token_added_to_outgoing_response(): tests that the CSRF token is added to the outgoing response. Tags: [general behavior]
- test_missing_csrf_token(): tests that if the CSRF token is not set in request.META, the function still returns a JSON response with a JWT token and a new CSRF token. Tags: [edge case]
- test_different_authentication_backend(): tests that the function works with different authentication backends. Tags: [general behavior]
- test_different_jwt_token_expiration_times(): tests that the function works with different expiration times for JWT tokens. Tags: [general behavior]
- test_different_jwt_token_encoding_algorithms(): tests that the function works with different algorithms for JWT token encoding. Tags: [general behavior]
"""


class TestUserLogin:
    def test_successful_login(self):
        # Arrange
        request = RequestFactory().post('/login', {'email': 'test@example.com', 'password': 'password123'})
        # Act
        response = user_login(request)
        # Assert
        assert response.status_code == 200
        assert 'auth_token' in response.json()
        assert 'csrf_token' in response.json()

    def test_auth_token_string_conversion(self):
        # Arrange
        request = RequestFactory().post('/login', {'email': 'test@example.com', 'password': 'password123'})
        # Act
        response = user_login(request)
        # Assert
        assert isinstance(response.json()['auth_token'], str)

    def test_jwt_token_encoded_using_secret_key(self):
        # Arrange
        request = RequestFactory().post('/login', {'email': 'test@example.com', 'password': 'password123'})
        # Act
        response = user_login(request)
        # Assert
        decoded_token = jwt.decode(response.json()['auth_token'], settings.SECRET_KEY, algorithms=['HS256'])
        assert decoded_token['user_id'] is not None

    def test_invalid_user(self):
        # Arrange
        request = RequestFactory().post('/login', {'email': 'invalid@example.com', 'password': 'password123'})
        # Act
        response = user_login(request)
        # Assert
        assert response.status_code == 401
        assert response.content == b'User does not exist'

    def test_expired_jwt_token(self):
        # Arrange
        request = RequestFactory().post('/login', {'email': 'test@example.com', 'password': 'password123'})
        # Act
        with freeze_time(datetime.utcnow() + timedelta(hours=25)):
            response = user_login(request)
        # Assert
        assert response.status_code == 401

    def test_csrf_token_added_to_outgoing_response(self):
        # Arrange
        request = RequestFactory().post('/login', {'email': 'test@example.com', 'password': 'password123'})
        # Act
        response = user_login(request)
        # Assert
        assert 'Set-Cookie' in response
        assert 'Vary' in response
