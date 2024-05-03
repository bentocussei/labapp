import pytest
from rest_framework.test import APIRequestFactory
from rest_framework import status
from .models import Escola
from .views import EscolaViewSet

@pytest.mark.django_db
def test_list_escolas():
    factory = APIRequestFactory()
    request = factory.get('/escolas/')
    response = EscolaViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0  # Não há escolas criadas ainda

@pytest.mark.django_db
def test_retrieve_escola():
    escola = Escola.objects.create(nome="Escola Teste", email="teste@email.com", numero_salas=15, provincia=["Luanda"])
    factory = APIRequestFactory()
    request = factory.get(f'/escolas/{escola.pk}/')
    response = EscolaViewSet.as_view({'get': 'retrieve'})(request, pk=escola.pk)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == escola.nome
    assert response.data['email'] == escola.email
    assert response.data['numero_salas'] == escola.numero_salas
    assert response.data['provincia'] == escola.provincia

@pytest.mark.django_db
def test_retrieve_escola_not_found():
    factory = APIRequestFactory()
    request = factory.get('/escolas/1000/')
    response = EscolaViewSet.as_view({'get': 'retrieve'})(request, pk=1000)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_update_escola():
    escola = Escola.objects.create(nome="Escola Teste", email="teste@email.com", numero_salas=15, provincia=["Luanda"])
    factory = APIRequestFactory()
    data = {
        "nome": "Escola Atualizada",
        "email": "atualizado@email.com",
        "numero_salas": 25,
        "provincia": ["Huíla"],
    }
    request = factory.put(f'/escolas/{escola.pk}/', data, format='json')
    response = EscolaViewSet.as_view({'put': 'update'})(request, pk=escola.pk)
    assert response.status_code == status.HTTP_200_OK
    escola.refresh_from_db()
    assert escola.nome == data['nome']
    assert escola.email == data['email']
    assert escola.numero_salas == data['numero_salas']
    assert escola.provincia == data['provincia']

@pytest.mark.django_db
def test_update_escola_not_found():
    factory = APIRequestFactory()
    request = factory.put('/escolas/1000/', {})
    response = EscolaViewSet.as_view({'put': 'update'})(request, pk=1000)

    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_update_escola_invalid_data():
    escola = Escola.objects.create(nome="Escola Teste", email="teste@email.com", numero_salas=15, provincia=["Luanda"])
    factory = APIRequestFactory()
    data = {"email": "invalid_email"}
    request = factory.put(f'/escolas/{escola.pk}/', data, format='json')
    response = EscolaViewSet.as_view({'put': 'update'})(request, pk=escola.pk)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data 

@pytest.mark.django_db
def test_partial_update_escola():
    escola = Escola.objects.create(nome="Escola Teste", email="teste@email.com", numero_salas=15, provincia=["Luanda"])
    factory = APIRequestFactory()
    data = {"numero_salas": 20}
    request = factory.patch(f'/escolas/{escola.pk}/', data, format='json')
    response = EscolaViewSet.as_view({'patch': 'partial_update'})(request, pk=escola.pk)

    assert response.status_code == status.HTTP_200_OK
    escola.refresh_from_db()
    assert escola.nome == "Escola Teste"
    assert escola.email == "teste@email.com"
    assert escola.numero_salas == 20
    assert escola.provincia == ["Luanda"]

@pytest.mark.django_db
def test_destroy_escola():
    escola = Escola.objects.create(nome="Escola Teste", email="teste@email.com", numero_salas=15, provincia=["Luanda"])
    factory = APIRequestFactory()
    request = factory.delete(f'/escolas/{escola.pk}/')
    response = EscolaViewSet.as_view({'delete': 'destroy'})(request, pk=escola.pk)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Escola.objects.count() == 0

@pytest.mark.django_db
def test_destroy_escola_not_found():
    factory = APIRequestFactory()
    request = factory.delete('/escolas/1000/')
    response = EscolaViewSet.as_view({'delete': 'destroy'})(request, pk=1000)

    assert response.status_code == status.HTTP_404_NOT_FOUND