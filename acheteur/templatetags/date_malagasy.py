from django import template

register = template.Library()

@register.filter
def date_malagasy(value):
    mois_fr = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"
    ]
    mois_mg = [
        "Janoary", "Febroary", "Martsa", "Aprily", "May", "Jona",
        "Jolay", "Aogositra", "Septambra", "Oktobra", "Novambra", "Desambra"
    ]

    if not value:
        return ""

    jour = value.day
    mois = mois_mg[value.month - 1]
    annee = value.year
    heure = value.strftime("%H:%M")

    return f"{jour} {mois} {annee} "
