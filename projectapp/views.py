from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')

def blog_single(request):
    return render(request, 'blog-single.html')

def contact(request):
    return render(request, 'contact.html')

def main(request):
    return render(request, 'main.html')

def restaurants(request):
    return render(request, 'restaurant.html')

def rooms(request):
    return render(request, 'rooms.html')

def rooms_single(request):
    return render(request, 'rooms-single.html')
