# 🧪 Tests de Cohérence - Détecteur d'Incohérences pour Estimation de Taille

Documentation complète de tous les tests de cohérence implémentés dans le script.

---

## 📊 Vue d'Ensemble

Le script implémente **9 catégories de tests de cohérence** pour valider les données anthropométriques.

| # | Catégorie | Type |
|---|-----------|------|
| 1 | Champs obligatoires | Structurelle |
| 2 | Plages de valeurs | Validation de base |
| 3 | Taille-Âge-Sexe | Normes anthropométriques |
| 4 | IMC | Cohérence poids-taille |
| 5 | Ratios corporels | Proportions anatomiques |
| 6 | Poids-Taille-Âge adultes | Multi-variables |
| 7 | Poids enfants | Spécifique enfants |
| 8 | Tour taille vs Envergure | Validation croisée |
| 9 | Jambe vs Envergure | Validation croisée |

---

## Test 1️⃣ : Validation des Champs Obligatoires

### Description
Vérifie la présence des champs essentiels pour effectuer les validations.

### Champs Requis
- `age` (int)
- `sexe` (str)
- `taille` (float)
- `poids` (float)



### Exemple
```python
donnees = {'age': 25}  # Manque: sexe, taille, poids
# Résultat: 3 erreurs
```

---

## Test 2️⃣ : Validation des Valeurs de Base

### 2.1 - Âge

**Plage valide** : 0 à 120 ans

```python
if age < 0 or age > 120:
    ERREUR
```

**Exemples d'erreurs** :
- Âge = -5 ans ❌
- Âge = 150 ans ❌

---

### 2.2 - Sexe

**Valeurs acceptées** : `'homme'` ou `'femme'` (insensible à la casse)

```python
if sexe not in ['homme', 'femme']:
    ERREUR
```

**Exemples d'erreurs** :
- Sexe = 'masculin' ❌
- Sexe = 'M' ❌

---

### 2.3 - Taille

**Plage valide** : 0 à 300 cm

```python
if taille <= 0 or taille > 300:
    ERREUR
```

**Exemples d'erreurs** :
- Taille = -10 cm ❌
- Taille = 350 cm ❌

---

### 2.4 - Poids

**Plage valide** : 0 à 500 kg

```python
if poids < 0 or poids > 500:
    ERREUR
```

**Exemples d'erreurs** :
- Poids = 0 kg ❌
- Poids = 600 kg ❌

---

## Test 3️⃣ : Cohérence Taille-Âge-Sexe

### Description
Compare la taille saisie avec les normes anthropométriques selon l'âge et le sexe.

### Normes Anthropométriques

#### Homme

| Tranche d'Âge | Taille Min | Taille Max |
|---------------|------------|------------|
| 0-2 ans | 50 cm | 90 cm |
| 2-5 ans | 85 cm | 115 cm |
| 5-10 ans | 105 cm | 145 cm |
| 10-15 ans | 130 cm | 180 cm |
| 15-20 ans | 155 cm | 200 cm |
| 20+ ans | 150 cm | 210 cm |

#### Femme

| Tranche d'Âge | Taille Min | Taille Max |
|---------------|------------|------------|
| 0-2 ans | 48 cm | 88 cm |
| 2-5 ans | 83 cm | 112 cm |
| 5-10 ans | 103 cm | 142 cm |
| 10-15 ans | 130 cm | 175 cm |
| 15-20 ans | 150 cm | 185 cm |
| 20+ ans | 145 cm | 195 cm |

### Critère d'Erreur
```python
if taille < min_taille or taille > max_taille:
    ERREUR
```

### Exemples
✅ Homme 25 ans, 178 cm → OK  
❌ Femme 8 ans, 180 cm → ERREUR (max: 142 cm)  
❌ Homme 30 ans, 230 cm → ERREUR (max: 210 cm)

---

## Test 4️⃣ : Validation IMC (Indice de Masse Corporelle)

### Description
Calcule l'IMC et détecte les valeurs extrêmes ou inhabituelles.

### Formule
```python
IMC = poids / ((taille / 100) ** 2)
```

### 4.1 - IMC Extrême (Erreur)

**Critère** :
```python
if imc < 10 or imc > 50:
    ERREUR
```

**Exemples** :
- IMC = 8.5 ❌
- IMC = 55 ❌

---

### 4.2 - IMC Inhabituel (Avertissement)

**Critère** :
```python
if imc < 13 or imc > 40:
    AVERTISSEMENT
```

**Exemples** :
- IMC = 12 ⚠️
- IMC = 42 ⚠️

### Plages de Référence

| IMC | Catégorie |
|-----|-----------|
| < 13 | Dénutrition sévère |
| 13-18.5 | Dénutrition |
| 18.5-25 | Normal |
| 25-30 | Surpoids |
| 30-40 | Obésité |
| > 40 | Obésité morbide |

---

## Test 5️⃣ : Validation des Ratios Corporels

