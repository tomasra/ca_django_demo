from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from .models import Book, BookInstance, Author, BookReview
from .forms import RegistrationForm, UserUpdateForm, ProfilisUpdateForm, BookReviewForm, UserBookCreateForm


def index(request):
    # Suskaičiuokime keletą pagrindinių objektų
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Laisvos knygos (tos, kurios turi statusą 'g')
    num_instances_available = BookInstance.objects.filter(status__exact='g').count()
    
    # Kiek yra autorių    
    num_authors = Author.objects.count()
    
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    # perduodame informaciją į šabloną žodyno pavidale:
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # renderiname index.html, su duomenimis kintamąjame context
    return render(request, 'library/index.html', context=context)


# def books(request):
#     all_books = Book.objects.all()
#     return render(request, 'library/books.html', context={'books': all_books})


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'my_book_list'
    template_name = 'library/book_list.html'


# # Importuojame FormMixin, kurį naudosime BookDetailView klasėje
# from django.views.generic.edit import FormMixin

# class BookDetailView(FormMixin, generic.DetailView):
#     model = Book
#     template_name = 'library/book_detail.html'
#     form_class = BookReviewForm

#     class Meta:
#         ordering = ['title']

#     # nurodome, kur atsidursime komentaro sėkmės atveju.
#     def get_success_url(self):
#         return reverse('library:book', kwargs={'pk': self.object.id})

#     # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)

#     # štai čia nurodome, kad knyga bus būtent ta, po kuria komentuojame, o vartotojas bus tas, kuris yra prisijungęs.
#     def form_valid(self, form):
#         form.instance.book = self.object
#         form.instance.reviewer = self.request.user
#         form.save()
#         return super(BookDetailView, self).form_valid(form)


class BookDetailView(generic.CreateView):
    model = BookReview
    template_name = 'library/book_detail.html'
    form_class = BookReviewForm

    def get_success_url(self):
        return reverse('library:book', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book, pk=self.kwargs.get('pk'))
        return context

    def form_valid(self, form):
        form.instance.book = get_object_or_404(Book, pk=self.kwargs.get('pk'))
        form.instance.reviewer = self.request.user
        return super().form_valid(form)


# @login_required
def authors(request):
    paginator = Paginator(Author.objects.all(), 2)
    page_number = request.GET.get('page')
    # all_authors = Author.objects.all()
    paged_authors = paginator.get_page(page_number)
    context = {
        'authors': paged_authors
    }
    return render(request, 'library/authors.html', context)


def author(request, author_id):
    # selected_author = Author.objects.get(pk=author_id)
    selected_author = get_object_or_404(Author, pk=author_id)
    context = {
        'author': selected_author
    }
    return render(request, 'library/author.html', context)


def search(request):
    query = request.GET.get('query')
    search_results = Book.objects.filter(Q(title__icontains=query) | Q(summary__icontains=query))
    return render(request, 'library/search.html', {'books': search_results, 'query': query})


# def register(request):
#     if request.method == 'POST':
#         # pasiimame reikšmes iš registracijos formos
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         password2 = request.POST['password2']

#         # tikriname, ar sutampa slaptažodžiai
#         if password == password2:
#             # tikriname, ar neužimtas username
#             if User.objects.filter(username=username).exists():
#                 messages.error(request, f'Vartotojo vardas {username} užimtas!')
#                 return redirect('library:register')
#             else:
#                 # tikriname, ar nėra tokio pat email
#                 if User.objects.filter(email=email).exists():
#                     messages.error(request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
#                     return redirect('library:register')
#                 else:
#                     # jeigu viskas tvarkoje, sukuriame naują vartotoją
#                     User.objects.create_user(username=username, email=email, password=password)
#                     messages.info(request, 'Registracija sėkminga')
#         else:
#             messages.error(request, 'Slaptažodžiai nesutampa!')
#             return redirect('library:register')

#     return render(request, 'library/register.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'], 
                email=form.cleaned_data['email'], 
                password=form.cleaned_data['password'])
            messages.info(request, 'Registracija sėkminga')
            return redirect('library:register')
    else:
        form = RegistrationForm()
    return render(request, 'library/register.html', {'form': form})


@login_required
def profilis(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfilisUpdateForm(request.POST, request.FILES, instance=request.user.profilis)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profilis atnaujintas")
            return redirect('library:profilis')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfilisUpdateForm(instance=request.user.profilis)
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'library/profilis.html', context=context)


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    context_object_name = 'books'
    template_name ='library/user_books.html'

    def get_queryset(self):
        return BookInstance.objects.filter(reader=self.request.user).order_by('due_back')


class BookByUserDetailView(LoginRequiredMixin, generic.DetailView):
    model = BookInstance
    template_name = 'library/user_book.html'


class BookByUserCreateView(LoginRequiredMixin, generic.CreateView):
    model = BookInstance
    # fields = ['book', 'due_back']
    success_url = reverse_lazy('library:mybooks')
    template_name = 'library/user_book_form.html'
    form_class = UserBookCreateForm

    def form_valid(self, form):
        form.instance.reader = self.request.user
        return super().form_valid(form)


class BookByUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = BookInstance
    fields = ['book', 'due_back']
    success_url = reverse_lazy('library:mybooks')
    template_name = 'library/user_book_form.html'

    # Toks variantas irgi galimas, atkreipkite demesi
    # i reverse() ir reverse_lazy() funkcijas

    # def get_success_url(self):
    #     return reverse('library:mybooks')

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.reader


class BookByUserDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = BookInstance
    success_url = reverse_lazy('library:mybooks')
    template_name = 'library/user_book_delete.html'

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.reader
