# Vérifications — Emby Metadata 1.2.9

## Contrôles de la version 1.2.4 — 30 septembre 2026

Tests exécutés dans Edge avec les états de démonstration :

- Sections fermées au départ, corps de section de hauteur nulle et inerte.
- Ouverture au clavier et animation avec hauteur intermédiaire mesurée.
- Fermeture animée et respect de la préférence de réduction des animations.
- Conservation de l’état ouvert lors d’une modification des métadonnées du même
  média, réinitialisation au changement de média.
- Bandeau de légende de même largeur que la photo, aligné en bas, noir à 60 %.
- Photo manquante ou invalide : silhouette de fond conservée et légende visible.
- Titre en haut et durée/note juste au-dessus du filet du synopsis.
- Largeurs 390, 600, 767, 768 et 1100 px ; trois colonnes sous 768 px, six au-dessus.
- Suppression de la colonne poster, synopsis animé, stabilité du DOM et repli des images.
- Traductions anglaise/française, variantes régionales et validation du JS généré.
- Page HTML autonome mise à jour ; captures mobile et horizontale inspectées.

Le backend Emby n’a pas été modifié. Ces tests n’utilisent pas le serveur Emby
de l’utilisateur et ne constituent pas une installation dans son Home Assistant.

## Historique des vérifications précédentes

Contrôles effectués le 29 septembre 2026. Les tests de rendu et du backend
ci-dessous ont été exécutés sur 1.2.2. La version 1.2.3 conserve ce code et
sépare les sources des traductions ; ses contrôles spécifiques figurent à la fin.

## Intégration : 16 tests réussis

Les dépendances Home Assistant et le transport HTTP ont été remplacés par des
doubles de test. Les fonctions de production du coordinateur, du capteur et des
images sont exécutées avec des réponses Emby simulées.

- Syntaxe de tous les fichiers Python et lecture de tous les fichiers JSON.
- Épisode enrichi : synopsis propre, nom de série, poster, backdrop, logo et personnes.
- Poster de saison et backdrop hérité.
- Repli du synopsis sans attribuer la note de série à l’épisode.
- Personnes sans nom ignorées, doublons supprimés, invités pris en compte ;
  correspondance entre les acteurs du capteur et les emplacements des images.
- Sélection des flux, sous-titres désactivés et choix par défaut.
- Filtrage HDR None/none/SDR et repli vers VideoRange.
- Exclusion des données de progression et utilisateur.
- Choix des flux correspondant à la version du média en lecture.
- Requête détaillée par utilisateur et cache.
- Repli vers la recherche d’éléments par identifiant.
- Conservation des détails connus pendant un échec temporaire d’enrichissement.
- Deux interrogations avec des positions différentes produisent les mêmes données.
- Intervalle au repos et absence de session.
- Attributs du capteur, saison 0 et résolution des identifiants d’images renommées.
- Cache des images et horodatage stables, invalidation au changement de source,
  indisponibilité en l’absence de source.

## Carte : tests dans Microsoft Edge

Carte exécutée dans un navigateur réel, avec des états HA et des images de test.

- Backdrop horizontal présent, ratio 16:9 conservé.
- Suppression de la colonne poster et utilisation de toute la largeur disponible.
- Largeurs de carte : 390, 600, 767, 768 et 1100 px ; absence de débordement.
- Grille de personnes de 2, 3 et 6 colonnes et poster uniquement en horizontal.
- Titre de série, saison 0, titre d’épisode et note avec virgule.
- Conservation des éléments DOM à données/configuration identiques, même si
  la position de lecture change.
- Hauteurs intermédiaires observées pendant l’animation du synopsis ; fermeture testée.
- Valeurs HDR sentinelles et note absente masquées.
- Repli texte en cas de logo invalide et repli poster si le backdrop échoue.
- Rotation du jeton HA sans reconstruction ; nouvelle version d’image détectée.
- Schéma du formulaire et validation des types.

Les captures horizontale et verticale ont également été inspectées visuellement.

## Éditeur visuel : test de référence de la version 1.2.1

