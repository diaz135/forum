# views.py

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, CustomAuthenticationForm, PublicationForm , ProfileForm 
from .models import Publication, Commentaire, Like, Message, Profile, Projet, Auteur,Follow
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .models import Message as ChatMessage  # Renommer ici si nécessaire
from django.contrib.auth.models import User as AuthUser  # Renommer ici si nécessaire
from django.contrib.auth.decorators import permission_required
from django.views import View
from .forms import ProfileForm

def home(request):
    publications_approuvees = Publication.objects.filter(est_approuve=True).select_related('user')
    print(publications_approuvees)  # Affichez les publications dans la console
    return render(request, 'forum/home.html', {'publications': publications_approuvees})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # Vérification si le profil existe déjà pour cet utilisateur
            if not Profile.objects.filter(user=user).exists():
                profile = profile_form.save(commit=False)
                profile.user = user  # Lier le profil à l'utilisateur
                profile.save()
            
            # Vous pouvez ajouter une redirection vers une page de succès ou la page de connexion
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Vous êtes connecté avec succès !')  # Message de succès
            return redirect('home')  # Rediriger vers le profil
        else:
            messages.error(request, 'Identifiants invalides. Veuillez réessayer.')  # Message d'erreur
    else:
        form = CustomAuthenticationForm()
    return render(request, 'forum/login.html', {'form': form})

def publier(request):
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)  # Récupère les données du formulaire
        if form.is_valid():
            publication = form.save(commit=False)  # Ne pas enregistrer tout de suite
            publication.auteur = request.user  # Assigner l'utilisateur connecté
            publication.save()  # Maintenant, enregistrez l'objet
            messages.success(request, "Votre publication est en cours d'approbation.")  # Message de confirmation
            return redirect('home')  # Redirigez vers la page d'accueil ou une autre page
    else:
        form = PublicationForm()  # Crée un nouveau formulaire vide

    return render(request, 'forum/publier.html', {'form': form})  # Rendu du template avec le formulaire

@staff_member_required
def verifier_publications(request):
    publications_non_approuvees = Publication.objects.filter(est_approuve=False)
    publications_approuvees = Publication.objects.filter(est_approuve=True)

    context = {
        'publications_non_approuvees': publications_non_approuvees,
        'publications_approuvees': publications_approuvees,
    }
    return render(request, 'forum/verifier_publications.html', context)

@staff_member_required
def approuver_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publication.est_approuve = True
    publication.save()
    messages.success(request, 'Publication approuvée avec succès !')
    
    # Débogage : Imprimez la publication pour confirmer qu'elle est approuvée
    print(f'Publication {publication.id} approuvée: {publication.est_approuve}')
    
    return redirect('verifier_publications')

@csrf_exempt  # Utilisez ceci si vous n'avez pas encore configuré le CSRF pour les requêtes AJAX
@login_required  # Assurez-vous que l'utilisateur est connecté
def commenter(request):
    if request.method == 'POST':
        publication_id = request.POST.get('publication_id')
        contenu = request.POST.get('contenu')
        
        # Créez un nouveau commentaire
        publication = get_object_or_404(Publication, id=publication_id)
        commentaire = Commentaire.objects.create(
            publication=publication,
            contenu=contenu,
            auteur=request.user  # Assurez-vous que l'utilisateur est authentifié
        )
        
        # Retournez une réponse JSON
        return JsonResponse({
            'auteur': commentaire.auteur.username,
            'contenu': commentaire.contenu,
            'date_creation': commentaire.date_creation.strftime("%d %b %Y %H:%M")
        })

def liker(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    like, created = Like.objects.get_or_create(publication=publication, utilisateur=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    new_like_count = publication.likes.count()
    return JsonResponse({'new_like_count': new_like_count, 'liked': liked})

@login_required
def envoyer_message(request, destinataire_id):
    destinataire = get_object_or_404(User, id=destinataire_id)
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        Message.objects.create(expediteur=request.user, destinataire=destinataire, contenu=contenu)
        messages.success(request, 'Message envoyé avec succès !')
        return redirect('home')
    return render(request, 'forum/envoyer_message.html', {'destinataire': destinataire})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie !')
    return redirect('home')

def publication_detail(request, id):
    publication = get_object_or_404(Publication, id=id)
    return render(request, 'forum/publication_detail.html', {'publication': publication})

def get_publication_data(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)  # Utilisation de get_object_or_404 pour la sécurité
    commentaires = [
        {
            'auteur': commentaire.auteur.username,  # Obtenez le nom d'utilisateur
            'contenu': commentaire.contenu,
            'date_creation': commentaire.date_creation.strftime("%d %b %Y %H:%M")
        }
        for commentaire in publication.commentaires.all()
    ]
    data = {
        'likes_count': publication.likes.count(),
        'commentaires': commentaires,
    }
    return JsonResponse(data)

@receiver(post_save, sender=User )
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User )
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request.user.profile.followers.add(user_to_follow)
    return redirect('profile', user_id=user_id)  # Redirigez vers le profil de l'utilisateur

@login_required
def chat(request, utilisateur_id):
    destinataire = get_object_or_404(User, id=utilisateur_id)
    messages = ChatMessage.objects.filter(
        (Q(expediteur=request.user) & Q(destinataire=destinataire)) |
        (Q(expediteur=destinataire) & Q(destinataire=request.user))
    ).order_by('date_envoi')

    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:  # Vérifiez que le contenu n'est pas vide
            ChatMessage.objects.create(expediteur=request.user, destinataire=destinataire, contenu=contenu)
            return redirect('chat', utilisateur_id=utilisateur_id)
        else:
            messages.error(request, 'Le message ne peut pas être vide.')  # Ajoutez un message d'erreur

    return render(request, 'forum/chat.html', {'destinataire': destinataire, 'messages': messages})

@login_required
class ProfilView(View):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(Profile, user=user)  # Récupérer le profil associé à l'utilisateur
        publications = Publication.objects.filter(auteur=user)  # Récupérer les publications de l'utilisateur
        return render(request, 'forum/profil.html', {
            'user': user,
            'profile': profile,
            'publications': publications
        })
    
@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'forum/edit_profile.html', {'form': form})

