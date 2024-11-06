from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Publication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='publications/', blank=True, null=True)
    date_pub = models.DateTimeField(auto_now_add=True)
    est_approuve = models.BooleanField(default=False)

    def __str__(self):
        return self.titre
    
    def nombre_de_commentaires(self):
        return self.commentaires.count()

    def nombre_de_likes(self):
        return self.likes.count()


class Commentaire(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField(validators=[MaxLengthValidator(1000)])  # Limite la longueur
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.auteur.username} - {self.contenu}"


class Like(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='likes')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('publication', 'utilisateur')  # Empêche les doublons

    def __str__(self):
        return f"{self.utilisateur.username} aime {self.publication.titre}"


class Message(models.Model):
    expediteur = models.ForeignKey(User, related_name='messages_envoyes', on_delete=models.CASCADE)
    destinataire = models.ForeignKey(User, related_name='messages_recus', on_delete=models.CASCADE)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.expediteur.username} à {self.destinataire.username}: {self.contenu[:20]}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Auteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Projet(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    auteur = models.ForeignKey(Auteur, on_delete=models.CASCADE, related_name='projets')
    approuve = models.BooleanField(default=False)
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'followed') 


# Signaux pour créer et sauvegarder le profil
@receiver(post_save, sender=User )
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User )
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()