Test exécuté dans la [démo publique Home Assistant](https://demo.home-assistant.io/),
avec le JavaScript 1.2.1 chargé comme carte personnalisée dans une session de test.
Ce test distant n’a pas été répété pour la version 1.2.3 ; les nouveaux callbacks
de traduction sont testés localement avec le contexte d’appel de cet éditeur.

1. La carte apparaît dans « Cartes de la communauté ».
2. Son éditeur visuel s’ouvre même sans entité initiale.
3. Une entité de démonstration peut être choisie avec le sélecteur natif.
4. Le panneau « Informations techniques » présente les trois options séparées.
5. Les cinq interrupteurs ont été actionnés dans l’interface. L’événement de
   configuration natif a produit :

```yaml
type: custom:emby-metadata-card
entity: sensor.battery_input
show_poster: false
show_cast: false
show_video: false
show_audio: false
show_subtitles: false
```

Cette entité est uniquement celle utilisée pour le test du sélecteur ; elle ne
doit pas remplacer l’entité Emby de votre configuration. Les options techniques
sont bien à la racine, sans dictionnaire `technical` ajouté.
L’aperçu accepte l’entité sélectionnée sans erreur de configuration.

## Limites

Le serveur Emby et l’instance Home Assistant de l’utilisateur n’étaient pas
accessibles. La récupération des vrais médias, les permissions de la clé API,
les photos réellement disponibles et le chargement de l’intégration dans cette
instance devront donc être confirmés après installation.

Le test visuel utilise le frontend de la démo disponible à cette date ; il ne
garantit pas le fonctionnement sur une ancienne version HA ne prenant pas en
charge `getConfigForm()`.


## Traductions 1.2.2 : tests locaux dans Edge

- Anglais par défaut sans langue HA ; français et variante fr-CA.
- Repli anglais pour les langues non prises en charge ; mêmes clés en/fr.
- Libellés et erreurs de l’éditeur appelés avec son contexte `hass`.
- Titre du groupe technique fourni par le callback de traduction.
- Nom des langues audio/sous-titres, rôle du réalisateur, indicateurs de sous-titres.
- Note avec point en anglais et virgule en français.
- Actualisation lors d’un changement de langue, y compris si l’entité manque.
- Conservation du DOM lorsque la langue et les données sont identiques.
- Métadonnées Emby conservées sans traduction automatique.

Les 16 tests Python et la suite de régression du rendu ont également été relancés
avec succès sur cette version.

## Génération 1.2.3

- Génération du JavaScript à partir des fichiers JSON en/fr.
- Vérification `--check` : sortie à jour.
- Syntaxe du JavaScript généré et suite de traduction dans Edge : succès.
- Huit cas de validation : fichiers valides et traduction partielle acceptés ;
  JSON invalide, doublons, clés inconnues, valeurs vides/non textuelles et
  paramètres de substitution incorrects rejetés.


## Version 1.2.5 — 30 septembre 2026

Tests Edge : synopsis entièrement sous le poster et sur toute la largeur utile
à 768 et 1100 px. Suite de régression du frontend relancée (mode sans poster,
responsive, sections repliables, synopsis animé, images et stabilité du DOM).
La règle CSS ne s’applique qu’à partir de 768 px lorsque le poster est activé.

## Version 1.2.6 — 1 octobre 2026

Ouverture exclusive du synopsis, des informations techniques et de la distribution. Vérification dans Edge aux largeurs 390 et 1100 px : toutes les transitions entre sections, clics rapides, fermeture de la section active, état conservé après changement des métadonnées. Régressions de mise en page et transitions existantes vérifiées. Pas de test sur une instance Home Assistant réelle pour cette modification.

## Version 1.2.7 — 1 octobre 2026

CSS fourni intégré (seul le sélecteur de prévisualisation est adapté au composant). Régressions navigateur : mise en page responsive, transitions et ouverture exclusive. Traductions allemandes et espagnoles : clés complètes, variables préservées, libellés et erreurs de l’éditeur, variantes de-DE et es-MX, repli anglais. Traductions de la configuration HA ajoutées. Pas de vérification sur une instance HA réelle pour cette version.

## Version 1.2.8 — 5 octobre 2026

CSS fourni intégré : padding du synopsis de 16 px en haut et en bas. Tests navigateur de régression réussis. Pierre confirme ses tests sur films, séries et films personnels avant ce dernier ajustement CSS. Configuration testée par Pierre : Core 2026.9.4, interface 20260826.7.

## Version 1.2.9

Sept tests de ressources avec doubles HA : installation, répétition, redémarrage, mise à jour, ressource manuelle, doublons, autres URL préservées, YAML intact, erreur et nouvelle tentative, deux clients et déchargement. API vérifiée sur le code HA 2026.9.4 (LovelaceData, async_get_info et collections de ressources). Mise à jour et recréation de la ressource confirmées sur HA réel par Pierre (voir ci-dessous) ; HACS/Hassfest restent à exécuter sur GitHub.

### Validation réelle par Pierre — 5 octobre 2026

Sur Home Assistant Core 2026.9.4 (interface 20260826.7) : mise à jour automatique de la ressource existante confirmée ; suppression de la ressource puis redémarrage HA confirmés, avec ajout automatique au démarrage. Le scénario de plusieurs lecteurs reste couvert par les tests automatisés, sans confirmation terrain à ce stade.
