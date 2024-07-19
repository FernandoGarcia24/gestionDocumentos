from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Document
from .backends import EmailBackend
from django.core.exceptions import ValidationError
from django.conf import settings
from .forms import DocumentForm
from django import template
register = template.Library()




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya existe. Por favor, elige otro.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("El correo electrónico ya está registrado. Por favor, elige otro.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
    
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                backend = EmailBackend()
                authenticated_user = backend.authenticate(request, username=user.email, password=form.cleaned_data['password1'])
                if authenticated_user is not None:
                    return redirect('signin')
                else:
                    return render(request, 'signup.html', {'form': form, 'error_message': 'No se pudo autenticar al usuario.'})
            except IntegrityError:
                form.add_error(None, 'El usuario ya existe')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})   
  
def sistemaGestion(request):
    return render(request, 'sistemagestion.html')

def signout(request):
    logout(request)
    return redirect('signin')
    
@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})
    
def home(request):
    form = CustomUserCreationForm()
    return render(request, 'home.html', {'form': form})    

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('document_list')
            else:
                messages.error(request, "Correo electronico o contraseña incorrecta.")
        else:
            messages.error(request, "Correo electronico o contraseña incorrecta.")
    else:
        form = AuthenticationForm()

    return render(request, 'signin.html', {'form': form})

def document_preview(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return render(request, 'document_preview.html', {'document': document})
        
@login_required
def assign_approver(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        print("form: ", form)
        if form.is_valid():
            document = form.save(commit=False)
            document.approver = form.cleaned_data['approver']
            print("document.approver: ", document.approver)
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document)

    return render(request, 'document_list.html', {'form': form, 'document': document})

@login_required
def approve_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        approval_status = request.POST.get('approval_status')
        print(approval_status)
        if approval_status == 'approve':
            document.approved = True
            document.rejected = False
            messages.success(request, "Documento aprobado exitosamente.")
        elif approval_status == 'reject':
            document.approved = False
            document.rejected = True
            messages.error(request, "Documento rechazado.")
        document.save()
        
    if request.user.is_superuser:
        return redirect('document_list')
    else:
        return redirect('document_list')

@login_required
def document_list(request):
    
    documents = Document.objects.filter(uploaded_by=request.user)
    documentsAssigned = Document.objects.filter(approver=request.user)
    
    documentsAssigned = Document.objects.filter(
        approver=request.user,
        approved__isnull=True,
        rejected__isnull=True 
    )
    
    context = {
        'documentsAssigned': documentsAssigned,
        'documents': documents,
    }
    return render(request, 'document_list.html', context)

@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.approver = form.cleaned_data['approver']
            document.save()
            messages.success(request, "Documento subido exitosamente.")
            return redirect('document_list')
    else:
        form = DocumentForm(user=request.user)
    return render(request, 'document_upload.html', {'form': form})

@login_required
def documents_for_approver(request, approver_id):
    approver = get_object_or_404(User, pk=approver_id)
    print("approver", approver)
    documents = Document.objects.filter(approver=approver, approved=False, rejected=False)
    return render(request, 'document_list.html', {'documents': documents, 'approver': approver})

@login_required
def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento actualizado correctamente.")
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document, user=request.user)
    return render(request, 'document_edit.html', {'form': form})

@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if request.method == 'POST':
        document.delete()
        messages.success(request, "Documento eliminado correctamente.")
        return redirect('document_list')
    return render(request, 'document_delete.html', {'document': document})

