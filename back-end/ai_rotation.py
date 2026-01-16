def rotation_score(last_crop, new_crop, soil):
    score = 50

    if last_crop:
        if last_crop["crop_family"] == new_crop["crop_family"]:
            score -= 30
        else:
            score += 30

    if soil.get("nitrogen", 0.5) < 0.5 and new_crop["nitrogen_effect"] == "HIGH":
        score += 20

    return max(0, min(100, score))

