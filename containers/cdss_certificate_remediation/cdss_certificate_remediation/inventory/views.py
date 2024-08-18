# cdss_certificate_remediation/inventory/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from .models import Inventory
from .forms import InventoryForm


class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = "inventory/inventory_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for item in context["object_list"]:
            item.connection_address = item.get_connection_address()
        return context


class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = Inventory
    template_name = "inventory/inventory_detail.html"


class InventoryCreateView(LoginRequiredMixin, CreateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "inventory/inventory_form.html"
    success_url = reverse_lazy("inventory:list")


class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "inventory/inventory_form.html"
    success_url = reverse_lazy("inventory:list")


class InventoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Inventory
    template_name = "inventory/inventory_confirm_delete.html"
    success_url = reverse_lazy("inventory:list")
