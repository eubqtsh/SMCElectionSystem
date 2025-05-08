from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Election, Ballot, Candidate, Vote, Result
from django.shortcuts import get_object_or_404

# Home page that lists all elections (dashboard)
def home(request):
    elections = Election.objects.all()
    context = {'elections': elections}

    # Determine action (login or register)
    action = request.GET.get('action', 'login')
    context['action'] = action

    if request.method == 'POST':
        if action == 'login':  # Handle login
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('dashboard')
            else:
                context['form'] = form

        elif action == 'register':  # Handle registration
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)  # Log in the user after registration
                messages.success(request, 'Registration successful!')
                return redirect('dashboard')
            else:
                context['form'] = form

    else:
        # Display the login or register form based on action
        if action == 'login':
            context['form'] = AuthenticationForm()
        elif action == 'register':
            context['form'] = UserRegistrationForm()

    return render(request, 'election/dashboard.html', context)


# Custom login view (rendered on the dashboard page)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'election/dashboard.html', {'form': form, 'action': 'login'})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('/?action=login')  # Redirect to home with login form
    else:
        form = UserRegistrationForm()

    return render(request, 'election/dashboard.html', {'form': form, 'action': 'register'})


# View to display the details of a specific election
def election_detail(request, election_id):
    election = Election.objects.get(id=election_id)
    context = {
        'election': election,
    }
    return render(request, 'election/election_detail.html', context)

@login_required
def vote(request, ballot_id):
    ballot = get_object_or_404(Ballot, id=ballot_id)
    election = ballot.election
    candidates = Candidate.objects.filter(election=election)

    return render(request, 'vote.html', {
        'ballot': ballot,
        'candidates': candidates
    })

def result(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    results = Result.objects.filter(election=election).select_related('ballot', 'candidate').order_by('ranking')
    return render(request, 'result.html', {'election': election, 'results': results})

@login_required
def dashboard(request):
    # You can customize the context with more data specific to logged-in users
    elections = Election.objects.all()  # Show elections or user-related data
    return render(request, 'election/dashboard.html', {'elections': elections})

def custom_logout_view(request):
    logout(request)
    return redirect('/accounts/login/')

def election_list(request):
    elections = Election.objects.all()
    return render(request, 'election/election_list.html', {'elections': elections})

def candidate_list(request):
    candidates = Candidate.objects.all()
    return render(request, 'election/candidate_list.html', {'candidates': candidates})

def ballot_detail(request, ballot_id):
    # Fetch the ballot details using the ballot_id
    ballot = get_object_or_404(Ballot, pk=ballot_id)
    
    return render(request, 'ballot_detail.html', {'ballot': ballot})

def ballot_list(request):
    ballots = Ballot.objects.all()
    candidates = Candidate.objects.filter(approval_status=True)  # optional filtering
    return render(request, 'ballot_list.html', {'ballots': ballots, 'candidates': candidates})



def vote_list(request):
    ongoing_elections = Election.objects.filter(status='ongoing').prefetch_related('ballots')
    return render(request, 'vote_list.html', {'elections': ongoing_elections})

@login_required
def vote_submit(request):
    if request.method == "POST":
        ballot_id = request.POST.get("ballot_id")
        candidate_id = request.POST.get("candidate_id")

        ballot = Ballot.objects.get(id=ballot_id)
        candidate = Candidate.objects.get(id=candidate_id)

        # Optional: check if user already voted
        if Vote.objects.filter(user=request.user, ballot=ballot).exists():
            return redirect('ballot_list')  # or show a warning

        Vote.objects.create(
            ballot=ballot,
            candidate=candidate,
            user=request.user
        )

        return redirect('ballot_list')

def result(request, election_id=None):
    if not election_id:
        # If no election_id is provided, redirect to the first election's result page
        first_election = Election.objects.first()
        if first_election:
            return redirect('result', election_id=first_election.id)
        else:
            # Handle the case where there are no elections (e.g., return a 404 or some message)
            return render(request, 'election/no_elections.html')

    # If election_id is provided, display the results for that election
    election = Election.objects.get(id=election_id)
    return render(request, 'election/result.html', {'election': election})

# View to show results for a specific election
def result_view(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    results = Result.objects.filter(election=election).order_by('ballot', 'ranking')
    context = {
        'election': election,
        'results': results,
    }
    return render(request, 'election/result.html', context)

# View to list all elections with available results
def result_list_view(request):
    elections = Election.objects.all()
    results = []

    for election in elections:
        candidates = Candidate.objects.filter(election=election)
        total_votes = Vote.objects.filter(candidate__in=candidates).count()

        candidate_data = []
        max_votes = 0

        for candidate in candidates:
            votes = Vote.objects.filter(candidate=candidate).count()
            percentage = round((votes / total_votes * 100), 2) if total_votes > 0 else 0
            candidate_data.append({
                'candidate': candidate,
                'votes': votes,
                'percentage': percentage,
            })
            max_votes = max(max_votes, votes)

        # Mark winner(s)
        for c in candidate_data:
            c['is_winner'] = c['votes'] == max_votes and max_votes > 0

        results.append({
            'election': election,
            'candidates': candidate_data,
            'total_votes': total_votes,
        })

    return render(request, 'election/result_list.html', {'results': results})