/*
 @licstart  The following is the entire license notice for the JavaScript code in this file.

 The MIT License (MIT)

 Copyright (C) 1997-2020 by Dimitri van Heesch

 Permission is hereby granted, free of charge, to any person obtaining a copy of this software
 and associated documentation files (the "Software"), to deal in the Software without restriction,
 including without limitation the rights to use, copy, modify, merge, publish, distribute,
 sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies or
 substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
 BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

 @licend  The above is the entire license notice for the JavaScript code in this file
*/
var NAVTREE =
[
  [ "Fileserver", "index.html", [
    [ "Documentation technique", "md_doc_2doc.html", [
      [ "Sommaire", "md_doc_2doc.html#autotoc_md1", [
        [ "Code Client", "md_doc_2doc.html#autotoc_md2", null ],
        [ "Code Serveur", "md_doc_2doc.html#autotoc_md3", null ],
        [ "Protocole", "md_doc_2doc.html#autotoc_md4", null ]
      ] ],
      [ "Code Client (Python)", "md_doc_2doc.html#autotoc_md6", [
        [ "Fonctionnalités", "md_doc_2doc.html#autotoc_md7", [
          [ "Découverte des serveurs", "md_doc_2doc.html#autotoc_md8", null ],
          [ "Gestion des commandes", "md_doc_2doc.html#autotoc_md9", null ],
          [ "Communication par socket", "md_doc_2doc.html#autotoc_md10", null ],
          [ "Gestion des fichiers et répertoires", "md_doc_2doc.html#autotoc_md11", null ]
        ] ],
        [ "Fonctions", "md_doc_2doc.html#autotoc_md13", [
          [ "create_socket()", "md_doc_2doc.html#autotoc_md14", null ],
          [ "connect_socket(client_socket, host, port)", "md_doc_2doc.html#autotoc_md15", null ],
          [ "handle_command(client_socket, message)", "md_doc_2doc.html#autotoc_md16", null ],
          [ "discover_servers(broadcast_port)", "md_doc_2doc.html#autotoc_md17", null ],
          [ "discover_servers_from_file(broadcast_port, filename)", "md_doc_2doc.html#autotoc_md18", null ],
          [ "broadcast()", "md_doc_2doc.html#autotoc_md19", null ],
          [ "find_server_from_file()", "md_doc_2doc.html#autotoc_md20", null ],
          [ "main()", "md_doc_2doc.html#autotoc_md21", null ],
          [ "Gestion des commandes", "md_doc_2doc.html#autotoc_md23", null ]
        ] ],
        [ "Fonctionnement", "md_doc_2doc.html#autotoc_md25", null ],
        [ "Utilisation", "md_doc_2doc.html#autotoc_md27", [
          [ "Exécution du script", "md_doc_2doc.html#autotoc_md28", null ],
          [ "Exemples de commandes", "md_doc_2doc.html#autotoc_md29", null ]
        ] ],
        [ "Dépendances", "md_doc_2doc.html#autotoc_md31", null ]
      ] ],
      [ "Code Serveur (C)", "md_doc_2doc.html#autotoc_md33", [
        [ "Fonctionnalités", "md_doc_2doc.html#autotoc_md34", null ],
        [ "Fonctions Principales", "md_doc_2doc.html#autotoc_md36", [
          [ "Initialisation du serveur", "md_doc_2doc.html#autotoc_md37", null ],
          [ "Découverte des serveurs", "md_doc_2doc.html#autotoc_md38", null ],
          [ "Gestion des clients", "md_doc_2doc.html#autotoc_md39", null ],
          [ "Manipulation de fichiers", "md_doc_2doc.html#autotoc_md40", null ],
          [ "Commandes utilisateur", "md_doc_2doc.html#autotoc_md41", null ]
        ] ],
        [ "Utilisation", "md_doc_2doc.html#autotoc_md43", [
          [ "Exécution du script", "md_doc_2doc.html#autotoc_md44", null ]
        ] ],
        [ "Fonctionnement", "md_doc_2doc.html#autotoc_md46", null ],
        [ "Dépendances", "md_doc_2doc.html#autotoc_md48", null ]
      ] ],
      [ "Protocole", "md_doc_2doc.html#autotoc_md50", [
        [ "Connexion client/serveur", "md_doc_2doc.html#autotoc_md51", null ]
      ] ],
      [ "Le serveur accepte la requête du client.", "md_doc_2doc.html#autotoc_md52", [
        [ "Échange de données", "md_doc_2doc.html#autotoc_md53", null ]
      ] ],
      [ "Un maximum de 3 renvoie de données est possible par requête.", "md_doc_2doc.html#autotoc_md54", [
        [ "Requête pwd", "md_doc_2doc.html#autotoc_md55", null ]
      ] ],
      [ "Sinon il affiche ce qu'il a reçu du serveur.", "md_doc_2doc.html#autotoc_md56", [
        [ "Requête list", "md_doc_2doc.html#autotoc_md57", null ]
      ] ],
      [ "Sinon il affiche les fichiers et répertoires du répertoire courant, puis envoie ACK lorsqu'il lit END", "md_doc_2doc.html#autotoc_md58", [
        [ "Requête cd", "md_doc_2doc.html#autotoc_md59", null ]
      ] ],
      [ "Le serveur modifie le répertoire courant de la session client, puis envoie ACK si il a réussit,...", "md_doc_2doc.html#autotoc_md60", [
        [ "Requête mkdir", "md_doc_2doc.html#autotoc_md61", null ]
      ] ]
    ] ],
    [ "Fileserver", "md__r_e_a_d_m_e.html", null ],
    [ "Namespaces", "namespaces.html", [
      [ "Namespace List", "namespaces.html", "namespaces_dup" ],
      [ "Namespace Members", "namespacemembers.html", [
        [ "All", "namespacemembers.html", null ],
        [ "Functions", "namespacemembers_func.html", null ],
        [ "Variables", "namespacemembers_vars.html", null ]
      ] ]
    ] ],
    [ "Data Structures", "annotated.html", [
      [ "Data Structures", "annotated.html", "annotated_dup" ],
      [ "Data Structure Index", "classes.html", null ],
      [ "Data Fields", "functions.html", [
        [ "All", "functions.html", null ],
        [ "Variables", "functions_vars.html", null ]
      ] ]
    ] ],
    [ "Files", "files.html", [
      [ "File List", "files.html", "files_dup" ],
      [ "Globals", "globals.html", [
        [ "All", "globals.html", null ],
        [ "Functions", "globals_func.html", null ],
        [ "Variables", "globals_vars.html", null ],
        [ "Macros", "globals_defs.html", null ]
      ] ]
    ] ]
  ] ]
];

var NAVTREEINDEX =
[
"annotated.html"
];

var SYNCONMSG = 'click to disable panel synchronisation';
var SYNCOFFMSG = 'click to enable panel synchronisation';