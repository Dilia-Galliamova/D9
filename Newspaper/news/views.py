from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .filters import PostFilter
from .forms import PostForm
from .models import Post, Subscription, Author, Category, PostCategory


@login_required
def upgrade_me(request):
    user = request.user
    new_author = Author(rating=0, user=user)
    new_author.save()
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
    return redirect('posts')


def subscribe(request, *args, **kwargs):
    user = request.user
    category = Category.objects.get(id=int(request.path[-1]))
    subscription = Subscription(
        user=user,
        category=category
    )
    subscription.save()
    category.user.add(user)

    return redirect('post_search')


class PostsList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-create_time'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
       queryset = super().get_queryset()
       self.filterset = PostFilter(self.request.GET, queryset)
       return self.filterset.qs

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['filterset'] = self.filterset
       context['is_author'] = not self.request.user.groups.filter(name='authors').exists()
       return context


class PostsFilter(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-create_time'
    template_name = 'post_search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
       queryset = super().get_queryset()
       self.filterset = PostFilter(self.request.GET, queryset)
       return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['subscribed'] = True
        user = self.request.user
        if self.request.GET.__contains__('category'):
            context['category'] = self.request.GET.__getitem__('category')
            id = int(context['category'])
            list_id = list(Subscription.objects.filter(user=user).values_list('category', flat=True))
            if Subscription.objects.filter(user=user).exists() and id in list_id:
                context['subscribed'] = False

        return context


class OnePost(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'NW'
        post = form.save(commit=True)
        # html_content = render_to_string(
        #     'news_subscribers.html',
        #     {
        #         'post': post,
        #     }
        # )
        # categories = list(PostCategory.objects.filter(post=post).values_list('category', flat=True))
        #
        # for item in categories:
        #     msg = EmailMultiAlternatives(
        #         subject=post.title,
        #         body=post.text[:20],
        #         from_email='mytestemailDilia@yandex.ru',
        #         to=list(Subscription.objects.filter(category__id=item).values_list('user__email', flat=True)),
        #     )
        #     msg.attach_alternative(html_content, "text/html")
        #     msg.send()

        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ('news.delete_post')
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')


class ArticleCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    form_class = PostForm
    model = Post
    template_name = 'article_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'PS'

        return super().form_valid(form)


class ArticleUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'article_edit.html'


class ArticleDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ('news.delete_post')
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')
