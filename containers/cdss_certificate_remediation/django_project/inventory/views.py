# django_project/inventory/views.py
from django.shortcuts import redirect
from django_celery_results.models import TaskResult
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .tasks import run_inventory_script

from .models import Inventory
from .forms import InventoryForm


class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = "inventory/inventory_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for item in context["object_list"]:
            item.connection_address = item.get_connection_address()

        # Get active tasks
        active_tasks = TaskResult.objects.filter(
            status__in=["PENDING", "STARTED", "RETRY"]
        )
        context["active_tasks"] = active_tasks
        return context


class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = Inventory
    template_name = "inventory/inventory_detail.html"


class InventoryCreateView(LoginRequiredMixin, CreateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "inventory/inventory_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        task = run_inventory_script.delay(self.object.id)
        messages.success(
            self.request, f"Inventory creation task started. Task ID: {task.id}"
        )
        return redirect(reverse("inventory:list") + f"?task_id={task.id}")

    def get_success_url(self):
        return reverse("inventory:list")


class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "inventory/inventory_form.html"
    success_url = reverse_lazy("inventory:list")


class InventoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Inventory
    template_name = "inventory/inventory_confirm_delete.html"
    success_url = reverse_lazy("inventory:list")