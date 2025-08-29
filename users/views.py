from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers.common import AuthSerializer
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken


class SignUpView(APIView):

    def post(self, request):
        serialized_user = AuthSerializer(data=request.data)
        serialized_user.is_valid(raise_exception=True)
        serialized_user.save()

        user = User.objects.get(pk=serialized_user.data["id"])
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token)}, 201)