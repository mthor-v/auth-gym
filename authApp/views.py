from rest_framework.mixins import UpdateModelMixin
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from django.conf import settings
from authApp.serializers import MyTokenObtainPairSerializer, UserSerializer
from authApp.models import User


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserCreateView(views.APIView):

    def post(self, request, *args, **kwargs):

        role = request.data.get('role')
        if role == "AD":
            code = int(request.query_params.get('code'))
            if code in settings.ADMI_CODES:
                serializer  = UserSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                tokenData   = {"email": request.data["email"],
                            "password": request.data["password"]}
                tokenSerializer = MyTokenObtainPairSerializer(data=tokenData)
                tokenSerializer.is_valid(raise_exception=True)
                return Response(tokenSerializer.validated_data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message":"No tiene permisos para crear cuenta de Administrador"}, status=status.HTTP_401_BAD_REQUEST)
        elif role == "CL":
            serializer  = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            tokenData   = {"email": request.data["email"],
                        "password": request.data["password"]}
            tokenSerializer = MyTokenObtainPairSerializer(data=tokenData)
            tokenSerializer.is_valid(raise_exception=True)
            return Response(tokenSerializer.validated_data, status=status.HTTP_201_CREATED)
class UserAccountView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        token           = request.META.get('HTTP_AUTHORIZATION')[7:]
        tokenBackend    = TokenBackend(algorithm=settings.SIMPLE_JWT['ALGORITHM'])
        valid_data      = tokenBackend.decode(token, verify=False)

        if valid_data['user_id'] != kwargs['pk']:
            stringResponse = {'detail': 'Unauthorized Request'}
            return Response(stringResponse, status=status.HTTP_401_UNAUTHORIZED)

        return super().get(request, *args, **kwargs)

class UserGeneralView(views.APIView):

    permission_classes = (IsAuthenticated,)    

    def get(self, request, *args, **kwargs):

        serializer = UserSerializer()
        q_data = request.query_params.get('dni')
        if q_data:
            try:
                instance = User(dni= q_data)
                result = serializer.customer_data(instance)

                return Response(result, status=status.HTTP_200_OK)
            except Exception:
                return Response({'message':'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':'Ingrese un dni valido'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):

        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        tokenBackend = TokenBackend(algorithm=settings.SIMPLE_JWT['ALGORITHM'])
        valid_data = tokenBackend.decode(token,verify=False)

        instance = User(id = valid_data["user_id"])

        serializer = UserSerializer(instance, data=request.data)        
        serializer.is_valid(raise_exception=True)        
        serializer.save()
        result = {'message': 'Usuario actualizado con exito.'}

        return Response(result, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        
        token = request.META.get('HTTP_AUTHORIZATION')[7:]
        tokenBackend = TokenBackend(algorithm=settings.SIMPLE_JWT['ALGORITHM'])
        valid_data = tokenBackend.decode(token,verify=False)

        if valid_data['user_id'] != kwargs['pk']:
            stringResponse = {'detail':'Unauthorized Request'}
            return Response(stringResponse, status=status.HTTP_401_UNAUTHORIZED)

        instance = User.objects.get(id= kwargs['pk'])
        instance.delete()
        result = {"message":"Usuario eliminado correctamente"}
        return Response(result, status=status.HTTP_200_OK)

class StatusManagerView(generics.GenericAPIView, UpdateModelMixin):#
    queryset = User.objects.filter(role='CL')
    serializer_class = UserSerializer
    lookup_field = 'dni'
    
    def put(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)
        return Response({"message":"Cambio efectuado"}, status=status.HTTP_200_OK)

class TestView(views.APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        data = UserSerializer(request.user).data
        del data['password']
        return Response(data)

class RetrieveAllUsers(views.APIView):
    queryset = User.objects.filter(role='CL')

    def get(self, rquest, *args, **kwargs):
        serializer = UserSerializer()
        users= []
        for i in self.queryset.all():
            users.append(serializer.customer_data(i))
        
        return Response({'usuarios':users}, status=status.HTTP_200_OK)