from django.db import models
from django.contrib.auth.models import User

# Admin model extending default User
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    privileges = models.TextField()

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'


# Election model
class Election(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_by = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='elections')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_date']


# Candidate model
class Candidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    position = models.CharField(max_length=255)
    manifesto = models.TextField()
    nomination_date = models.DateTimeField(auto_now_add=True)
    approval_status = models.BooleanField(default=False)
    image = models.ImageField(upload_to='candidate_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} for {self.position} ({self.election.title})"

    class Meta:
        unique_together = ('user', 'election', 'position')


# Ballot model
class Ballot(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='ballots')
    title = models.CharField(max_length=255)
    description = models.TextField()
    max_votes_allowed = models.PositiveIntegerField()
    display_order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} - {self.election.title}"

    class Meta:
        ordering = ['display_order']


# Vote model
class Vote(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} voted for {self.candidate.user.username} in {self.ballot.title}"

    class Meta:
        unique_together = ('ballot', 'user', 'candidate')
        ordering = ['-timestamp']


# Result model
class Result(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='results')
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, related_name='results')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='results')
    vote_count = models.PositiveIntegerField()
    percentage = models.FloatField(default=0.0)
    ranking = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.candidate.user.username} - {self.vote_count} votes in {self.ballot.title}"

    class Meta:
        unique_together = ('ballot', 'candidate')
        ordering = ['ranking']

    def calculate_percentage(self):
        """
        Calculate the percentage of total votes the candidate received in the ballot.
        """
        total_votes = Vote.objects.filter(ballot=self.ballot).count()
        self.percentage = (self.vote_count / total_votes) * 100 if total_votes > 0 else 0
        self.save()
        return self.percentage

    def update_ranking(self):
        """
        Update rankings of all candidates in the same ballot based on vote count.
        """
        results = Result.objects.filter(election=self.election, ballot=self.ballot).order_by('-vote_count')
        for index, result in enumerate(results):
            result.ranking = index + 1
            result.save()
