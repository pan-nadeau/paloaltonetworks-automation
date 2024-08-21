# django_project/jobs/views.py
import uuid

from django.shortcuts import redirect
from django_celery_results.models import TaskResult
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .tasks import run_automation_job

from .models import Job, Automation
from .forms import AutomationForm


class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "jobs/job_list.html"
    context_object_name = "jobs_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all jobs
        context["jobs_list"] = Job.objects.all()

        # Get active jobs
        context["active_jobs"] = Job.objects.filter(
            status__in=[
                "PENDING",
                "STARTED",
                "RETRY",
            ]
        )
        return context


class JobDetailView(
    LoginRequiredMixin,
    DetailView,
):
    model = Job
    template_name = "jobs/job_detail.html"
    context_object_name = "job"


class AutomationCreateView(LoginRequiredMixin, CreateView):
    model = Automation
    form_class = AutomationForm
    template_name = "automation/automation_form.html"

    def form_valid(self, form):
        automation = form.save(commit=False)
        job = Job.objects.create(status="PENDING")
        automation.job = job
        automation.save()
        form.save_m2m()  # This saves the many-to-many relationships

        run_automation_job.delay(automation.id)

        messages.success(self.request, f"Automation job initiated, job id: {job.id}")
        return redirect(reverse("jobs:job_detail", args=[job.id]))

    def get_success_url(self):
        return reverse("jobs:job_detail", args=[self.object.job.id])


class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = "jobs/job_confirm_delete.html"
    success_url = reverse_lazy("jobs:job_list")
