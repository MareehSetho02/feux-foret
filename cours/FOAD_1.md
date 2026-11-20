# Programme de travail pour le 17 novembre après-midi

Compte-tenu de l'état d'avancement de vos travaux, voici quelques pistes possibles.

## A terminer

Vous devriez pouvoir nous rendre ce soir ;

1. les **listes de questions** :
    - individuelles
    - synthèse collective

Certains d'entre vous se sont laissés piéger par le gabarit fourni par Marine ; vous n'êtes pas limités à 4 questions, naturellement ;o)

Sans une version finale de votre document : 
- privilégiez des questions « atomiques » (souvenez-vous de principes de simplicité, comme **KISS** — *Keep It Simple, Stupid* — ou le **Single Responsibility** de SOLID), que vous pourrez plus facilemnt lier à des données de ganularité fine ;
  - À partir des questions analytiques générales, distinguez les thématiques atomiques (ex: localisation des feux, météo et date des départs de feux).
- évitez les questions sur la gestion du projet, qui ne sont pas l'enjeu ici ;
- évitez de projeter des solutions au travers des questions (biais de confirmation)
- ne partez pas d'une solution technique issue de votre imagination, en essayant de faire entrer lo problème à l'intérieur de ce cadre ; d'une part le stade actuel n'est pas dépendant de la technique ; d'autre part vous raisonnez dans le mauvais sens.

2. le **glossaire**, à savoir la liste des termes rencontrés dans l"énoncé et la documentation, relatifs à la problématique du défi.

Si vous avez rencontré des définitions contradictoires dans les jeux de données explorés, vous devez établir un processus de sélection de votre **définition de référence**, qui fera foi par suite, et engendrera des modifications des données ne suivant pas cette défintion.

Après une première version du glossaire, où chaque entrée est liée à une définition, vous pouvez également ajouter d'autres annotations, comme :
- le registre (c'est un terme technique, juridique, un acronyme, une convention de langage, un nom propre, etc.)
- le contexte d'usage du terme
- les synonymes ou antonymes (p. ex. **SDIS** est un synonyme de *Service Départemental d'Incendie et de Secours* ; **`urgence`** est un antonyme de *tranquillité*, *patience*, ou *plus tard*)

3. Le **tableau croisé questions x sources**, dont le but est de caractériser les données dont vous aurez besoin pour répondre aux questions que vous avez répertoriées. 

L'intérêt de ce tableau est double: 
- premièrement, il vous permet de vérifier que tout question est au moins partiellement couverte par les sources sélectionnées ;
- deuxièmement, que toute source couvre au moins une des questions (principe de minimisation des données)

4. Les **fiches d'analyse des sources**, pour lesquelles vous avez un modèle (`Exercice 2 - Fiche d'identité des sources.pdf`)

N'oubliez pas, dans les fiches d"analyse des sources de décrire le schéma de données de celles-ci, afin de pouvoir par la suite identifier facilement les données qie vous souhaiteriez en exraire.

## Ce que vous pouvez préparer pour demain

### 1) Caractériser les données manquantes

En partant du document *`UE01.A — C2 pertinence d’une source et sources manquantes`*, complétez la description de vos données en indiquant quelles sont les données que vous ne pouvez pas utiliser, pour quelles raisons, et les conclusions que vous en tirez

### 2) Estimer la qualité des données

En partant du document *`UE01.A — C3 qualité et complétude des données`*, estimez la qualité des données. Vous pouvez en particulier étudier la norme **ISO/IEC 25012**,
Un certain nombre de mesures de qualité ne seront possibles qu'une fois la source cible constituée, mais il est possible d'abticiper certains points.

La norme, notamment, ne donne pas une mesure intrinsèque de la qualité, mais vous donne les moyens de définir vous-mêmes ce que vous estimez être le « bon » niveau de qualité.

### 3) Traquer les données personnelles

La question du RGPD sera abordée lors de la prochaine session, mais vous pouvez déjà regarder si, dans les sources que vous envisagre de retenir, des données sensibles ou personnelles sont préssentes. 
Les sources proposées par le défi étant déjà publiques, il y a peu de risques que cela se produise, mais vous pouvez très bien utiliser vos propres sources additionnelles qui seront peut-être moins rigoureuses.

### 4) Préparer le modèle cible

À partir du document *`UE01.A — C6 consolidation multi-sources`*, vous pouvez commencer à réfléchir à votre propre modèle de données local.
Pour cela, vous allez devoir sélectionner dans les sources les données qui vous intéressent, puis les aligner au modèle que vous aurez constitué.
Dans ce processus, il se peut que des conflits surgissent, c'est la partie la plus délicate.
