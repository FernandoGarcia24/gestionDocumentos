from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Document
from .forms import DocumentForm
from django.conf import settings
from .models import Document
from .forms import DocumentForm
from django import template
register = template.Library()



def signup(request):

    if request.method == 'GET':
        form = CustomUserCreationForm()
        return render(request, 'signup.html', {'form': form})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], 
                email=request.POST['email'], password=request.POST['password1'])
                user.save() 
                return redirect('/signin')
            except IntegrityError:
                return render(request, 'signin.html', {
                            'form': CustomUserCreationForm,        
                            'error': 'El usuario ya existe'
                            })       
        form = CustomUserCreationForm()  
        form.add_error('password2', 'Las contraseñas no coinciden')
        return render(request, 'signup.html', 
                        {'form': form})    
  
  
def sistemaGestion(request):
    return render(request, 'sistemagestion.html')

def signout(request):
    logout(request)
    return redirect('signin')

class CustomUserCreationForm(UserCreationForm):
     
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    
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
            email = form.cleaned_data.get('username')  # Obtén el correo electrónico del formulario
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('document_list')  # Redirige a la página deseada después de iniciar sesión
            else:
                return render(request, 'signin.html', {
                    'form': form,
                    'error': 'Correo electrónico o contraseña incorrectos'
                })
        else:
            return render(request, 'signin.html', {
                'form': form,
                'error': 'Correo electrónico o contraseña incorrectos'
            })
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
        if form.is_valid():
            document = form.save(commit=False)
            document.approver = form.cleaned_data['approver']
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document)

    return render(request, 'assign_approver.html', {'form': form, 'document': document})

@login_required
def approve_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        approval_status = request.POST.get('approval_status')
        print(approval_status)
        if approval_status == 'approve':
            document.approved = True
            document.rejected = False
            document.approval_message = 'Documento aprobado exitosamente.'
        elif approval_status == 'reject':
            document.approved = False
            document.rejected = True
            print(document.rejected)
            print(document)
            document.approval_message = 'Documento rechazado.'
        document.save()
        
    if request.user.is_superuser:
        return redirect('document_list')  # Redireccionar a la lista general de documentos pendientes
    else:
        return redirect('document_list')

@login_required
def document_list(request):
    
    documents = Document.objects.filter(uploaded_by=request.user)
    print("Documentos a usuario:", documents)
     
    documentsAssigned = Document.objects.filter(approver=request.user)
    print("Documentos a revisar:", documentsAssigned)
    
    context = {
        'documentsAssigned': documentsAssigned,
        'documents': documents,
    }

    return render(request, 'document_list.html', context)

@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.approver = form.cleaned_data['approver']
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'document_upload.html', {'form': form})

@login_required
def documents_for_approver(request, approver_id):
    approver = get_object_or_404(User, pk=approver_id)
    documents = Document.objects.filter(approver=approver, approved=False, rejected=False)
    return render(request, 'documents_for_approver.html', {'documents': documents, 'approver': approver})

@login_required
def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    if document.uploaded_by != request.user:
        messages.error(request, "No tienes permiso para editar este documento.")
        return redirect('document_list')
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento actualizado correctamente.")
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document)
    return render(request, 'document_edit.html', {'form': form})

@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.user != document.uploaded_by:
        messages.error(request, "No tienes permiso para eliminar este documento.")
        return redirect('document_list')
    if request.method == 'POST':
        document.delete()
        messages.success(request, "Documento eliminado correctamente.")
        return redirect('document_list')
    return render(request, 'document_delete.html', {'document': document})

