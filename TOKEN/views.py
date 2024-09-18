from django.db.models import Count, DurationField, F, ExpressionWrapper
from django.db.models.fields import return_None
from django.shortcuts import render
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework import status
from urllib3 import request
from . import models, serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.response import Response

from .models import Borrow
from .serializers import UserSerializer
from django.utils import timezone

# Create your views here.

class CreateUser(APIView):
    def post(self, request):
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDelUser(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class AdminOnlyAcccess(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class =UserSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
        except:
            return Response({"msg": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)
        token.delete()
        return Response(status=status.HTTP_200_OK)


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        user = User.objects.get(id=id)
        serializer = serializers.UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"Password changed"}, status=status.HTTP_200_OK)

class ListCreateBooks(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = models.Book.objects.all()
    serializer_class = serializers.BookSerializer

class UpdateDestroyBooks(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = models.Book.objects.all()
    serializer_class = serializers.BookSerializer


class BorrowBooks(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id, book_id):
        if request.auth == Token.objects.get(user_id=user_id):
            user = User.objects.get(id=user_id)
            books = models.Book.objects.get(id = book_id)
            copies_requested = int(request.data.get('copies', 1))
            if books.available_copies >= copies_requested:
                books.available_copies -= copies_requested
                books.save()
                borrow = models.Borrow.objects.create(user=user,book = books,borrow_date = timezone.now().date(),is_returned=False, copies_requested = copies_requested)
                return Response({"msg":"Book "+str(books.id)+" "+"has been borrowed succesfully"}, status=status.HTTP_200_OK)
            elif copies_requested > books.available_copies:
                return Response({"message":"Copies not avaliable"}, status=status.HTTP_200_OK)
            elif User.DoesNotExist:
                return Response({"message":"User doesnot exist"}, status=status.HTTP_400_BAD_REQUEST)
            elif models.Book.DoesNotExist:
                return Response({"message": "User doesnot exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message":"See logs for errors"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Wrong Token"}, status=status.HTTP_403_FORBIDDEN)

class BookReturned(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, user_id, book_id):
        if request.auth == Token.objects.get(user_id=user_id):
            try:
                user = User.objects.get(id=user_id)
                books = models.Book.objects.get(id=book_id)
                copies_returned = int(request.data.get('copies', 1))

                books.available_copies += copies_returned
                books.save()
                borrow = models.Borrow.objects.create(user=user, book=books,return_date=timezone.now().date(),copies_requested=0,
                                                          is_returned=True,copies_returned=copies_returned)
                return Response({"msg": "Book " + str(books.id) + " " + "has been returned succesfully"},
                                    status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_200_OK)

        else:
            return Response({"message": "Wrong Token"}, status=status.HTTP_403_FORBIDDEN)

class BorrowingUser(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        if request.auth == Token.objects.get(user = User.objects.get(id=user_id)):
            borrow_history = models.Borrow.objects.filter(user__id = user_id)
            serializer = serializers.BorrowSerializer(borrow_history, many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        elif User.DoesNotExist:
            return Response( {"message":"Token creds wrong"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class BorrowedBooksByGenre(APIView):
    permission_classes = [IsAuthenticated]

    def get(selfself, request, user_id):
        query_params_genre = request.query_params.get('genre','')
        query_params_author = request.query_params.get('author', '')
        query_params_start_date = request.query_params.get('start_date', '')
        query_params_end_date = request.query_params.get('end_date', '')
        try:
            borrow = models.Borrow.objects.filter(user__id = user_id)
        except Exception as e:
            return Response({"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if request.auth == Token.objects.get(user = User.objects.get(id=user_id)):
            if query_params_genre:
                borrow = Borrow.objects.filter(book__genre__icontains=query_params_genre)
            if query_params_author:
                borrow = borrow.objects.filter(book__author__icontains=query_params_author)
            if query_params_start_date:
                date = parse_date(query_params_start_date)
                if date:
                    borrow = borrow.objects.filter(borrow_date__gte=date)
            if query_params_end_date:
                enddate = parse_date(query_params_end_date)
                if enddate:
                    borrow = borrow.objects.filter(return_date__gte=enddate)

            serializer = serializers.BorrowSerializer(borrow, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "Token creds wrong"}, status=status.HTTP_400_BAD_REQUEST)

class AvailableByGenre(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        if request.auth == Token.objects.get(user=User.objects.get(id=user_id)):
            query_genre = request.query_params.get('genre')
            if query_genre:
                books = models.Book.objects.filter(genre__iexact = query_genre, available_copies__gte = 1)
                if books.exists():
                    serializer = serializers.BookSerializer(books, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({"message":"No books available of this genre"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message":"please provide a genre"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Check credentials"}, status=status.HTTP_403_FORBIDDEN)

class BookStatistics(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request):
        if request.auth == Token.objects.get(user=User.objects.get(id=1)):
                query_params_start_date = request.query_params.get('start_date')
                query_params_start_date = parse_date(query_params_start_date)
                query_params_end_date = request.query_params.get('end_date')
                query_params_end_date = parse_date(query_params_end_date)
                if query_params_end_date and query_params_start_date:
                    total_borrowed_books = models.Borrow.objects.filter(borrow_date__range=[query_params_start_date,query_params_end_date])
                    most_borrowed_books = models.Borrow.objects.filter(borrow_date__range=[query_params_start_date,query_params_end_date]).values('book__title','book__author__name').annotate(books_count=Count('id')).order_by('-books_count')[:10]
                    most_active_borrowers = models.Borrow.objects.filter(borrow_date__range=[query_params_start_date,query_params_end_date]).values('user__username').annotate(books_count=Count('book__id')).order_by('-books_count')[:10]
                    avg_borrow_duration = models.Borrow.objects.filter(borrow_date__range=[query_params_start_date,query_params_end_date]).filter(return_date__isnull = False).annotate(duration=ExpressionWrapper(F('return_date')-F('borrow_date'), output_field=DurationField()))

                    serializer = serializers.BorrowSerializer(total_borrowed_books, many=True)
                    serializer1 = serializers.BorrowSerializer(most_borrowed_books, many=True)
                    serializer2 = serializers.BorrowSerializer(most_active_borrowers, many=True)
                    serializer3 = serializers.BorrowSerializer(avg_borrow_duration, many=True)

                    return Response({
                        "total_borrowd_books" : serializer.data,
                        "most_borrowd_books" : serializer1.data,
                        "most_active_borrowers": serializer2.data,
                        "avg_borrow_duration": serializer3.data
                    }, status=status.HTTP_200_OK )
                else:
                    return Response({"message":"Check logical errors"}, status=status.HTTP_400_BAD_REQUEST)