# Emby Metadata 1.2.9

Version 1.2.9 : enregistrement et mise à jour automatiques de la ressource de carte en mode stockage. Une seule section se développe à la fois.
Sans poster visible, la disposition précédente est conservée.
La carte et le manifeste portent le même numéro : 1.2.9.

## Installation

1. Conserver une copie du dossier actuellement installé.
2. Copier le dossier `custom_components/emby_metadata` de cette archive dans
   `/config/custom_components/emby_metadata`, en remplaçant les fichiers existants.
   Le nouveau fichier `metadata.py` doit être copié lui aussi.
3. Redémarrer Home Assistant. Il n’est pas nécessaire de supprimer ni de recréer
   l’intégration : les identifiants des capteurs et images sont conservés.
4. La ressource est ajoutée automatiquement en mode stockage (gestion par l’interface). Une ancienne entrée à la même URL est mise à jour. Pour les ressources gérées en YAML uniquement, utiliser `/api/emby_metadata/emby-metadata-card.js?v=1.2.9`, type `module`.
5. Recharger complètement le navigateur (Ctrl+F5 sur ordinateur).

Le JavaScript séparé remplace seulement
`/config/custom_components/emby_metadata/static/emby-metadata-card.js`.
Pour bénéficier des corrections des personnes et des épisodes, installer l’archive complète.

## Configuration

Les sections Informations techniques et Distribution sont fermées par défaut.
Cliquer sur leur titre, ou utiliser Entrée/Espace au clavier, pour les ouvrir.
L’état est conservé pendant les mises à jour du même média et réinitialisé au
changement de média. Une section sans données ou désactivée dans les options
n’apparaît pas.

Le CSS reprend les ajustements fournis par l’utilisateur : portraits de 150 px
maximum, trois colonnes sur petit écran et six à partir de 768 px. Le titre et
les genres restent en haut ; durée et note sont positionnées au bas du bloc
d’introduction, juste avant le synopsis. Les légendes des portraits sont intégrées
sur un bandeau noir à 60 %. Une silhouette discrète reste visible en l’absence
de photo ou en cas d’échec du chargement.

```yaml
type: custom:emby-metadata-card
entity: sensor.emby_metadata_shield_tv
show_poster: true
show_cast: true
show_video: true
show_audio: true
show_subtitles: true
```

Remplacer l’entité de l’exemple par celle déjà utilisée. Tous les réglages sont
disponibles dans l’éditeur visuel ; vidéo, audio et sous-titres sont regroupés
sous « Informations techniques ». Le poster est affiché uniquement à partir
de 768 px de largeur **de la carte**. Une fenêtre large avec des colonnes étroites
peut donc conserver la présentation verticale.

## Ajouter un deuxième lecteur Emby

Créer une configuration de l’intégration par lecteur :

1. Ouvrir Emby sur le lecteur supplémentaire pour qu’il apparaisse parmi les clients actifs du serveur.
2. Dans **Paramètres → Appareils et services → Ajouter une intégration**, choisir à nouveau **Emby Metadata**.
3. Renseigner les mêmes paramètres de serveur et la même clé API si le lecteur utilise le même serveur Emby.
4. Sélectionner le lecteur supplémentaire. Un lecteur déjà configuré ne peut pas être ajouté deux fois.
5. Ajouter une nouvelle carte au tableau de bord, ou dupliquer une carte existante, puis sélectionner le capteur du nouveau lecteur dans l’éditeur visuel.

Chaque lecteur possède son propre capteur et ses propres entités images. Le capteur se retrouve dans les entités associées à sa configuration de l’intégration ; son identifiant dépend de l’installation. Chaque carte affiche la lecture de son lecteur : plusieurs cartes peuvent donc présenter des médias différents simultanément.

La ressource JavaScript est unique et partagée entre tous les lecteurs. Il ne faut ni ajouter une nouvelle ressource ni installer une deuxième copie des fichiers de l’intégration. Même en mode YAML, la ressource ne se déclare qu’une seule fois.

## Langues

