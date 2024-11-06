from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    home,
    register,
    login_view,
    publier,
    verifier_publications,
    approuver_publication,
    commenter, 
    liker,
    chat,
    logout_view, 
    supprimer_publication,
    publication_detail, 
    get_publication_data, 
    follow_user, 
    envoyer_message, 
    edit_profile, 
    profile, 
    edit_publication,
    profil_auteur_view, 
    like_publication, 
    unlike_publication, 
    like_publication_ajax
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('publier/', publier, name='publier'),
    path('verifier_publications/', verifier_publications, name='verifier_publications'),
    path('approuver_publication/<int:publication_id>/', approuver_publication, name='approuver_publication'),
    path('commenter/', commenter, name='commenter'),
    path('liker/<int:publication_id>/', liker, name='liker'),
    path('envoyer_message/<int:destinataire_id>/', envoyer_message, name='envoyer_message'),
    path('chat/<int:utilisateur_id>/', chat, name='chat'),
    path('logout/', logout_view, name='logout'),
    path('publication/<int:id>/', publication_detail, name='publication_detail'),
    path('publication/data/<int:publication_id>/', get_publication_data, name='get_publication_data'),
    path('follow/<int:user_id>/', follow_user, name='follow_user'),
    path('profil/', profile, name='profile'),
    path('profil/edit_publication/<int:pk>/', edit_publication, name='edit_publication'),
    path('edit_profile/', edit_profile, name='edit_profile'), 
    path('publication/supprimer/<int:publication_id>/', supprimer_publication, name='supprimer_publication'),
    path('profil/auteur/<int:id>/', profil_auteur_view, name='profil_auteur'),
    path('publication/<int:publication_id>/like/', like_publication, name='like_publication'),
    path('publication/<int:publication_id>/unlike/', unlike_publication, name='unlike_publication'),
    path('like_publication/<int:publication_id>/', like_publication_ajax, name='like_publication_ajax'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
