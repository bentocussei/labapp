# LABAPP

LABAPP é uma API desenvolvida em Django que gerencia informações sobre escolas, permitindo a criação, atualização, exclusão e importação de dados a partir de um arquivo Excel.

![LABAPP API](files/img/api.png)

## Requisitos

- Veja o arquivo requirements.txt.

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/bentocussei/labapp.git
```
2. Instale as dependências:

3. Configure o banco de dados no arquivo settings.py.

4. Execute as migrações:

```bash
python manage.py migrate
```
5. Inicie o servidor:

```bash
python manage.py runserver
```
## Uso

### Endpoints da API
- GET /escolas/: Lista todas as escolas.
- GET /escolas/{id}/: Retorna detalhes de uma escola específica.
- POST /escolas/: Cria uma nova escola.
- PUT /escolas/{id}/: Atualiza os detalhes de uma escola existente.
- PATCH /escolas/{id}/: Atualiza parcialmente os detalhes de uma escola existente.
- DELETE /escolas/{id}/: Exclui uma escola existente.
- POST /escolas/upload-excel/: Importa dados de escolas a partir de um arquivo Excel.
- POST /escolas/filter_by_provincia/: Filtra as escolas com base nas províncias fornecidas no JSON no corpo da requisição.

### Autenticação
API aberta

## Testes

![LABAPP API](files/img/testes.png)
