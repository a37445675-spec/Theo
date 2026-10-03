from django.core.exceptions import ValidationError


def validate_attributes_against_set(attributes: dict, attribute_set, enforce_required=True):
    """
    Valide un dict d'attributs par rapport à un AttributeSet : rejette toute
    clé hors périmètre, valide chaque valeur selon le type de son
    AttributeDefinition, et vérifie les attributs obligatoires si demandé.
    """
    attributes = attributes or {}

    if attribute_set is None:
        if attributes:
            raise ValidationError(
                "Cette catégorie n'a pas d'ensemble d'attributs (AttributeSet) associé : "
                "aucun attribut dynamique n'est autorisé sur ses produits."
            )
        return

    definitions_by_code = {item.attribute.code: item.attribute for item in attribute_set.items.select_related("attribute")}
    allowed_codes = set(definitions_by_code.keys())
    provided_codes = set(attributes.keys())

    unknown_codes = provided_codes - allowed_codes
    if unknown_codes:
        raise ValidationError(
            f"Attribut(s) non autorisé(s) pour la catégorie (AttributeSet '{attribute_set.name}') : "
            f"{', '.join(sorted(unknown_codes))}. Attributs autorisés : {', '.join(sorted(allowed_codes)) or 'aucun'}."
        )

    if enforce_required:
        required_codes = {item.attribute.code for item in attribute_set.items.filter(is_required=True).select_related("attribute")}
        missing_codes = required_codes - provided_codes
        if missing_codes:
            raise ValidationError(f"Attribut(s) obligatoire(s) manquant(s) : {', '.join(sorted(missing_codes))}.")

    for code, value in attributes.items():
        definitions_by_code[code].validate_value(value)
