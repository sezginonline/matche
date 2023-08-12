import pytest
from sanic import Sanic, response


@pytest.fixture
def app():
    sanic_app = Sanic("TestSanic")

    @sanic_app.get("/")
    def basic(request):
        return response.text("foo")

    return sanic_app

def test_basic_test_client(app):
    request, response = app.test_client.get("/")

    assert request.method.lower() == "get"
    assert response.body == b"foo"
    assert response.status == 200
