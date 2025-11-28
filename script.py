import math
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Résultat de validation avec détails des incohérences"""
    est_valide: bool
    erreurs: List[str]
    avertissements: List[str]
    score_coherence: float  # 0-100

class DetecteurIncoherenceTaille:
    """
    Détecte les incohérences dans les données pour l'estimation de taille.
    Basé sur des normes anthropométriques et relations physiologiques.
    """
    
    def __init__(self):
        # Plages normales de taille par âge et sexe (en cm)
        self.taille_normale = {
            'homme': {
                (0, 2): (50, 90),
                (2, 5): (85, 115),
                (5, 10): (105, 145),
                (10, 15): (130, 180),
                (15, 20): (155, 200),
                (20, 150): (150, 210)
            },
            'femme': {
                (0, 2): (48, 88),
                (2, 5): (83, 112),
                (5, 10): (103, 142),
                (10, 15): (130, 175),
                (15, 20): (150, 185),
                (20, 150): (145, 195)
            }
        }
        
        # Ratios normaux entre mesures corporelles
        self.ratios_normaux = {
            'tour_taille_taille': (0.35, 0.55),  # Tour de taille / Taille
            'envergure_taille': (0.98, 1.06),     # Envergure / Taille
            'longueur_jambe_taille': (0.45, 0.53) # Longueur jambe / Taille
        }
    
    def valider_donnees(self, donnees: Dict) -> ValidationResult:
        """
        Valide la cohérence de toutes les données saisies.
        
        Args:
            donnees: Dictionnaire contenant {
                'age': int,
                'sexe': str ('homme' ou 'femme'),
                'taille': float (en cm),
                'poids': float (en kg),
                'tour_taille': float (en cm, optionnel),
                'envergure': float (en cm, optionnel),
                'longueur_jambe': float (en cm, optionnel),
                'taille_mere': float (en cm, optionnel),
                'taille_pere': float (en cm, optionnel)
            }
        
        Returns:
            ValidationResult avec erreurs et avertissements
        """
        erreurs = []
        avertissements = []
        score = 100.0
        
        # Validation des champs obligatoires
        champs_requis = ['age', 'sexe', 'taille', 'poids']
        for champ in champs_requis:
            if champ not in donnees or donnees[champ] is None:
                erreurs.append(f"❌ Champ obligatoire manquant: {champ}")
                score -= 25
        
        if erreurs:
            return ValidationResult(False, erreurs, avertissements, max(0, score))
        
        # Extraction des données
        age = donnees['age']
        sexe = donnees['sexe'].lower()
        taille = donnees['taille']
        poids = donnees['poids']
        
        # 1. Validation des valeurs de base
        if age < 0 or age > 120:
            erreurs.append(f"❌ Âge invalide: {age} ans (doit être entre 0 et 120)")
            score -= 20
        
        if sexe not in ['homme', 'femme']:
            erreurs.append(f"❌ Sexe invalide: {sexe} (doit être 'homme' ou 'femme')")
            score -= 20
        
        if taille <= 0 or taille > 300:
            erreurs.append(f"❌ Taille invalide: {taille} cm (doit être entre 0 et 300)")
            score -= 20
        
        if poids <= 0 or poids > 500:
            erreurs.append(f"❌ Poids invalide: {poids} kg (doit être entre 0 et 500)")
            score -= 20
        
        if erreurs:
            return ValidationResult(False, erreurs, avertissements, max(0, score))
        
        # 2. Validation de la cohérence taille-âge-sexe
        plage_taille = self._obtenir_plage_taille(age, sexe)
        if plage_taille:
            min_taille, max_taille = plage_taille
            if taille < min_taille or taille > max_taille:
                erreurs.append(
                    f"❌ Taille incohérente pour {sexe} de {age} ans: {taille} cm "
                    f"(plage normale: {min_taille}-{max_taille} cm)"
                )
                score -= 15
        
        # 3. Validation IMC (Indice de Masse Corporelle)
        imc = poids / ((taille / 100) ** 2)
        if imc < 10 or imc > 50:
            erreurs.append(
                f"❌ IMC extrême: {imc:.1f} (poids {poids} kg / taille {taille} cm). "
                f"Valeurs normales: 18.5-30"
            )
            score -= 15
        elif imc < 13 or imc > 40:
            avertissements.append(
                f"⚠️ IMC inhabituel: {imc:.1f}. Vérifiez poids et taille."
            )
            score -= 5
        
        # 4. Validation des ratios corporels
        if 'tour_taille' in donnees and donnees['tour_taille']:
            ratio_tt = donnees['tour_taille'] / taille
            min_r, max_r = self.ratios_normaux['tour_taille_taille']
            if ratio_tt < min_r or ratio_tt > max_r:
                erreurs.append(
                    f"❌ Ratio tour de taille/taille incohérent: {ratio_tt:.2f} "
                    f"(normal: {min_r:.2f}-{max_r:.2f})"
                )
                score -= 10
        
        if 'envergure' in donnees and donnees['envergure']:
            ratio_env = donnees['envergure'] / taille
            min_r, max_r = self.ratios_normaux['envergure_taille']
            if ratio_env < min_r - 0.1 or ratio_env > max_r + 0.1:
                erreurs.append(
                    f"❌ Ratio envergure/taille incohérent: {ratio_env:.2f} "
                    f"(normal: {min_r:.2f}-{max_r:.2f})"
                )
                score -= 10
            elif ratio_env < min_r or ratio_env > max_r:
                avertissements.append(
                    f"⚠️ Envergure légèrement atypique: {donnees['envergure']} cm "
                    f"pour taille {taille} cm"
                )
                score -= 3
        
        if 'longueur_jambe' in donnees and donnees['longueur_jambe']:
            ratio_jambe = donnees['longueur_jambe'] / taille
            min_r, max_r = self.ratios_normaux['longueur_jambe_taille']
            if ratio_jambe < min_r or ratio_jambe > max_r:
                erreurs.append(
                    f"❌ Ratio longueur jambe/taille incohérent: {ratio_jambe:.2f} "
                    f"(normal: {min_r:.2f}-{max_r:.2f})"
                )
                score -= 10
        
        # 5. Validation de la cohérence poids-taille-âge (relation multi-variables)
        if age >= 18:  # Adultes
            # Vérifier que le poids est cohérent avec la taille pour un adulte
            imc_min_sain, imc_max_sain = 16, 35
            poids_min = imc_min_sain * ((taille / 100) ** 2)
            poids_max = imc_max_sain * ((taille / 100) ** 2)
            
            if poids < poids_min * 0.8 or poids > poids_max * 1.2:
                erreurs.append(
                    f"❌ Combinaison poids/taille/âge incohérente: "
                    f"Pour un adulte de {taille} cm, poids de {poids} kg est extrême "
                    f"(plage attendue: {poids_min:.0f}-{poids_max:.0f} kg)"
                )
                score -= 10
        
        # 6. Cohérence poids-taille pour enfants
        if age < 18:
            poids_attendu = self._estimer_poids_enfant(age, taille, sexe)
            if poids_attendu:
                diff_poids = abs(poids - poids_attendu) / poids_attendu
                if diff_poids > 0.5:  # Plus de 50% de différence
                    avertissements.append(
                        f"⚠️ Poids inhabituel pour l'âge et la taille: {poids} kg "
                        f"(attendu environ {poids_attendu:.0f} kg)"
                    )
                    score -= 5
        
        # 7. Validation des mesures corporelles multiples (cohérence croisée)
        if 'tour_taille' in donnees and donnees['tour_taille'] and 'envergure' in donnees and donnees['envergure']:
            # Le tour de taille ne devrait pas être supérieur à l'envergure
            if donnees['tour_taille'] > donnees['envergure']:
                erreurs.append(
                    f"❌ Incohérence: tour de taille ({donnees['tour_taille']} cm) "
                    f"supérieur à l'envergure ({donnees['envergure']} cm)"
                )
                score -= 10
        
        # 8. Validation longueur jambe vs envergure
        if 'longueur_jambe' in donnees and donnees['longueur_jambe'] and 'envergure' in donnees and donnees['envergure']:
            # Les jambes ne peuvent pas être plus longues que l'envergure
            if donnees['longueur_jambe'] > donnees['envergure']:
                erreurs.append(
                    f"❌ Incohérence: longueur jambe ({donnees['longueur_jambe']} cm) "
                    f"supérieure à l'envergure ({donnees['envergure']} cm)"
                )
                score -= 10
        
        est_valide = len(erreurs) == 0
        score = max(0, min(100, score))
        
        return ValidationResult(est_valide, erreurs, avertissements, score)
    
    def _obtenir_plage_taille(self, age: int, sexe: str) -> Tuple[float, float]:
        """Obtient la plage normale de taille pour un âge et sexe donnés"""
        if sexe not in self.taille_normale:
            return None
        
        for (age_min, age_max), (taille_min, taille_max) in self.taille_normale[sexe].items():
            if age_min <= age < age_max:
                return (taille_min, taille_max)
        return None
    

    def _estimer_poids_enfant(self, age: int, taille: float, sexe: str) -> float:
        """Estime un poids approximatif pour un enfant"""
        if age < 2:
            # Formule approximative pour bébés/très jeunes enfants
            return age * 3 + 7
        elif age < 12:
            # Formule approximative pour enfants
            return age * 2 + 8
        else:
            # Pour adolescents, utiliser IMC normal (19)
            return 19 * ((taille / 100) ** 2)


def exemple_utilisation():
    """Exemples d'utilisation du détecteur"""
    
    detecteur = DetecteurIncoherenceTaille()
    
    print("=" * 70)
    print("DÉTECTEUR D'INCOHÉRENCES POUR ESTIMATION DE TAILLE")
    print("=" * 70)
    
    # Exemple 1: Données cohérentes
    print("\n📋 Exemple 1: Données cohérentes")
    print("-" * 70)
    donnees1 = {
        'age': 25,
        'sexe': 'homme',
        'taille': 178,
        'poids': 75,
        'envergure': 180,
        'tour_taille': 85
    }
    print(f"Données: {donnees1}")
    resultat1 = detecteur.valider_donnees(donnees1)
    afficher_resultat(resultat1)
    
    # Exemple 2: Taille incohérente avec l'âge
    print("\n📋 Exemple 2: Taille incohérente avec l'âge")
    print("-" * 70)
    donnees2 = {
        'age': 8,
        'sexe': 'femme',
        'taille': 180,  # Trop grande pour 8 ans
        'poids': 30
    }
    print(f"Données: {donnees2}")
    resultat2 = detecteur.valider_donnees(donnees2)
    afficher_resultat(resultat2)
    
    # Exemple 3: IMC incohérent
    print("\n📋 Exemple 3: Poids incohérent avec la taille")
    print("-" * 70)
    donnees3 = {
        'age': 30,
        'sexe': 'homme',
        'taille': 180,
        'poids': 50  # Poids trop faible
    }
    print(f"Données: {donnees3}")
    resultat3 = detecteur.valider_donnees(donnees3)
    afficher_resultat(resultat3)
    
    # Exemple 4: Ratios corporels incohérents
    print("\n📋 Exemple 4: Ratios corporels incohérents")
    print("-" * 70)
    donnees4 = {
        'age': 35,
        'sexe': 'femme',
        'taille': 165,
        'poids': 60,
        'envergure': 140,  # Trop courte
        'longueur_jambe': 100  # Trop longue
    }
    print(f"Données: {donnees4}")
    resultat4 = detecteur.valider_donnees(donnees4)
    afficher_resultat(resultat4)
    
    # Exemple 5: Mesures corporelles contradictoires
    print("\n📋 Exemple 5: Mesures corporelles contradictoires")
    print("-" * 70)
    donnees5 = {
        'age': 28,
        'sexe': 'homme',
        'taille': 175,
        'poids': 70,
        'tour_taille': 200,  # Tour de taille impossible
        'envergure': 178,
        'longueur_jambe': 180  # Plus longue que l'envergure!
    }
    print(f"Données: {donnees5}")
    resultat5 = detecteur.valider_donnees(donnees5)
    afficher_resultat(resultat5)


def afficher_resultat(resultat: ValidationResult):
    """Affiche le résultat de validation de manière formatée"""
    print(f"\n{'✅ DONNÉES VALIDES' if resultat.est_valide else '❌ DONNÉES INVALIDES'}")
    print(f"Score de cohérence: {resultat.score_coherence:.1f}/100")
    
    if resultat.erreurs:
        print(f"\n🚫 Erreurs ({len(resultat.erreurs)}):")
        for erreur in resultat.erreurs:
            print(f"  {erreur}")
    
    if resultat.avertissements:
        print(f"\n⚠️  Avertissements ({len(resultat.avertissements)}):")
        for avert in resultat.avertissements:
            print(f"  {avert}")
    
    if not resultat.erreurs and not resultat.avertissements:
        print("\n✨ Toutes les données sont cohérentes!")


if __name__ == "__main__":
    exemple_utilisation()