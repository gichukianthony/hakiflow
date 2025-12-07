from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Case, OfficerNote, NotificationSubscription, AnonymousReport

# Public Views

def home_view(request):
    query = request.GET.get('q')
    if query:
        case = Case.objects.filter(ob_number=query).first()
        if case:
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

# Officer/Admin Views

class CaseListView(ListView):
    model = Case
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    ordering = ['-created_at']

class CaseCreateView(CreateView):
    model = Case
    fields = ['ob_number', 'title', 'description', 'status', 'court_date']
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
