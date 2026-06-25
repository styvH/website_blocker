# 🛡️ Website Blocker

**Website Blocker** est une application de bureau Windows, simple et légère, qui permet de
**bloquer ou débloquer l'accès à des sites web** en quelques clics. Idéale pour limiter les
distractions, mettre en place un contrôle parental basique ou se concentrer pendant le travail.

L'interface est entièrement en français, au design sombre (thème *Dracula*), sans bordure
système et sans dépendance à un service en ligne : **tout fonctionne 100 % en local**.

![Plateforme](https://img.shields.io/badge/Windows-10%20%7C%2011-blue)
![Python](https://img.shields.io/badge/Python-3.12-yellow)
![Interface](https://img.shields.io/badge/UI-PyQt5-green)
![Version](https://img.shields.io/badge/version-1.1.0-orange)

---

## ✨ Fonctionnalités

- ➕ **Ajouter un blocage** : saisissez un domaine (`exemple.com`) ; le site et sa variante
  `www.` sont bloqués automatiquement.
- ➖ **Débloquer un site** : sélectionnez-le dans la liste (ou double-cliquez dessus).
- 📋 **Liste claire** des sites actuellement bloqués, avec compteur en temps réel.
- 🔁 **Prise d'effet immédiate** : le cache DNS de Windows est vidé après chaque modification.
- 🧹 **Saisie tolérante** : colle d'une URL complète (`https://site.com/page`) acceptée, le
  domaine est extrait automatiquement.
- 💾 **Sauvegarde automatique** du fichier `hosts` avant toute modification.
- 🎨 **Interface moderne** : fenêtre sans bordure, déplaçable, boutons réduire/agrandir/fermer.

---

## ⚙️ Comment ça marche

L'application modifie le fichier **`hosts`** de Windows :

```
C:\Windows\System32\drivers\etc\hosts
```

Bloquer un site revient à rediriger son nom de domaine vers l'adresse locale `127.0.0.1`,
ce qui rend le site inaccessible depuis le navigateur. Chaque ligne ajoutée par l'application
est balisée par un marqueur `# WebsiteBlocker` :

```
127.0.0.1 exemple.com # WebsiteBlocker
127.0.0.1 www.exemple.com # WebsiteBlocker
```

Ce marqueur garantit que l'application ne touche **jamais** aux entrées système ou créées
par d'autres logiciels. Modifier le fichier `hosts` nécessite les **droits administrateur** :
l'application demande donc automatiquement une élévation de privilèges au démarrage (UAC).

> ℹ️ Une sauvegarde `hosts.webblocker.bak` est créée à côté du fichier original avant
> chaque modification, au cas où vous voudriez revenir en arrière manuellement.

---

## 🚀 Installation

### Option 1 — Exécutable prêt à l'emploi (recommandé)

1. Téléchargez `WebsiteBlocker.exe` depuis la page **[Releases](../../releases)**.
2. Double-cliquez dessus. Windows demandera une autorisation administrateur (UAC) :
   c'est normal, l'application en a besoin pour modifier le fichier `hosts`.

> ⚠️ **Avertissement SmartScreen / antivirus** — voir la section
> [Sécurité & confiance](#-sécurité--confiance) ci-dessous.

### Option 2 — Lancer depuis les sources

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd website_blocker

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer (l'élévation administrateur est automatique)
python website_blocker.py
```

**Prérequis** : Windows 10/11 et Python 3.12+.

---

## 🔨 Compiler l'exécutable soi-même

Le projet se compile en un **unique fichier `.exe`** via [PyInstaller](https://pyinstaller.org/) :

```bash
pip install -r requirements.txt pyinstaller

pyinstaller --onefile --windowed --uac-admin ^
  --name WebsiteBlocker ^
  --icon app_icon.ico ^
  --version-file version_info.txt ^
  --add-data "app_icon.ico;." ^
  website_blocker.py
```

L'exécutable est généré dans le dossier `dist/`.

### Build automatique (GitHub Actions)

Le dépôt contient un workflow [`.github/workflows/build.yml`](.github/workflows/build.yml) qui :

- compile l'`.exe` à chaque tag `v*` **et** sur déclenchement manuel ;
- publie automatiquement une **Release GitHub** avec le binaire lorsqu'un tag est poussé.

Pour publier une nouvelle version :

```bash
git tag v1.1.0
git push origin v1.1.0
```

---

## 🔒 Sécurité & confiance

Cette application est **open source** : tout le code est lisible dans
[`website_blocker.py`](website_blocker.py). Elle ne contient aucune télémétrie, aucune
connexion réseau et n'écrit que dans le fichier `hosts` de Windows.

**Pourquoi Windows peut-il afficher un avertissement ?**
Un exécutable PyInstaller, non signé numériquement, qui demande les droits administrateur
et modifie un fichier système, déclenche souvent un avertissement SmartScreen ou un faux
positif antivirus. C'est attendu pour ce type d'outil.

**Ce qui est mis en place pour améliorer la confiance et l'acceptation au téléchargement :**

- 🪪 **Métadonnées de version embarquées** ([`version_info.txt`](version_info.txt)) : éditeur,
  description, version et copyright sont visibles dans les propriétés du fichier. Un binaire
  « identifié » est nettement mieux accepté qu'un binaire anonyme.
- 🧱 **Modifications minimales et balisées** : seules les lignes marquées `# WebsiteBlocker`
  sont gérées ; rien d'autre n'est touché dans `hosts`.
- 💾 **Sauvegarde automatique** avant chaque écriture.
- 🚫 **Aucune connexion réseau, aucune collecte de données.**
- 📖 **Code source intégralement public et compilable** par n'importe qui.

**Pour aller plus loin (recommandé en production) :** signer l'exécutable avec un
**certificat de signature de code** (Authenticode / EV) supprime l'avertissement SmartScreen.
C'est l'étape la plus efficace mais elle requiert l'achat d'un certificat auprès d'une
autorité de certification.

---

## 🗂️ Structure du projet

| Fichier | Rôle |
|---|---|
| `website_blocker.py` | Code de l'application (interface PyQt5 + logique de blocage). |
| `requirements.txt` | Dépendances Python. |
| `version_info.txt` | Métadonnées de version embarquées dans l'`.exe`. |
| `app_icon.ico` | Icône de l'application. |
| `.github/workflows/build.yml` | Compilation et publication automatiques. |

---

## ❓ FAQ

**Le blocage ne fonctionne pas tout de suite ?**
Le cache DNS est vidé automatiquement, mais certains navigateurs gardent leur propre cache.
Fermez et rouvrez l'onglet, ou redémarrez le navigateur.

**Comment tout débloquer manuellement ?**
Ouvrez `C:\Windows\System32\drivers\etc\hosts` en administrateur et supprimez les lignes
marquées `# WebsiteBlocker`, ou restaurez la sauvegarde `hosts.webblocker.bak`.

**Pourquoi certains domaines ne peuvent pas être bloqués ?**
Les domaines `.test` et `kubernetes.docker.internal` sont réservés à un usage système/local
et sont volontairement exclus.

---

## 📄 Licence

Projet développé par **MultiHServices**. Libre d'utilisation et de modification.
