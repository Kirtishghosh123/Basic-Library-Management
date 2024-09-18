
from django.contrib import admin
from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('register/', views.CreateUser.as_view(), name='register'),
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('updateuser/<int:pk>/', views.UpdateDelUser.as_view(), name='update-user'),
    path('users/', views.UpdateDelUser.as_view(), name='all-user'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('change-password/', views.ChangePassword.as_view(), name='change-password'),
    path('books/', views.ListCreateBooks.as_view(), name='list-create-books'),
    path('books/<int:id>/', views.UpdateDestroyBooks.as_view(), name='update-delete-books'),
    path('user/<int:user_id>/books/<int:book_id>/borrow/', views.BorrowBooks.as_view(), name='update-delete-books'),
    path('user/<int:user_id>/books/<int:book_id>/returned/', views.BookReturned.as_view(), name='update-delete-books'),
    path('borrow-history/<int:user_id>/', views.BorrowingUser.as_view(), name='borrow-history'),
    path('borrow-history/<int:user_id>/filter/', views.BorrowedBooksByGenre.as_view(), name='borrow-history-filter'),
    path('user/<int:user_id>/books/available-by-genre/', views.AvailableByGenre.as_view(), name='borrow-books-genre'),
    path('statistics/', views.BookStatistics.as_view(), name='borrow-stats'),
]
