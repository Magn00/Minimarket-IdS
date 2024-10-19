from django.shortcuts import render

# Create your views here.

def vendedor(request):
    return render(request, 'vendedor.html')