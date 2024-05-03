from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import Escola
from .serializers import EscolaSerializer
import pandas as pd
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.views import APIView

class EscolaViewSet(viewsets.ModelViewSet):
    queryset = Escola.objects.all()
    serializer_class = EscolaSerializer

    @swagger_auto_schema(
        responses={200: 'OK', 404: 'Not Found'},
        operation_description="Recupera uma escola específica pelo seu ID."
    )
    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk=pk)

    @swagger_auto_schema(
        responses={204: 'No Content', 404: 'Not Found'},
        operation_description="Exclui uma escola específica pelo seu ID."
    )
    def destroy(self, request, pk=None):
        return super().destroy(request, pk=pk)
    
    @swagger_auto_schema(
        responses={200: 'OK'},
        operation_description="Lista todas as escolas."
    )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        responses={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
        operation_description="Atualiza parcialmente os detalhes de uma escola existente."
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk=pk)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nome': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'numero_salas': openapi.Schema(type=openapi.TYPE_INTEGER),
                'provincia': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
            },
            required=['nome', 'email', 'numero_salas', 'provincia']
        ),
        responses={201: 'Created', 400: 'Bad Request'},
        operation_description="Cria uma nova escola com os dados fornecidos no corpo da requisição."
    )
    def create(self, request):
        # Validar os dados antes de criar uma nova escola
        data = request.data
        serializer = EscolaSerializer(data=data)

        if serializer.is_valid():
            print(data, 'es valido')
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nome': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'numero_salas': openapi.Schema(type=openapi.TYPE_INTEGER),
                'provincia': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
            },
            required=[]
        ),
        responses={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
        operation_description="Atualiza uma escola existente com os dados fornecidos no corpo da requisição."
    )
    def update(self, request, pk=None, partial=False):
        try:
            escola = self.get_queryset().get(pk=pk)
        except Escola.DoesNotExist:
            return Response({"message": "Escola não encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Validar os dados antes de atualizar a escola
        serializer = EscolaSerializer(instance=escola, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'provincias', 
                openapi.IN_QUERY, 
                type=openapi.TYPE_STRING,
                description='Filtrar escolas por província (separadas por vírgula).'
            )
        ],
        responses={200: 'OK'},
        operation_description="Filtra as escolas com base nas províncias fornecidas nos parâmetros da requisição."
    )
    @action(detail=False, methods=['get'], name='filter_by_provincia', url_path='filter_by_provincia')
    def filter_by_provincia(self, request):
        provincias_desejadas = request.GET.get('provincias')

        if provincias_desejadas:
            queryset = self.queryset.filter(provincia__contains=[provincias_desejadas])
            serializer = EscolaSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)
        

class UploadExcelView(APIView):
    parser_classes = [MultiPartParser]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='file', 
                in_=openapi.IN_FORM, 
                type=openapi.TYPE_FILE,
                description='Escolha um arquivo excel.'
            )
        ],
        responses={200: 'OK', 400: 'Bad Request', 500: 'Internal Server Error'},
        operation_description="Faz o upload de um arquivo Excel contendo dados das escolas para criar novos registros."
    )
    @action(detail=False, methods=['post'], parser_classes=(MultiPartParser, ), name='upload-excel', url_path='upload-excel')
    def post(self, request, format=None):
        if 'file' not in request.data:
            return Response({'error': 'Nenhum arquivo foi enviado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_obj = request.data['file']
            file_content = file_obj.read()

            # Validação do arquivo Excel
            if not file_content.startswith(b'\x50\x4b\x03\x04'):
                return Response({'error': 'Arquivo não é um arquivo Excel (.xlsx).'}, status=status.HTTP_400_BAD_REQUEST)

            # Leitura dos dados do Excel
            df = pd.read_excel(file_content)

            # Validação da estrutura do Excel
            if not set(df.columns) == {'nome', 'email', 'numero_salas', 'provincia'}:
                return Response({'error': 'Estrutura do Excel incorreta. Colunas esperadas: nome, email, numero_salas, provincia.'}, status=status.HTTP_400_BAD_REQUEST)

            # Contadores de inserção dos dados na base de dados
            escolas_inseridas = 0
            escolas_falhadas = 0
            erros = []

            for index, row in df.iterrows():
                try:
                    # Convertendo a string 'provincia' em uma lista de itens
                    # Estamos supondo que cada escola virá somente com uma provincia
                    # mas o modelo foi desenhado para uma escola estar em varias provincias
                    provincia = row['provincia'].split(',') if isinstance(row['provincia'], str) else row['provincia']
                    
                    data = {
                        'nome': row['nome'],
                        'email': row['email'],
                        'numero_salas': row['numero_salas'],
                        'provincia': provincia,
                    }
                    serializer = EscolaSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        escolas_inseridas += 1
                    else:
                        escolas_falhadas += 1
                        erros.append(f"Linha {index+1}: {serializer.errors}")
                except Exception as e:
                    escolas_falhadas += 1
                    erros.append(f"Linha {index+1}: {e}")

            # Resostas
            if erros:
                relatorio = f"**{escolas_inseridas} escolas inseridas com sucesso.**\n**{escolas_falhadas} escolas falharam:**\n{''.join(erros)}"
                return Response({'relatorio': relatorio}, status=status.HTTP_200_OK)
            else:
                relatorio = f"**{escolas_inseridas} escolas inseridas com sucesso.**"
                return Response({'relatorio': relatorio}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)