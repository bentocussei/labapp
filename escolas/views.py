from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from .models import Escola
from .serializers import EscolaSerializer
import pandas as pd


class EscolaViewSet(viewsets.ModelViewSet):
    queryset = Escola.objects.all()
    serializer_class = EscolaSerializer

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


    def filter_queryset(self, request):
        request = self.request
        provincias_desejadas = request.GET.get('provincias')

        if provincias_desejadas:
            return self.queryset.filter(provincia__contains=[provincias_desejadas])
        else:
            return self.queryset
        

    def upload_excel(self, request):
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


