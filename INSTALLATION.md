# Emby Metadata

[English](README.md) · [Français](INSTALLATION.md)

Une intégration Home Assistant pour les médias en cours de lecture sur un client Emby, accompagnée d’une carte de tableau de bord facultative.

**Utilisez la carte fournie ou créez votre propre tableau de bord.** Chaque client Emby configuré dispose de son propre capteur de métadonnées et de ses entités images, utilisables dans d’autres cartes Home Assistant et présentations personnalisées.

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/custom_components/emby_metadata/brand/icon.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/custom_components/emby_metadata/brand/icon.png" alt="Emby Metadata" width="128"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet.png" alt="Film sur tablette avec affiche et synopsis" width="640"></a>

[Captures d’écran](#captures-décran) · [Installation](#installation) · [Configuration de la carte Lovelace](#configuration-de-la-carte-lovelace)

## Fonctionnalités

- Films, épisodes de séries et vidéos personnelles, selon les métadonnées disponibles dans Emby.
- Présentation adaptative à 768 px, affiche facultative, arrière-plan proportionnel et logo du titre avec repli sur le texte.
- Commandes de lecture facultatives, temps écoulé/restant et progression, associés automatiquement au lecteur Emby correspondant dans Home Assistant.
- Synopsis, note, durée et informations vidéo, audio et sous-titres.
- Réalisateur et jusqu’à cinq acteurs, avec photos et portraits de remplacement.
- Sections animées : ouvrir une section referme les autres.
- Anglais, français, allemand et espagnol, selon la langue de Home Assistant.
- Images servies par Home Assistant ; la clé API Emby reste sur le serveur.
- Les métadonnées inchangées ne provoquent pas de reconstruction de la carte.

## Captures d’écran

Captures réelles de Home Assistant sur mobile et tablette. Les exemples utilisent l’interface française ; la carte prend aussi en charge l’anglais, l’allemand et l’espagnol. Cliquez sur une image pour l’ouvrir en taille originale.

### Mobile

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-synopsis.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-synopsis.jpg" alt="Synopsis et lecteur" width="280"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-technical.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-technical.jpg" alt="Informations techniques et lecteur" width="280"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-cast.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-cast.jpg" alt="Distribution et lecteur" width="280"></a>

### Tablette

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-technical.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-technical.png" alt="Informations techniques" width="640"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-cast.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-cast.png" alt="Distribution" width="640"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-no-poster.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-no-poster.png" alt="Lecteur sans affiche" width="640"></a>

### Épisodes de séries

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-tv-show.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-tv-show.jpg" alt="Épisode de série" width="640"></a>

## Installation

### Installer depuis HACS (recommandé)

1. Ouvrez **HACS** dans Home Assistant et recherchez **Emby Metadata**.
2. Ouvrez l’intégration et téléchargez-la.
3. Redémarrez Home Assistant, puis configurez votre lecteur comme indiqué ci-dessous.

### Avant de configurer un lecteur

**Le lecteur Emby ciblé doit être actif et connecté au serveur Emby pour être détecté.** Ouvrez l’application Emby sur cet appareil, connectez-vous et laissez-la ouverte pendant la configuration. Allumer uniquement l’appareil ne suffit pas. La détection utilise les sessions actives du serveur, et non la liste de tous les appareils utilisés auparavant.

Si le lecteur n’apparaît pas, lancez brièvement une lecture, puis revenez à l’étape de connexion au serveur et validez-la à nouveau pour actualiser la liste. Répétez cette préparation pour chaque lecteur supplémentaire.

### Configurer le lecteur

1. Ouvrez **Paramètres → Appareils et services → Ajouter une intégration → Emby Metadata**.
2. Renseignez le protocole, l’adresse du serveur, le port et la clé API Emby, puis sélectionnez le client à suivre. Démarrez le client s’il n’apparaît pas dans la liste.
3. La ressource de la carte est enregistrée automatiquement lorsque les ressources sont gérées par l’interface. Rechargez le navigateur après le redémarrage. Pour les ressources gérées en YAML, ajoutez cette URL comme **module JavaScript** :

```text
/api/emby_metadata/emby-metadata-card.js?v=2.0.0
```

En mode stockage, l’intégration crée ou met à jour sa ressource et supprime les doublons correspondant exactement à son adresse. Les entrées manuelles existantes à cette adresse sont réutilisées. Les autres URL ne sont pas modifiées. Les ressources YAML nécessitent toujours une mise à jour manuelle, avec la même URL et `type: module`. Supprimer ou recharger un client Emby conserve la ressource partagée de la carte.

### Installation manuelle (alternative)

1. Téléchargez l’archive **Source code (zip)** de la [dernière version](https://github.com/PedroDelCargo/ha-emby-metadata/releases/latest) et extrayez-la.
2. Copiez le dossier `custom_components/emby_metadata` de l’archive dans le dossier `custom_components` de Home Assistant.
3. Redémarrez Home Assistant, puis suivez la section **Configurer le lecteur** ci-dessus.

## Configuration de la carte Lovelace

Choisissez le capteur du lecteur et activez ou désactivez le lecteur, l’affiche, la vidéo, l’audio, les sous-titres et la distribution directement dans l’éditeur visuel de carte de Home Assistant.

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
show_player: false
```

Remplacez l’entité de l’exemple par votre capteur. Ces options sont aussi disponibles dans l’éditeur visuel. L’affiche concerne la présentation horizontale. Les sections vides sont masquées. Les titres, synopsis, genres et rôles restent dans la langue fournie par Emby.

### Lecteur facultatif

Activez **Afficher le lecteur et la progression** dans l’éditeur visuel (`show_player: true` en YAML). Cette option est désactivée par défaut, y compris après une mise à jour. Les configurations de cartes existantes continuent de fonctionner.

L’intégration native **Emby** doit fournir une entité `media_player` correspondante dans Home Assistant. Emby Metadata l’associe automatiquement grâce à l’identifiant du client Emby, même si l’entité a été renommée. Aucune sélection supplémentaire n’est nécessaire. Sans entité correspondante, le bloc lecteur est masqué ; les métadonnées et les images continuent de fonctionner indépendamment.

Le lecteur se place entre le synopsis et les informations techniques. Quelle que soit la taille de l’écran, le temps écoulé est à gauche, les commandes Précédent / Arrêter / Lecture-Pause / Suivant sont centrées et le temps restant est à droite. La progression se superpose au séparateur inférieur avec la couleur d’accentuation du thème Home Assistant. Elle n’est pas interactive. Précédent et Suivant concernent les éléments de la file de lecture du client, et non des sauts de quelques secondes. Les commandes dépendent des capacités du client et sont désactivées lorsqu’elles sont indisponibles. Les temps inconnus sont représentés par un tiret.

Le temps affiché avance localement pendant la lecture et se recale sur les informations reçues de Home Assistant. Cela n’ajoute aucune requête périodique à Emby. La note est en haut à droite, la durée totale est alignée à gauche au-dessus du synopsis et l’image du titre est limitée à la moitié de la largeur de la carte.

## Créer votre propre tableau de bord

La carte Emby Metadata fournie est facultative. L’intégration crée des entités pour chaque client Emby configuré : vous pouvez donc créer votre propre présentation avec des cartes Home Assistant prenant en charge ces entités et leurs attributs.

- **Capteur Now Playing :** titre actuel et attributs tels que synopsis, genres, année, durée, notes, détails de série/saison/épisode, informations vidéo/audio/sous-titres, réalisateur et acteurs.
- **Entités images :** affiche, arrière-plan, logo du titre, portrait du réalisateur et cinq portraits d’acteurs, selon les images disponibles dans Emby.

Retrouvez ces entités dans **Paramètres → Appareils et services → Emby Metadata**, puis ouvrez l’appareil correspondant au client. Consultez les attributs du capteur dans **Outils de développement → États**. Les identifiants d’entités dépendent de votre installation : utilisez ceux affichés dans votre Home Assistant.

Le capteur expose aussi `poster_entity`, `backdrop_entity` et `logo_entity`. Lorsque des personnes sont disponibles, `director` et les entrées de `actors` contiennent leurs noms, rôles et références `image_entity`. Les métadonnées dépendent des informations fournies par Emby ; les entités images peuvent être indisponibles lorsqu’aucune image correspondante n’existe.

## Délais de vérification

Ouvrez **Paramètres → Appareils et services → Emby Metadata**, puis la configuration/les options du lecteur concerné. Les délais sont réglables de **5 à 300 secondes**, en secondes entières :

| État du lecteur | Valeur par défaut |
| --- | --- |
| Connecté, sans lecture | 5 secondes |
| En lecture ou en pause | 5 secondes |
| Absent des sessions Emby | 30 secondes |

Les changements s’appliquent immédiatement, sans redémarrer Home Assistant. Les lecteurs déjà configurés reçoivent automatiquement ces valeurs par défaut. Les lecteurs utilisant la même adresse de serveur et la même clé API partagent une seule requête de sessions, au délai le plus court requis par leurs états actuels. Les adresses de serveur ou clés API différentes sont traitées séparément. Des délais plus courts augmentent les requêtes ; les caches des métadonnées et des images restent actifs.

Il s’agit de délais de vérification, pas d’une garantie sur le temps total d’affichage : Emby doit d’abord signaler la lecture, puis les métadonnées et images doivent être chargées. Si vous ouvrez l’application Emby et démarrez un film en même temps, le délai du lecteur absent peut encore affecter la détection. Essayez de le réduire à 10 secondes si nécessaire. Après une erreur de connexion au serveur, les vérifications des sessions reprennent après 30 secondes.

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

## Licence

MIT — voir [LICENSE](LICENSE).