### Description
Vérifie que les proportions anatomiques respectent les normes physiologiques.

### 5.1 - Ratio Tour de Taille / Taille

**Plage normale** : 0.35 à 0.55

```python
ratio = tour_taille / taille
if ratio < 0.35 or ratio > 0.55:
    ERREUR
```

**Exemples** :
- Taille 180 cm, Tour 100 cm → Ratio = 0.56 ❌
- Taille 170 cm, Tour 75 cm → Ratio = 0.44 ✅

---

### 5.2 - Ratio Envergure / Taille

**Plage normale** : 0.98 à 1.06

```python
ratio = envergure / taille

# Erreur si très en dehors de la norme
if ratio < 0.88 or ratio > 1.16:
    ERREUR

# Avertissement si légèrement atypique
elif ratio < 0.98 or ratio > 1.06:
    AVERTISSEMENT
```

**Exemples** :
- Taille 175 cm, Envergure 176 cm → Ratio = 1.01 ✅
- Taille 180 cm, Envergure 150 cm → Ratio = 0.83 ❌
- Taille 170 cm, Envergure 175 cm → Ratio = 1.03 ✅

---

### 5.3 - Ratio Longueur Jambe / Taille

**Plage normale** : 0.45 à 0.53

```python
ratio = longueur_jambe / taille
if ratio < 0.45 or ratio > 0.53:
    ERREUR
```

**Exemples** :
- Taille 180 cm, Jambe 90 cm → Ratio = 0.50 ✅
- Taille 170 cm, Jambe 100 cm → Ratio = 0.59 ❌

---

## Test 6️⃣ : Cohérence Poids-Taille-Âge (Adultes)

### Description
Pour les adultes (≥18 ans), vérifie que le poids est cohérent avec la taille.

### Méthode
1. Calcule le poids min/max selon IMC sain (16-35)
2. Applique une tolérance de ±20%

```python
if age >= 18:
    poids_min = 16 * ((taille / 100) ** 2)
    poids_max = 35 * ((taille / 100) ** 2)
    
    if poids < poids_min * 0.8 or poids > poids_max * 1.2:
        ERREUR
```

### Exemples
- Adulte 180 cm, 52 kg → Poids min attendu ≈ 52 kg ✅
- Adulte 180 cm, 30 kg → Trop léger ❌
- Adulte 170 cm, 120 kg → Trop lourd ❌

---

## Test 7️⃣ : Cohérence Poids pour Enfants

### Description
Pour les enfants (<18 ans), estime un poids approximatif et détecte les écarts importants.

### Formules d'Estimation

```python
if age < 2:
    poids_attendu = age * 3 + 7
elif age < 12:
    poids_attendu = age * 2 + 8
else:  # 12-17 ans
    poids_attendu = 19 * ((taille / 100) ** 2)
```

### Critère d'Avertissement
```python
diff_poids = abs(poids - poids_attendu) / poids_attendu
if diff_poids > 0.5:  # Plus de 50% de différence
    AVERTISSEMENT
```

### Exemples

| Âge | Taille | Poids Saisi | Poids Attendu | Écart | Résultat |
|-----|--------|-------------|---------------|-------|----------|
| 5 ans | 110 cm | 18 kg | 18 kg | 0% | ✅ |
| 8 ans | 130 cm | 50 kg | 24 kg | +108% | ⚠️ |
| 15 ans | 165 cm | 40 kg | 52 kg | -23% | ✅ |

---

## Test 8️⃣ : Validation Croisée - Tour de Taille vs Envergure

### Description
Détecte les contradictions anatomiques impossibles.

### Règle Physiologique
Le tour de taille ne peut jamais être supérieur à l'envergure.

```python
if tour_taille > envergure:
    ERREUR
```

### Exemples
❌ Tour de taille = 200 cm, Envergure = 180 cm  
❌ Tour de taille = 120 cm, Envergure = 100 cm  
✅ Tour de taille = 85 cm, Envergure = 178 cm

---

## Test 9️⃣ : Validation Croisée - Longueur Jambe vs Envergure

### Description
Vérifie que les jambes ne sont pas plus longues que l'envergure.

### Règle Physiologique
Les jambes (du bassin au sol) ne peuvent pas dépasser l'envergure (bras étendus).

```python
if longueur_jambe > envergure:
    ERREUR
```

### Exemples
❌ Jambe = 180 cm, Envergure = 170 cm  
❌ Jambe = 95 cm, Envergure = 90 cm  
✅ Jambe = 90 cm, Envergure = 180 cm

---

## 📝 Notes Importantes

1. **Ordre d'exécution** : Les tests sont exécutés séquentiellement. Si les champs obligatoires sont manquants, les tests suivants ne sont pas effectués.

2. **Mesures optionnelles** : Les tests 5, 8 et 9 ne sont exécutés que si les mesures correspondantes sont fournies.

3. **Sensibilité à la casse** : Le sexe est converti en minuscules pour la comparaison.




---
