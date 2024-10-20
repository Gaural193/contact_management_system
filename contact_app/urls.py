from django.urls import path
from .views import *

urlpatterns = [
    path('', contact_list, name='contact_list'),
    path('create/', contact_create, name='contact_create'),
    path('edit/<int:contact_id>/', contact_edit, name='contact_edit'),
    path('delete/<int:contact_id>/', contact_delete, name='contact_delete'),
    path('import/', import_contacts, name='import_contacts'),
    path('export/', export_contacts, name='export_contacts'),
    path('merge_duplicates/', merge_duplicates, name='merge_duplicates'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    # path('search/', search_contacts, name='search_contacts')
     path('contacts/',contacts_list, name='contacts_list')
]
