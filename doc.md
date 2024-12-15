# Documentation technique

## Sommaire

### [Code Client](#code-client-python)
- [Fonctionnalités](#fonctionnalités)
- [Fonctions](#fonctions)
- [Fonctionnement](#fonctionnement)
- [Utilisation](#utilisation)
- [Dépendances](#dépendances)

### [Code Serveur](#code-serveur-c)
- [Fonctionnalités](#fonctionnalités-1)
- [Fonctions Principales](#fonctions-principales)
- [Utilisation](#utilisation)
- [Fonctionnement](#fonctionnement-1)
- [Dépendances](#dépendances-1)

---

## [Code Client (Python)]

### Fonctionnalités

#### Découverte des serveurs

- Découverte des serveurs disponibles sur le réseau local via une diffusion UDP.
- Recherche des serveurs sur le réseau local hébergeant un fichier spécifique.

#### Gestion des commandes

- Cartographie dynamique et exécution des commandes côté client.
- Vérification des arguments des commandes avant de les envoyer au serveur.

#### Communication par socket

- Création de sockets TCP pour la communication client-serveur.
- Création d'un socket UDP pour entrer en contact avec les serveurs.

#### Gestion des fichiers et répertoires

- Upload de fichiers et répertoires vers le serveur connecté.
- Download de fichiers et répertoires depuis le serveur connecté.
- Navigation dans les répertoires côté client et côté serveur.
- Création de répertoire côté client et côté serveur.

---

### Fonctions

#### `create_socket()`

Crée et retourne un socket TCP.

- **Retourne** : `client_socket` - Le socket créé pour la communication.
- **Gestion des erreurs** : Quitte le programme et prévient l'utilisateur de l'erreur en cas d'échec de la création du socket.

#### `connect_socket(client_socket, host, port)`

Connecte le socket donné à un hôte et un port spécifiques.

- **Paramètres** :
  - `client_socket` : Le socket TCP.
  - `host` (str) : Adresse IP du serveur.
  - `port` (int) : Numéro du port.
- **Gestion des erreurs** : Quitte le programme et prévient l'utilisateur de l'erreur en cas d'échec de la connexion.

#### `handle_command(client_socket, message)`

Traite une commande utilisateur et utilise la fonction appropriée depuis `cmd_h.command_map`.

- **Paramètres** :
  - `client_socket` : Le socket client actif.
  - `message` (str) : La commande saisie par l'utilisateur.
- **Comportement** :
  - Divise le message en parties.
  - Associe la commande à `cmd_h.command_map` et exécute la fonction correspondante.
  - Affiche un message d'erreur si la commande est introuvable, le programme continue son exécution normalement.

#### `discover_servers(broadcast_port)`

Découvre les serveurs sur le réseau local via une diffusion UDP.

- **Paramètres** :
  - `broadcast_port` (int) : Le numéro de port pour la diffusion de la requête de découverte.
- **Retourne** : Liste des réponses des serveurs.
- **Comportement** :
  - Diffuse un message de découverte (`DISCOVER_SERVER`).
  - Attend des réponses des serveurs.
  - Affiche et collecte les réponses.
  - Gère le timeout si aucun serveur ne répond.

#### `discover_servers_from_file(broadcast_port, filename)`

Découvre les serveurs hébergeant un fichier spécifique sur le réseau local.

- **Paramètres** :
  - `broadcast_port` (int) : Le numéro de port pour la diffusion de la requête.
  - `filename` (str) : Le fichier à rechercher sur les serveurs.
- **Retourne** : Liste des réponses des serveurs.
- **Comportement** :
  - Diffuse un message de découverte `FILE_DISCOVER_SERVER` et le nom du fichier.
  - Attend des réponses et les collecte.
  - Gère le timeout si aucun serveur ne répond.

#### `broadcast()`

Lance la découverte des serveurs et permet à l'utilisateur de se connecter à un serveur découvert.

- **Retourne** : Le socket connecté ou `0` si aucun serveur n'est trouvé.
- **Comportement** :
  - Appelle `discover_servers`.
  - Affiche la liste des serveurs découverts.
  - Invite l'utilisateur à sélectionner un serveur auquel se connecter.
  - Prévient l'utilisateur si aucun serveur n'a répondu.

#### `find_server_from_file()`

Lance une recherche de serveurs hébergeant un fichier spécifique et permet à l'utilisateur de se connecter à l'un d'eux.

- **Retourne** : Le socket connecté ou `0` si aucun serveur n'est trouvé.
- **Comportement** :
  - Invite l'utilisateur à entrer un nom de fichier.
  - Appelle `discover_servers_from_file`.
  - Affiche la liste des serveurs hébergeant le fichier.
  - Invite l'utilisateur à sélectionner un serveur auquel se connecter.
  - Prévient l'utilisateur si aucun serveur n'a répondu.

#### `main()`

Point d'entrée du programme. Gère l'interaction avec l'utilisateur.

- **Comportement** :
  - Invite l'utilisateur à choisir une méthode de découverte des serveurs :
    1. Découverte générale (`broadcast`).
    2. Découverte spécifique à un fichier (`find_server_from_file`).
  - Établit une connexion au serveur sélectionné.
  - Entre dans une boucle pour traiter les commandes de l'utilisateur.
  - Quitte le programme proprement en cas d'interruption clavier.

---

#### Gestion des commandes

Le dictionnaire suivant mappe les commandes à leurs fonctions :

```python
command_map = {
    'help' : handle_help,
    'cd' : handle_cd,
    'list' : handle_list,
    'mkdir' : handle_mkdir,
    'pwd' : handle_pwd,
    'download' : handle_download,
    'upload' : handle_upload,
    'lcd' : handle_lcd,
    'llist' : handle_llist,
    'lmkdir' : handle_lmkdir,
    'lpwd' : handle_lpwd
}
```

**Commandes disponibles :**

| Commande    | Description |
|-------------|-------------|
| `help`      | Affiche la liste des commandes disponibles ou des détails sur une commande spécifique. |
| `list`      | Liste les fichiers dans le répertoire courant du serveur. |
| `llist`     | Liste les fichiers dans le répertoire courant du client. |
| `pwd`       | Affiche le répertoire courant du serveur. |
| `lpwd`      | Affiche le répertoire courant du client. |
| `cd`        | Accède à un répertoire donné sur le serveur. |
| `lcd`       | Accède à un répertoire donné sur le client. |
| `mkdir`     | Crée un répertoire sur le serveur. |
| `lmkdir`    | Crée un répertoire sur le client. |
| `download`  | Télécharge un fichier/répertoire depuis le serveur vers le client. |
| `upload`    | Transfère un fichier/répertoire depuis le client vers le serveur. |

---


### Fonctionnement

1. **Saisie utilisateur** :

   - L'utilisateur choisit une méthode de découverte (générale ou spécifique à un fichier).
   - Saisit des commandes après une connexion réussie.

2. **Découverte des serveurs** :

   - Diffuse des messages de découverte via UDP.
   - Affiche les serveurs disponibles et permet une sélection par l'utilisateur.

3. **Communication par socket** :

   - Établit une connexion TCP au serveur sélectionné.
   - Envoie des commandes et traite les réponses.

4. **Gestion des commandes** :

   - Les commandes sont traitées dynamiquement via `cmd_h.command_map`.

5. **Gestion des erreurs** :

   - Gère les erreurs de création et de connexion de socket.
   - Traite les erreurs de saisie des commandes et les commandes inconnues.

---

### Utilisation

#### Exécution du script

Exécutez le script en utilisant Python :

```bash
python script_name.py
```

#### Exemples de commandes

- Découvrir des serveurs :
  ```
  1
  ```
- Rechercher un fichier :
  ```
  2
  Entrez le nom du fichier>example.txt
  ```
- Exécuter une commande :
  ```
  help
  ```

---

### Dépendances

- Python 3.x

---

## [Code Serveur (C)]

### Fonctionnalités

1. **Configuration du serveur** :
   - Création de sockets TCP et UDP pour gérer les connexions client et les diffusions réseau.
   - Initialisation des structures du serveur et des événements.

2. **Découverte et réponse aux clients** :
   - Réception des requêtes UDP pour découvrir le serveur (`DISCOVER_SERVER`) ou localiser un fichier spécifique.
   - Envoi des réponses aux clients pour indiquer l'état ou la disponibilité.

3. **Gestion des connexions client** :
   - Acceptation de nouvelles connexions client via TCP.
   - Gestion des sessions client (répertoires de travail, sockets actifs).

4. **Manipulation de fichiers et répertoires** :
   - Téléchargement et envoi de fichiers et répertoires.
   - Création et gestion des répertoires côté serveur.

5. **Événements réseau** :
   - Traitement des événements asynchrones pour les connexions et les diffusions.

---

### Fonctions Principales

#### Initialisation du serveur

- **`setup_storage_dir`** : Vérifie et initialise le répertoire de stockage du serveur.
- **`init`** : Configure les sockets, les adresses, et initialise les événements nécessaires.
- **`start_event_loop`** : Démarre la boucle principale pour gérer les événements TCP/UDP.

#### Découverte des serveurs

- **`on_udp_broadcast`** : Répond aux diffusions UDP pour indiquer la disponibilité du serveur ou des fichiers.

#### Gestion des clients

- **`on_accept`** : Accepte une nouvelle connexion client et initialise sa session.
- **`on_client_data`** : Traite les commandes envoyées par les clients (`upload`, `download`, `cd`, etc.).

#### Manipulation de fichiers

- **`write_file`** : Reçoit un fichier d'un client et l'écrit sur le serveur.
- **`write_directory`** : Reçoit un répertoire et son contenu récursivement.
- **`send_file_to_client`** : Envoie un fichier au client.
- **`send_directory`** : Envoie un répertoire (et ses sous-éléments) au client.

#### Commandes utilisateur

- **`change_directory`** : Change le répertoire courant de la session client.
- **`print_working_dir`** : Affiche le répertoire courant du client.
- **`on_client_data`** : Parse et exécute les commandes `upload`, `download`, `cd`, `list`, etc.

---
### Utilisation

#### Exécution du script

Exécutez le script depuis le répertoire `bin` :

```bash
sudo ./server <port> <interface>
```

---

### Fonctionnement

1. **Démarrage** :
   - Initialisation des sockets TCP et UDP, configuration des événements.
   - Vérification et création du répertoire de stockage si nécessaire.

2. **Événements réseau** :
   - Diffusion UDP pour découvrir le serveur ou des fichiers.
   - Connexion des clients via TCP pour des opérations spécifiques.

3. **Interaction client** :
   - Réception des commandes (upload, download, cd, pwd).
   - Exécution des opérations demandées (écriture de fichiers, envoi de répertoires, etc.).

---

### Dépendances

- `libevent` : Gestion des événements réseau.
- Systèmes Unix (pour les sockets et la manipulation de fichiers).

