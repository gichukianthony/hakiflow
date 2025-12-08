from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Case, OfficerNote, NotificationSubscription, AnonymousReport, CitizenProfile
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import csv
from django.contrib.auth.decorators import login_required

# Public Views

def home_view(request):
    query = request.GET.get('q')
    if query:
        case = Case.objects.filter(ob_number=query).first()
        if case:
            # Auto-subscribe authenticated users with an email
            if request.user.is_authenticated and request.user.email:
                NotificationSubscription.objects.get_or_create(case=case, email=request.user.email)
            return redirect('case_detail', pk=case.pk)
        else:
            messages.error(request, 'Case not found with that OB Number.')
    return render(request, 'cases/home.html')

def case_detail_view(request, pk):
    case = get_object_or_404(Case, pk=pk)
    return render(request, 'cases/case_detail.html', {'case': case})

def report_view(request):
    if request.method == 'POST':
        details = request.POST.get('details')
        if details:
            AnonymousReport.objects.create(details=details)
            messages.success(request, 'Report submitted successfully.')
            return redirect('home')
    return render(request, 'cases/report.html')

def subscribe_view(request):
    if request.method == 'POST':
        ob_number = request.POST.get('ob_number')
        email = request.POST.get('email')
        case = Case.objects.filter(ob_number=ob_number).first()
        if case and email:
            NotificationSubscription.objects.create(case=case, email=email)
            messages.success(request, 'Subscribed to updates successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid OB Number or Email.')
    return render(request, 'cases/subscribe.html')

class SignUpView(CreateView):
    class SignUpForm(UserCreationForm):
        id_number = forms.CharField(max_length=50, required=True, help_text="Enter your ID number to link your cases.")

        class Meta(UserCreationForm.Meta):
            model = User
            fields = ("username", "id_number")

    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        id_number = form.cleaned_data.get('id_number')
        if id_number:
            CitizenProfile.objects.get_or_create(user=self.object, defaults={'id_number': id_number})
        messages.success(self.request, 'Account created successfully. Please login.')
        return response

class UserDashboardView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'cases/user_dashboard.html'
    context_object_name = 'cases'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        # Handle OB number form POST
        if request.method == 'POST':
            ob_number = request.POST.get('ob_number')
            if ob_number:
                case = Case.objects.filter(ob_number=ob_number).first()
                if case:
                    # Auto-subscribe authenticated users with email
                    if request.user.is_authenticated and request.user.email:
                        NotificationSubscription.objects.get_or_create(case=case, email=request.user.email)
                    elif request.user.is_authenticated and not request.user.email:
                        messages.warning(request, 'Add an email to receive notifications for this case.')
                    return redirect('case_detail', pk=case.pk)
                else:
                    messages.error(request, 'No case found with that OB Number.')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        cases = Case.objects.none()
        email = self.request.user.email
        if email:
            subscribed_cases = NotificationSubscription.objects.filter(email=email).values_list('case', flat=True)
            cases = Case.objects.filter(pk__in=subscribed_cases)
        # Add cases linked by ID number through the citizen profile
        profile = getattr(self.request.user, 'citizen_profile', None)
        if profile:
            id_cases = Case.objects.filter(id_number=profile.id_number)
            cases = cases.union(id_cases)
        return cases

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['case_counts'] = {
            'total': qs.count(),
            'investigation': qs.filter(status='investigation').count(),
            'dci': qs.filter(status='dci').count(),
            'court': qs.filter(status='court').count(),
            'judgement': qs.filter(status='judgement').count()
        }
        # Recent notes for user's cases (activity feed)
        context['recent_notes'] = OfficerNote.objects.filter(case__in=qs).order_by('-created_at')[:10]
        # Upcoming court dates
        context['upcoming_court_dates'] = qs.filter(court_date__isnull=False).order_by('court_date')[:5]
        return context


@login_required
def export_user_cases_csv(request):
    """
    Export the current user's tracked cases as CSV.
    """
    qs = Case.objects.none()
    if request.user.email:
        subscribed_cases = NotificationSubscription.objects.filter(email=request.user.email).values_list('case', flat=True)
        qs = Case.objects.filter(pk__in=subscribed_cases)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=\"my_cases.csv\"'

    writer = csv.writer(response)
    writer.writerow(['OB Number', 'Title', 'Status', 'Court Date', 'Created At'])
    for c in qs:
        writer.writerow([
            c.ob_number,
            c.title,
            c.get_status_display(),
            c.court_date.isoformat() if c.court_date else '',
            c.created_at.isoformat()
        ])
    return response

# Officer/Admin Views

class CaseListView(ListView):
    model = Case
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Case.objects.all()
        context['case_counts'] = {
            'total': qs.count(),
            'investigation': qs.filter(status='investigation').count(),
            'dci': qs.filter(status='dci').count(),
            'court': qs.filter(status='court').count(),
            'judgement': qs.filter(status='judgement').count()
        }
        return context

class CaseCreateView(CreateView):
    model = Case
    fields = ['ob_number', 'title', 'description', 'status', 'court_date', 'id_number']
    template_name = 'cases/case_form.html'
    success_url = reverse_lazy('case_list')

    def form_valid(self, form):
        messages.success(self.request, 'Case created successfully.')
        return super().form_valid(form)

class CaseUpdateView(UpdateView):
    model = Case
    fields = ['title', 'description', 'status', 'court_date']
    template_name = 'cases/case_form.html'
    success_url = reverse_lazy('case_list')

    def form_valid(self, form):
        messages.success(self.request, 'Case updated successfully.')
        return super().form_valid(form)

class OfficerNoteCreateView(CreateView):
    model = OfficerNote
    fields = ['note']
    template_name = 'cases/note_form.html'
    
    def form_valid(self, form):
        case = get_object_or_404(Case, pk=self.kwargs['pk'])
        form.instance.case = case
        messages.success(self.request, 'Note added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('case_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = get_object_or_404(Case, pk=self.kwargs['pk'])
        return context

@method_decorator(login_required, name='dispatch')
class NotificationManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'cases/notification_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriptions'] = NotificationSubscription.objects.filter(email=self.request.user.email)
        return context

    def post(self, request, *args, **kwargs):
        # Unsubscribe logic: expect 'subscription_id' in POST
        subscription_id = request.POST.get('subscription_id')
        subscription = NotificationSubscription.objects.filter(id=subscription_id, email=request.user.email).first()
        if subscription:
            subscription.delete()
            messages.success(request, 'Unsubscribed successfully.')
        else:
            messages.error(request, 'Could not unsubscribe. Please try again.')
        return self.get(request, *args, **kwargs)
