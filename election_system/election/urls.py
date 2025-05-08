from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Election detail
    path('election/<int:election_id>/', views.election_detail, name='election_detail'),

    # Voting
    path('vote/<int:ballot_id>/', views.vote, name='vote'),

    # Election results (by election ID)
    path('result/<int:election_id>/', views.result_view, name='result'),

    # Optional: general result page (list or redirect)
    path('result/', views.result_list_view, name='result_list'),

    # Auth views
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/logout/', views.custom_logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Lists
    path('election/', views.election_list, name='election_list'),
    path('candidate/', views.candidate_list, name='candidate_list'),
    path('ballot/', views.ballot_list, name='ballot_list'),

    # Ballot detail
    path('ballot/<int:ballot_id>/', views.ballot_detail, name='ballot_detail'),

    # Vote views
    path('vote/', views.vote_list, name='vote_list'),
    path('vote/submit/', views.vote_submit, name='vote_submit'),
]