@login_required
def profile(request):
    publications = Publication.objects.filter(user=request.user)
    return render(request, 'forum/profile.html', {'publications': publications})

@login_required
def edit_publication(request, pk):
    publication = get_object_or_404(Publication, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PublicationForm(request.POST, instance=publication)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirigez vers le profil après l'édition
    else:
        form = PublicationForm(instance=publication)
    
    return render(request, 'forum/edit_publication.html', {
        'form': form,
        'publication': publication,  # Ajoutez l'objet publication au contexte
    })


@login_required
def supprimer_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    if request.method == 'POST':
        publication.delete()
        return redirect('profile')  # Redirigez vers la page de profil ou une autre page après la suppression
    return render(request, 'confirmer_suppression.html', {'publication': publication})

def forum_view(request):
    # Récupérer tous les projets avec leurs auteurs
    publications = Projet.objects.select_related('auteur').all()
    return render(request, 'forum/forum.html', {'publications': publications})

def profil_auteur_view(request, id):
    auteur = get_object_or_404(User, id=id)  # Cela renverra une 404 si l'utilisateur n'existe pas
    publications = Publication.objects.filter(user=auteur)  # Récupère les publications de cet auteur
    return render(request, 'forum/profil_auteur.html', {'auteur': auteur, 'publications': publications})

def follow_user(request, user_id):
    print(f"User  {request.user.username} is trying to follow/unfollow user with ID {user_id}")
    user_to_follow = get_object_or_404(User, id=user_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    
    if not created:
        print(f"User  {request.user.username} is already following {user_to_follow.username}. Unfollowing now.")
        follow.delete()  # Désabonne l'utilisateur
        message = "Vous vous êtes désabonné."
    else:
        print(f"User  {request.user.username} is now following {user_to_follow.username}.")
        message = "Vous suivez maintenant cet utilisateur."
    
    messages.success(request, message)  # Ajoutez un message de succès
    return redirect('profil_auteur', id=user_id)  # Redirige vers le profil de l'utilisateur

def like_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    # Logique pour aimer la publication
    Like.objects.get_or_create(publication=publication, utilisateur=request.user)
    return redirect('publication_detail', id=publication.id)  # Utilisez 'id' ici


def unlike_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    Like.objects.filter(publication=publication, utilisateur=request.user).delete()
    return redirect('publication_detail', publication_id=publication.id)
   

def profil_auteur(request, auteur_id):
    auteur = get_object_or_404(User, id=auteur_id)
    publications = Publication.objects.filter(auteur=auteur)

    # Créer un ensemble d'IDs de publications que l'utilisateur a aimées
    liked_publications = Like.objects.filter(utilisateur=request.user).values_list('publication_id', flat=True)

    context = {
        'auteur': auteur,
        'publications': publications,
        'liked_publications': liked_publications,  # Passer les publications aimées
    }
    return render(request, 'forum/profil_auteur.html', context)

@login_required
def profile(request):
    publications = Publication.objects.filter(user=request.user)
    total_likes = Like.objects.filter(publication__in=publications).count()  # Compte le nombre total de likes
    return render(request, 'forum/profile.html', {
        'publications': publications,
        'total_likes': total_likes,  # Ajoutez le total des likes au contexte
    })

from django.http import JsonResponse

@login_required
def like_publication_ajax(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    like, created = Like.objects.get_or_create(publication=publication, utilisateur=request.user)

    if created:
        message = 'Vous avez aimé la publication !'
    else:
        message = 'Vous avez déjà aimé cette publication.'

    return JsonResponse({
        'message': message,
        'likes_count': publication.likes.count(),  # Renvoie le nombre total de likes
        'liked': created  # Indique si le like a été créé ou non
    })