from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponseRedirect, render, redirect, resolve_url
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from project.models import *
from project.product.forms import *
from project.custom.views import *
from django.contrib.auth.models import Group
from project.product.filters import *
from project.other.forms import ImageCreateForm 

# Create your views here.


class ProductCreateView(AuthenticateCreateView):
    model = Product
    template_name = "product/create.html"
    form_class = ProductCreateForm
    success_url = reverse_lazy('store:store_index') 
    permission = 'project.add_product'

    def update_extra_context(self,extra):
        if self.extra_context is None:
            self.extra_context = extra
        else:
            self.extra_context.update(extra)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].fields['Images'].queryset = Image.objects.filter(Owner__id=self.request.user.id)
        context['image_form'] = ImageCreateForm()
        return context
    
    @auth
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = None
        form = self.get_form()
        try:
            store = Store.objects.get(id=kwargs['store_id'])
            if store.Owner.id == request.user.id:
                form.instance.Store = store
                self.success_url = reverse_lazy('store:store_product_list',kwargs={'store_id':store.id})
            else:
                extra = {'error':'User not authorized to create a product in this store, must be its owner'}
                self.update_extra_context(extra)
                return self.form_invalid(form)
        except ObjectDoesNotExist:
            extra = {'error':'Store doesnt exist'}
            self.update_extra_context(extra)
            return self.form_invalid(form)
        
        if form.is_valid():
            image_form = ImageCreateForm(request.POST, request.FILES)
            product = form.save()
            if image_form.is_valid():
                image_form.instance.Owner_id = request.user.id
                image = image_form.save()
                product.Images.add(image)
            product.save()
            return redirect(resolve_url('store:store_view',pk=kwargs['store_id']),permanent=True)
            # return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def other_condition(self, request,*args, **kwargs):
        if 'store_id' in kwargs:
            user = request.user
            store = Store.objects.get(id=kwargs['store_id'])
            return store.Owner.id == user.id
        else:
            return True

class ProductListView(FilterOrderAuthenticateListView):
    model = Product
    template_name='product/list.html'
    permission = 'project.view_product'
    form_order = ProductOrderForm
    form_filter = ProductFilter
    
    def get_context_data(self,object_list=None,**kwargs):
        context = super().get_context_data(object_list,**kwargs)
        try:
            context['store_id'] = kwargs['store_id']
            context['store'] = Store.objects.get(id=kwargs['store_id'])
        except:
            pass
        return context
    
    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            try:
                queryset = self.model.objects.filter(Store__id=self.kwargs['store_id'])
            except KeyError:
                queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset
    
class ProductDetailView(AuthenticateDetailView):
    model = Product
    template_name = "product/view.html"
    permission = 'project.view_product'

class ProductDeleteView(AuthenticateDeleteView):
    model = Product
    template_name = "delete.html"
    success_url = reverse_lazy('project:success')
    permission = 'project.delete_product'
    
    def other_condition(self, request,*args, **kwargs):
        user = request.user
        product = Product.objects.get(id=kwargs['pk'])
        return product.Store.Owner.id == user.id

class ProductUpdateView(AuthenticateUpdateView):
    model = Product
    form_class = ProductCreateForm
    template_name = "update.html"
    success_url = reverse_lazy('project:success')
    permission = 'project.change_product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].fields['Images'].queryset = Image.objects.filter(Owner__id=self.request.user.id)
        # context['form'].fields['success_url'].initial = self.request.META.get('HTTP_REFERER')
        return context
    
    def other_condition(self, request,*args, **kwargs):
        user = request.user
        product = Product.objects.get(id=kwargs['pk'])
        return product.Store.Owner.id == user.id

