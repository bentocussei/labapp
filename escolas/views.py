from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Escola
from .serializers import EscolaSerializer


class EscolaViewSet(viewsets.ModelViewSet):
    queryset = Escola.objects.all()
    serializer_class = EscolaSerializer

    def create(self, request):
        # Validar os dados antes de criar uma nova escola
        data = request.data
        serializer = EscolaSerializer(data=data)

        if serializer.is_valid():
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