La carte et son éditeur suivent automatiquement la langue de Home Assistant.
L’anglais est la langue par défaut ; le français, l’allemand et l’espagnol sont inclus, avec prise en charge
des variantes comme `fr-CA`. Les langues non prises en charge utilisent l’anglais.
La note utilise le séparateur décimal de la langue choisie. Aucune option YAML
supplémentaire n’est nécessaire. Les métadonnées restent dans la langue d’Emby.
Voir `TRANSLATIONS.md` pour ajouter une traduction.

L’archive inclut également `frontend/` et `scripts/` pour les contributeurs.
Ces dossiers ne sont pas à copier dans Home Assistant : le JavaScript fourni
est déjà généré et contient les traductions.

## Corrections conservées depuis 1.2.1

- Une seule structure de carte : backdrop commun aux deux présentations,
  image proportionnelle sans recadrage, overlay noir de 30 %, puis fondu vers
  le noir sur le dernier tiers. Le fond inférieur reste noir.
- `show_poster: false` supprime la colonne ; le contenu occupe la largeur disponible.
- Poster horizontal de 210 à 230 px suivant la largeur, contre 145 à 180 px auparavant.
- Synopsis animé à l’ouverture et à la fermeture, également utilisable au clavier.
  La préférence système de réduction des animations est respectée.
- Séparateurs renforcés au-dessus et sous le synopsis, ainsi qu’avant la distribution.
- Valeurs HDR `None`, `none`, vides et SDR masquées. Note sous la forme `★ 6,4`.
- Logo du titre remplacé par le titre texte en cas d’erreur ; autres images avec
  repli ou emplacement neutre. Une note absente ne devient plus une note de zéro.
- Réalisateur et cinq acteurs : sélection commune au capteur et aux images,
  suppression des doublons et des personnes sans nom, prise en compte des invités.
  Les photos passent par Home Assistant ; la clé API Emby reste côté serveur.
- Métadonnées détaillées obtenues par `/Users/{UserId}/Items/{Id}`, avec repli
  sur `/Items?Ids=...&Fields=...`. Les images sont initialisées avant le capteur.
- Épisodes : titre de série, saison et numéro d’épisode (y compris saison 0 et
  épisodes doubles), titre et synopsis d’épisode. Synopsis, genres et personnes
  complétés par la saison/série selon disponibilité. La note de série n’est pas
  présentée comme une note d’épisode.
- Poster de saison puis de série en priorité ; backdrop et logo hérités selon
  disponibilité. La vignette d’épisode peut servir de dernier repli au backdrop.
- Première récupération immédiate ; sessions vérifiées toutes les 5 s pendant
  la lecture et toutes les 30 s au repos. Les détails sont mis en cache 5 minutes,
  avec nouvelle tentative après 30 s en cas d’échec d’enrichissement.
- Position de lecture et données utilisateur exclues de la comparaison. À données
  identiques, la carte garde ses éléments et son synopsis ouvert. Le renouvellement
  du jeton d’image HA ne reconstruit pas la carte ; un changement d’image l’invalide.

## Après installation

Tester un film puis un épisode sur l’appareil Emby sélectionné. Dans
**Outils de développement → États**, le capteur doit fournir `director`, `actors`,
et, pour un épisode, `series_title`, `season_number`, `episode_number`.
Les références `image_entity` doivent désigner les entités image de l’intégration.
Un nom peut être affiché même lorsqu’Emby ne possède aucune photo correspondante.

Les contrôles exécutés et leurs limites sont détaillés dans `VERIFICATION.md`.

## Références techniques

- [Éditeur natif des cartes Home Assistant](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/#using-the-built-in-form-editor)
- [Métadonnées d’un élément Emby](https://dev.emby.media/doc/restapi/Item-Information.html)
- [Élément de la bibliothèque d’un utilisateur](https://dev.emby.media/reference/RestAPI/UserLibraryService/getUsersByUseridItemsById.html)
- [Recherche d’éléments Emby](https://dev.emby.media/reference/RestAPI/ItemsService/getItems.html)
