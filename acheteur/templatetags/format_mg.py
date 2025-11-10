from django import template

register = template.Library()

@register.filter
def separateur_mg(value):
    """
    Formatage des nombres avec espace comme séparateur de milliers
    Exemple : 1500000 → 1 500 000
    """
    try:
        # Si c’est un nombre, on le convertit correctement
        valeur = float(value)
        # Format avec séparateur d’espace insécable
        return f"{valeur:,.0f}".replace(",", " ")
    except (ValueError, TypeError):
        return value
