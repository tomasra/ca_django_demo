from django.contrib import admin
from .models import Book, BookInstance, Author, Genre, Profilis, BookReview


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0
    readonly_fields = ('id',)
    can_delete = False


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'display_genre',)
    list_filter = ('author__first_name',)
    inlines = [BooksInstanceInline]


class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'reader')
    list_filter = ('status', 'due_back',)
    readonly_fields = ('id',)
    search_fields = ('book__title',)
    list_editable = ('due_back', 'status')

    fieldsets = (
        ('Bendra informacija', {'fields': ('id', 'book',)}),
        ('Prieinamumas', {'fields': ('status', 'due_back', 'reader')}),
    )


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'display_books')
    search_fields = ('first_name', 'last_name')


class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'date_created', 'reviewer', 'content')


admin.site.register(Book, BookAdmin)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(Profilis)
admin.site.register(BookReview, BookReviewAdmin)

