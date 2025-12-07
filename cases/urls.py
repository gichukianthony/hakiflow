from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.home_view, name='home'),
    path('case/<int:pk>/', views.case_detail_view, name='case_detail'),
    path('report/', views.report_view, name='report'),
    path('subscribe/', views.subscribe_view, name='subscribe'),

    # Officer/Admin URLs
    path('cases/', views.CaseListView.as_view(), name='case_list'),
    path('cases/add/', views.CaseCreateView.as_view(), name='case_add'),
    path('cases/<int:pk>/edit/', views.CaseUpdateView.as_view(), name='case_edit'),
    path('cases/<int:pk>/add-note/', views.OfficerNoteCreateView.as_view(), name='add_note'),
]
