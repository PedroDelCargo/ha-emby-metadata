# Emby Metadata

[English](README.md) · [Français](INSTALLATION.md)

Une intégration Home Assistant pour les médias en cours de lecture sur un client Emby, accompagnée d’une carte de tableau de bord facultative.

**Utilisez la carte fournie ou créez votre propre tableau de bord.** Chaque client Emby configuré dispose de son propre capteur de métadonnées et de ses entités images, utilisables dans d’autres cartes Home Assistant et présentations personnalisées.

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/custom_components/emby_metadata/brand/icon.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/custom_components/emby_metadata/brand/icon.png" alt="Emby Metadata" width="128"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-synopsis.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-synopsis.jpg" alt="Film sur tablette avec affiche et synopsis" width="640"></a>

[Captures d’écran](#captures-décran) · [Installation](#installation) · [Configuration de la carte](#configuration)

## Fonctionnalités

- Films, épisodes de séries et vidéos personnelles, selon les métadonnées disponibles dans Emby.
- Présentation adaptative à 768 px, affiche facultative, arrière-plan proportionnel et logo du titre avec repli sur le texte.
- Synopsis, note, durée et informations vidéo, audio et sous-titres.
- Réalisateur et jusqu’à cinq acteurs, avec photos et portraits de remplacement.
- Sections animées : ouvrir une section referme les autres.
- Anglais, français, allemand et espagnol, selon la langue de Home Assistant.
- Images servies par Home Assistant ; la clé API Emby reste sur le serveur.
- Les métadonnées inchangées ne provoquent pas de reconstruction de la carte.

## Captures d’écran

Captures réelles de Home Assistant sur mobile et tablette. Les exemples utilisent l’interface française ; la carte prend aussi en charge l’anglais, l’allemand et l’espagnol. Cliquez sur une image pour l’ouvrir en taille originale.

### Mobile

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-synopsis-small.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-synopsis-small.jpg" alt="Carte mobile avec synopsis réduit" width="280"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-actors.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-actors.jpg" alt="Carte mobile avec réalisateur et acteurs affichés" width="280"></a>

Synopsis compact et distribution dépliable, avec noms et rôles en surimpression sur les portraits.

**Autres vues mobiles : synopsis complet et informations techniques**

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-synopsis-full.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-synopsis-full.jpg" alt="Carte mobile avec synopsis complet" width="280"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-technical-data.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-technical-data.jpg" alt="Carte mobile avec informations vidéo, audio et sous-titres" width="280"></a>

### Épisodes de séries

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-tv-show.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-tv-show.jpg" alt="Épisode avec logo de série, saison, numéro, titre et synopsis" width="640"></a>

Illustrations de la série et informations propres à l’épisode. L’affiche est masquée dans cet exemple.

**Autres vues sur tablette : informations techniques et distribution**

**Vidéo, audio et sous-titres, avec l’affiche activée**

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-technical-data.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-technical-data.jpg" alt="Carte tablette avec informations techniques" width="640"></a>

**Réalisateur et acteurs, avec l’affiche masquée**

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-actors.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-actors.jpg" alt="Carte tablette avec réalisateur et acteurs" width="280"></a>

## Installation

### Avant de configurer un lecteur

**Le lecteur Emby ciblé doit être actif et connecté au serveur Emby pour être détecté.** Ouvrez l’application Emby sur cet appareil, connectez-vous et laissez-la ouverte pendant la configuration. Allumer uniquement l’appareil ne suffit pas. La détection utilise les sessions actives du serveur, et non la liste de tous les appareils utilisés auparavant.

Si le lecteur n’apparaît pas, lancez brièvement une lecture, puis revenez à l’étape de connexion au serveur et validez-la à nouveau pour actualiser la liste. Répétez cette préparation pour chaque lecteur supplémentaire.

### Installer et configurer

1. Copiez `custom_components/emby_metadata` dans le dossier `custom_components` de Home Assistant.
2. Redémarrez Home Assistant.
3. Ouvrez **Paramètres → Appareils et services → Ajouter une intégration → Emby Metadata**.
4. Renseignez le protocole, l’adresse du serveur, le port et la clé API Emby, puis sélectionnez le client à suivre. Démarrez le client s’il n’apparaît pas dans la liste.
5. La ressource de la carte est enregistrée automatiquement lorsque les ressources sont gérées par l’interface. Rechargez le navigateur après le redémarrage. Pour les ressources gérées en YAML, ajoutez cette URL comme **module JavaScript** :

```text
/api/emby_metadata/emby-metadata-card.js?v=1.2.12
```

En mode stockage, l’intégration crée ou met à jour sa ressource et supprime les doublons correspondant exactement à son adresse. Les entrées manuelles existantes à cette adresse sont réutilisées. Les autres URL ne sont pas modifiées. Les ressources YAML nécessitent toujours une mise à jour manuelle, avec la même URL et `type: module`. Supprimer ou recharger un client Emby conserve la ressource partagée de la carte.

`https://github.com/PedroDelCargo/ha-emby-metadata` peut être installé comme dépôt personnalisé HACS de type **Intégration**. Redémarrez Home Assistant et suivez les étapes 3 à 5. Le projet ne figure pas encore dans le catalogue HACS par défaut.

## Configuration

Choisissez le capteur du lecteur et activez ou désactivez l’affiche, la vidéo, l’audio, les sous-titres et la distribution directement dans l’éditeur visuel de carte de Home Assistant.

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/configuration.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/configuration.jpg" alt="Éditeur visuel Home Assistant de la carte Emby Metadata" width="280"></a>

Vous pouvez également configurer la carte en YAML :

```yaml
type: custom:emby-metadata-card
entity: sensor.emby_metadata_shield_tv
show_poster: true
show_video: true
show_audio: true
show_subtitles: true
show_cast: true
```

Remplacez l’entité de l’exemple par votre capteur. Ces options sont aussi disponibles dans l’éditeur visuel. L’affiche concerne la présentation horizontale. Les sections vides sont masquées. Les titres, synopsis, genres et rôles restent dans la langue fournie par Emby.

## Créer votre propre tableau de bord

La carte Emby Metadata fournie est facultative. L’intégration crée des entités pour chaque client Emby configuré : vous pouvez donc créer votre propre présentation avec des cartes Home Assistant prenant en charge ces entités et leurs attributs.

- **Capteur Now Playing :** titre actuel et attributs tels que synopsis, genres, année, durée, notes, détails de série/saison/épisode, informations vidéo/audio/sous-titres, réalisateur et acteurs.
- **Entités images :** affiche, arrière-plan, logo du titre, portrait du réalisateur et cinq portraits d’acteurs, selon les images disponibles dans Emby.

Retrouvez ces entités dans **Paramètres → Appareils et services → Emby Metadata**, puis ouvrez l’appareil correspondant au client. Consultez les attributs du capteur dans **Outils de développement → États**. Les identifiants d’entités dépendent de votre installation : utilisez ceux affichés dans votre Home Assistant.

Le capteur expose aussi `poster_entity`, `backdrop_entity` et `logo_entity`. Lorsque des personnes sont disponibles, `director` et les entrées de `actors` contiennent leurs noms, rôles et références `image_entity`. Les métadonnées dépendent des informations fournies par Emby ; les entités images peuvent être indisponibles lorsqu’aucune image correspondante n’existe.

## Plusieurs lecteurs Emby

Ajoutez une configuration de l’intégration pour chaque lecteur Emby :

1. Ouvrez Emby sur le lecteur supplémentaire pour que le serveur le reconnaisse comme client actif.
2. Dans **Paramètres → Appareils et services → Ajouter une intégration**, choisissez à nouveau **Emby Metadata**.
3. Renseignez les mêmes paramètres de serveur et la même clé API si le lecteur utilise le même serveur Emby.
4. Sélectionnez le lecteur supplémentaire. Un lecteur déjà configuré ne peut pas être ajouté deux fois.
5. Ajoutez une nouvelle carte au tableau de bord, ou dupliquez une carte existante, et sélectionnez le capteur du nouveau lecteur dans l’éditeur visuel.

Chaque lecteur possède son propre capteur et ses entités images. Retrouvez le bon capteur parmi les entités associées à sa configuration ; les identifiants dépendent de votre installation. Chaque carte affiche le média en cours de lecture sur le lecteur sélectionné : plusieurs cartes peuvent donc présenter simultanément des médias différents.

Tous les lecteurs partagent une seule ressource JavaScript. N’ajoutez pas de ressource supplémentaire ni de deuxième copie des fichiers de l’intégration. Cela s’applique aussi aux ressources gérées en YAML : déclarez la ressource une seule fois.

## Dépannage

- **Custom element does not exist :** vérifiez l’URL de la ressource, redémarrez Home Assistant et actualisez le cache du navigateur.
- **Client absent :** démarrez le client Emby et recommencez la configuration.
- **Personnes ou images manquantes :** vérifiez les métadonnées du média dans Emby ; les solutions de remplacement dépendent des données disponibles.
- **Aucune lecture affichée :** vérifiez que le client configuré lit bien le média.

## Compatibilité

Testé avec Home Assistant Core **2026.9.4**, interface **20260826.7**. Les versions antérieures n’ont pas été vérifiées.

## Contribuer

Consultez [CONTRIBUTING.md](CONTRIBUTING.md) et [TRANSLATIONS.md](TRANSLATIONS.md). Les utilisateurs n’ont pas besoin de générer le JavaScript fourni. La version anglaise de ce guide est disponible dans [README.md](README.md).

## État de publication

Disponible comme dépôt personnalisé HACS. La [demande d’ajout au catalogue par défaut](https://github.com/hacs/default/pull/11725) est en attente d’examen.

## Licence

MIT — voir [LICENSE](LICENSE).
